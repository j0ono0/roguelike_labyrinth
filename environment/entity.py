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
from settings import COMMON_TRAITS, AUTHORITIES, Obj
import pathfinding as pf
from input_commands import target_select
from line_of_sight import LineOfSight as los


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
    def __init__(self, parent, health_max, is_android=False):
        self.parent = parent
        self.health_max = health_max
        self.health_current = health_max
        self.android = is_android
        # Personality is a 'spectrum' expressed as int
        # +10: extremist anti-android and pro-life
        # -10: extremist pro-android and anti-life

    def __call__(self):
        return self.health_current > 0

    def damage(self, num):
        self.health_current = self.health_current - num
        if self.health_current <= 0:
            self.die()

    def die(self):
        if self.android:
            ui.narrative.add(f'The {self.parent.name} was an android!')
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
        self.parent = parent
        self.offence = offence
        self.defence = defence
        self.current_target = None

    def attack(self, target):
        att_str = max([random.randint(1,100) for x in range(self.offence)])
        def_str = max([random.randint(1,100) for x in range(target.combat.defence)])
        if att_str > def_str:
            ui.narrative.add(f'{self.parent.kind} wounds {target.kind}.')
            target.life.damage(random.randint(0,3))
        elif att_str < def_str * 0.5:
            ui.narrative.add(f'{self.parent.kind} is overwhelmed by {target.kind} ferocity.')
            self.parent.life.damage(1)
        else:
            ui.narrative.add(f"{target.kind} defends {self.parent.kind}' attack.")

    def aquire_target(self, entities):
        foes = [e for e in entities if hasattr(e,'initiative')]
        sorted(foes, key = lambda foe: pf.distance(self.parent.loc(), foe.loc()))
        if len(foes) == 0:
            self.current_target = None
        elif self.current_target not in entities:
            # Aquire new target
            self.current_target = foes[-1]
            print(f'{self.parent} aquired target: {self.current_target}.')

        return self.current_target

###################
#
# Personalities ('act')
#
###################
class Cat:
    def __init__(self, parent):
        self.parent = parent
        self.owner = None
        self.target = None
        self.path = []

    def __call__(self, dm):
        # Initial fov update
        if not self.parent.percept.fov:
            self.parent.percept.look(dm.terrain)
        # Assign owner
        if not self.owner and dm.pc.loc() in self.parent.percept.fov:
            self.owner = dm.pc
            ui.narrative.add(f'A cat takes a liking to {self.owner.name}.')
        # Path to target
        if self.target:
            if self.target.loc() not in self.path:
                self.path = dm.find_path(self.parent.loc(), self.target.loc())
        # Path following owner
        elif self.owner and not self.path:
            path_start = self.parent.loc()
            path_end = random.choice(self.owner.percept.fov)
            self.path = dm.find_path(path_start, path_end)
        if self.path:
            # follow path
            target_loc = self.path.pop()
            target = dm.get_target(target_loc, True)
            # Move
            if not target.block.motion:
                self.parent.loc.update(target_loc)

        

class Citizen:
    def __init__(self, parent):
        self.parent = parent
        self.fov = []

    def __call__(self, dm):
        if not self.fov:
            self.fov = self.parent.percept.look(dm.terrain)
        #entities_in_fov = [e for e in dm.entities if e.loc() in self.fov]
        authorities_in_fov = [e for e in dm.entities if e.loc() in self.fov and e.kind in AUTHORITIES]
        # androids flee police and detectives unless they are also androids
        if self.parent.life.android and authorities_in_fov:
            flee_map = pf.flee_map(dm.terrain.motionmap, {e.loc(): 0 for e in authorities_in_fov})
            """
            try:
                target_loc = flee_map[self.parent.loc()]
                target = dm.get_target(target_loc, True)
                if not target.block.motion:
                    ui.narrative.add(f'The paranoid android runs!')
                    self.parent.loc.update(target_loc)
                else:
                    ui.narrative.add(f'The {target.name} blocks {self.parent.name}\'s way.')
            except Exception as e:
                print('error in citizen act: ', e)
            """

