###########################################################
#
# Base for all physical objects that exist in the game space
#
###########################################################
import random
from collections import namedtuple
import field_of_view
from user_interface import interfaces as ui 
from user_interface import keyboard
from . import actions
from settings import COMMON_TRAITS, Obj
import pathfinding as pf


###################
#
# Entity attributes
#
###################

class Location:
    def __init__(self, coords=(-1,-1)):
        self._x = coords[0]
        self._y = coords[1]

    def __call__(self):
        return (self._x, self._y)

    def update(self, coords):
        self._x = coords[0]
        self._y = coords[1]

    def proposed(self, direction):
        return (self._x + direction[0], self._y + direction[1])
    
    def move(self, coords):
            self.update(self.proposed(coords))


class Inventory:
    def __init__(self, parent, max):
        self.parent = parent
        self.max = max
        self.items = []

    def add(self, target):
        target.loc = self.parent.loc
        self.items.insert(0, target)
        ui.narrative.add('{} picks up a {}.'.format(self.parent.name, target.name))

    def remove(self, target):
        target.loc = Location(target.loc())
        self.items.remove(target)


class Perception:
    def __init__(self, parent, max_vision):
        self.parent = parent
        self.max_vision = max_vision
        self.fov = []
 
    def look(self, terrain):
        if not self.fov or self.fov[0] != self.parent.loc():
            # Entity has moved since last calculating field-of-view
            self.fov = field_of_view.scan(self.parent.loc(), terrain.sightmap, self.max_vision)
        return self.fov


class Life:
    p_max = 10
    p_min = -10
    def __init__(self, parent, health_max, personality=0):
        self.parent = parent
        self.health_max = health_max
        self.health_current = health_max
        # Personality is a 'spectrum' expressed as int
        # +10: extremist anti-android and pro-life
        # -10: extremist pro-android and anti-life
        self.personality = min(self.p_max, max(self.p_min, personality))

    def __call__(self):
        return self.health_current > 0

    def demeanor(self, target):
        return  target.life.personality - self.personality

    def damage(self, num):
        self.health_current = self.health_current - num
        if self.health_current <= 0:
            self.die()

    def die(self):
        ui.narrative.add('{} dies'.format(self.parent))
        for attr in Obj._fields:
            setattr(self.parent, attr, getattr(COMMON_TRAITS['consumable'], attr))
        self.parent.del_ability('initiative')

class Initiative:
    def __init__(self, parent, modifier=0):
        self.modifier = modifier
    
    def __call__(self):
        return random.randint(0,20) + self.modifier
        

class Combat:
    def __init__(self, parent, offence, defence):
        self.offence = offence
        self.defence = defence

    def attack(self, target):
        pass

    def damage(self, amount):
        self.life = self.life - amount



###################
#
# Personalities ('act')
#
###################
class Follower:
    def __init__(self, parent):
        self.parent = parent
        self.path = []
        self.target = None

    def __call__(self, dm):
        if not self.target:
            self.target = dm.pc

        if len(self.path) < random.randint(1,4):
            path_start = self.parent.loc()
            path_end = random.choice(self.target.percept.fov)
            self.path = dm.find_path(path_start, path_end)
        else:
            target_loc = self.path.pop()
            target = dm.get_target(target_loc, True)
            if not target.block.motion:
                self.parent.loc.update(target_loc)


    
class PersonalityA:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self, dm):
        fov = self.parent.percept.look(dm.terrain)
        foes = [e for e in dm.entities if e.loc() in fov and hasattr(e,'initiative') and abs(e.life.personality - self.parent.life.personality) > 5]
        try:
            foe = foes[0]
        except IndexError:
            """ No foes are in range """ 
            return

        if self.parent.life.health_current > 1:
            """ ATTACK """
            path = dm.find_path(self.parent.loc(), foe.loc())
            target_loc = path.pop()
            try:
                target = dm.get_target(target_loc, True)
                if target in foes:
                    actions.melee_attack(dm, self.parent, target)
                elif not target.block.motion:
                    self.parent.loc.update(target_loc)
                else:
                    ui.narrative.add(f'{target} blocks the way of {self.parent}.')
                return
                
            except IndexError as e:
                """ there is no unblocked path to the foe """
                # TODO: if being in way plot path and more as far a possible
                return

        else:
            """ FLEE """
            resistance_map = pf.dijkstra(dm.terrain.motionmap, {foe.loc(): 0})[1]
            # Reverse movement costs so entity flees starting points
            # Recalculate Dijkstra algorithm
            resistance_map = {key:value * -1.175 for (key, value) in resistance_map.items()}
            paths = pf.dijkstra(dm.terrain.motionmap, resistance_map)[0]
            target_loc = paths[self.parent.loc()]
            target = dm.get_target(target_loc, True)
            
        if not target.block.motion:
            self.parent.loc.update(target_loc)
        else:
            ui.narrative.add(f'The {target} blocks {self.parent}\'s way.')


class PlayerInput:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self, dm):
        # Clear messages in narrative display
        ui.narrative.archive()

        # Return action according to player's input
        fn, args = keyboard.GameInput().capture_keypress() 
        fn(dm, self.parent, args)



###################
#
# Entities
#
###################

class Entity():
    def __init__(self, kind, loc, glyph, fg, bg, block, abilities=None):
        self.kind = kind
        self.title = None
        self.loc = loc if isinstance(loc, Location) else Location(loc)
        self.glyph = glyph
        self.fg = fg
        self.bg = bg
        self.block = block
            
        # Create properties for all kwargs
        if abilities:
            for name, ability in abilities.items():
                self.add_ability(name, ability)
            

    @property
    def name(self):
        return self.__str__()

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.kind 
   
    # Used for bisect sort
    def __lt__(self, other):
        attrs1 = dir(self)
        attrs2 = dir(other)
        if 'perform' in attrs2 and 'perform' not in attrs1:
            return True
        elif other.block.motion == True and self.block.motion == False:
            return True
        return False

    def add_ability(self, name, ability):
        klass, args = ability
        setattr(self, name, klass(self, *args))

    def del_ability(self, name):
        delattr(self, name)

class Tile:
    def __init__(self, kind, abilities=None):
        self.kind = kind
        self.glyph = COMMON_TRAITS[kind].glyph
        self.fg = COMMON_TRAITS[kind].fg
        self.bg = COMMON_TRAITS[kind].bg
        self.block = COMMON_TRAITS[kind].block
        self.seen = False
        
        # Create properties for abilities
        if abilities:
            for name, ability in abilities.items():
                self.add_ability(name, ability)
    
    @property
    def name(self):
        return self.__str__()

    def __str__(self):
        return self.kind

    def add_ability(self, name, ability):
        klass, args = ability
        setattr(self, name, klass(self, *args))


class HandGun(Entity):
    def __init__(self, loc):
        super().__init__(
            'handgun',
            loc,
            *COMMON_TRAITS['weapon']
        )
        self.charges = 3

    def act(self, dm):
        self.charges -= 1
        ui.narrative.add(f'the weapon discharges. ({self.charges} left)')


class Scanner(Entity):
    def __init__(self, loc):
        super().__init__(
            'scanner',
            loc,
            *COMMON_TRAITS['tech device'],
        )

    def act(self, dm):
        ui.narrative.add(f'The {self.kind} acts.')
        actions.display_entity_type(self, dm)
        
class Radar(Entity):
    def __init__(self, loc):
        super().__init__(
            'radar',
            loc,
            *COMMON_TRAITS['tech device'],
        )

    def act(self, dm):
        ui.narrative.add(f'The {self.kind} shows escape routes.')
        actions.flee_map(self, dm)
