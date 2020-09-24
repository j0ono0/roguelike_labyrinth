###########################################################
#
# Base for all physical objects that exist in the game space
#
###########################################################
from collections import namedtuple
import field_of_view
from user_interface import interfaces as ui 
from settings import COMMON_TRAITS, Obj


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
        self.parent.del_ability('perform')
       
        

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
# Entities
#
###################

class Entity():
    def __init__(self, kind, loc, glyph, fg, bg, block, abilities):
        self.kind = kind
        self.title = None
        self.loc = loc if isinstance(loc, Location) else Location(loc)
        self.glyph = glyph
        self.fg = fg
        self.bg = bg
        self.block = block
            

        # Create properties for all kwargs
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
        fn, args = ability
        setattr(self, name, fn(self, *args))

    def del_ability(self, name):
        delattr(self, name)

class Tile:
    def __init__(self, kind, abilities):
        self.kind = kind
        self.glyph = COMMON_TRAITS[kind].glyph
        self.fg = COMMON_TRAITS[kind].fg
        self.bg = COMMON_TRAITS[kind].bg
        self.block = COMMON_TRAITS[kind].block
        self.seen = False
        
        # Create properties for all kwargs
        for name, ability in abilities.items():
            self.add_ability(name, ability)
    
    @property
    def name(self):
        return self.__str__()

    def __str__(self):
        return self.kind

    def add_ability(self, name, ability):
        fn, args = ability
        setattr(self, name, fn(self, *args))