class Sentry:
    def __init__(self, parent):
        self.parent = parent
        self.fov = []
        self.pathmap = None # Dict
    
    def flee_current_loc(self, dm):
        coords = self.pathmap[self.parent.loc()]
        print('fleeing current loc.')
        target = dm.get_target(coords, True)
        if not target.block.motion:
            self.parent.loc.update(coords)
            self.fov = None
        else:
            #path is blocked
            self.pathmap = None
            ui.narrative.add(f'The {target.name} path is blocked.')


    def __call__(self, dm):
        # make a copy of motionmap and account for blocking entities
        motionmap = [row[:] for row in dm.terrain.motionmap]
        
        for e in dm.entities:
            if e.block.motion and e != self.parent:
                x, y = e.loc()
                motionmap[x][y] = False
        
        neighbour_locs =  pf.neighbours(motionmap, *self.parent.loc())
        
        if len(neighbour_locs) < 6:
            if self.pathmap:
                self.flee_current_loc(dm)
            else:
                self.pathmap = pf.flee_map(motionmap, {self.parent.loc():0})
                self.flee_current_loc(dm)
        else:
            self.pathmap = None
        
            if not self.fov:
                self.parent.percept.look(dm.terrain)
            
            if dm.pc.loc() in self.fov:
                aside = ' (android)' if self.parent.life.android else ''
                ui.narrative.add(f'The {aside} {self.parent.name} stands at {self.parent.loc()}.')
        
    
class PersonalityA:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self, dm):
        fov = self.parent.percept.look(dm.terrain)
        entities_in_fov = [e for e in dm.entities if e.loc() in fov]
        foe = self.parent.combat.aquire_target(entities_in_fov)


        if foe and self.parent.life.health_current > 2:
            """ ATTACK """
            try:
                path = dm.find_path(self.parent.loc(), foe.loc())
                target_loc = path.pop()
                
                target = dm.get_target(target_loc, True)
                if target is foe:
                    self.parent.combat.attack(target)
                elif not target.block.motion:
                    self.parent.loc.update(target_loc)
                else:
                    ui.narrative.add(f'{target} blocks the way of {self.parent}.')
                return
                
            except IndexError as e:
                """ there is no unblocked path to the foe """
                # TODO: if being in way plot path and more as far a possible
                return

        elif foe:
            """ FLEE """
            resistance_map = pf.dijkstra(dm.terrain.motionmap, {foe.loc(): 0})[1]
            # Reverse movement costs so entity flees starting points
            # Recalculate Dijkstra algorithm
            resistance_map = {key:value * -1.175 for (key, value) in resistance_map.items()}
            paths = pf.dijkstra(dm.terrain.motionmap, resistance_map)[0]
            target_loc = paths[self.parent.loc()]
            target = dm.get_target(target_loc, True)
        
        try:
            if not target.block.motion:
                self.parent.loc.update(target_loc)
            else:
                ui.narrative.add(f'The {target} blocks {self.parent}\'s way.')
        except Exception:
            pass # no target



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


###################
#
# Equipment
#
###################


class RangeWeapon:
    def __init__(self, parent, charges):
        self.parent = parent
        self.charges = charges

    def __call__(self, dm):
        ui.narrative.add('You aim the gun...')
        loc = target_select(dm, self.parent, None)
        if self.charges > 0:
            self.charges -= 1
            aim = los(self.parent.loc(), loc)
            path = aim.path(map=dm.terrain.motionmap)
            ui.narrative.add('And dial distance;')
            ui.narrative.add('The gun kicks as charged metal crackles through the air.')
            # Remove path loc that gun wielder occupies
            path = path[1:]
            for victim in [e for e in dm.entities if e.loc() in path and hasattr(e, 'life')]:
                try:
                    victim.life.damage(random.randint(2,10))
                except AttributeError:
                    ui.narrative.add(f'The {victim.name} smokes a little.')
        else:
            ui.narrative.add(f'The {self.parent.name} clicks quitely.')


class HandGun(Entity):
    def __init__(self, loc):
        super().__init__(
            'handgun',
            loc,
            *COMMON_TRAITS['weapon']
        )
        self.charges = 3

    def act(self, dm):
        ui.narrative.add(f'You aim the {self.name}.')
        target_loc = target_select(dm, self, None)
        self.charges -= 1
        ui.narrative.add(f'the weapon discharges at {target_loc}. ({self.charges} left)')


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
