###########################################################
#
# Base for all physical objects that exist in the game space
#
###########################################################
from collections import namedtuple
import field_of_view
from user_interface import interfaces as ui 
from settings import ELEMENTS, Obj


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
 
    def see(self, terrain):
        self.fov = field_of_view.scan(self.parent.loc(), terrain, self.max_vision)


class Life:
    def __init__(self, parent, max, personality=None):
        self.parent = parent
        self.max = max
        self.current = max
        self.personality = personality

    def __call__(self):
        return self.current > 0

    def damage(self, num):
        self.current = self.current - num
        if self.current <= 0:
            self.die()

    def die(self):
        ui.narrative.add('{} dies'.format(self.parent))
        for attr in Obj._fields:
            setattr(self.parent, attr, getattr(ELEMENTS['corpse'], attr))
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
    def __init__(self, kind, name=None, loc=Location(), abilities={}):
        self.kind = kind
        self.name = name
        self.loc = loc
        self.glyph = ELEMENTS[kind].glyph
        self.fg = ELEMENTS[kind].fg
        self.bg = ELEMENTS[kind].bg
        self.block = ELEMENTS[kind].block
        # Create properties for all kwargs
        for name, ability in abilities.items():
            self.add_ability(name, ability)
        
    def __str__(self):
        return f"{self.name}" if self.name else f"A {self.kind}" 
   
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
        self.glyph = ELEMENTS[kind].glyph
        self.fg = ELEMENTS[kind].fg
        self.bg = ELEMENTS[kind].bg
        self.block = ELEMENTS[kind].block
        self.seen = False
        
        # Create properties for all kwargs
        for name, ability in abilities.items():
            self.add_ability(name, ability)
        
    def __str__(self):
        return self.kind

    def add_ability(self, name, ability):
        fn, args = ability
        setattr(self, name, fn(self, *args))