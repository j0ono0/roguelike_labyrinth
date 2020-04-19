###########################################################
#
# Base for all physical objects that exist in the game space
#
###########################################################
from collections import namedtuple
import field_of_view
from user_interface import interfaces as ui 
from settings import ELEMENTS, Obj
import dungeon_master as dm


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

    def add(self, item):
        self.items.insert(0, item)

    def pickup(self, target):
        e = dm.entities
        i = e.index(target)
        self.add(e.pop(i))
        target.loc = self.parent.loc
        ui.narrative.add('{} picks up a {}.'.format(self.parent.kind, target.kind))

    def drop(self, target):
        try:
            i = self.items.index(target)
            target.loc = Location(target.loc())
            dm.entities.append(self.items.pop(i))
            ui.narrative.add('{} drops a {}.'.format(self.parent.name, target.name))
        except ValueError:
            """
            Action aborted.
            Keypress does not match any inventory items.
            """


class Perception:
    def __init__(self, parent, max_vision):
        self.max_vision = max_vision
        self.loc = parent.loc
        self.fov = []
 
    def see(self, terrain):
        self.fov = field_of_view.scan(self.loc(), terrain, self.max_vision)


class Life:
    def __init__(self, parent, max):
        self.parent = parent
        self.max = max
        self.current = max

    def damage(self, num):
        self.current = self.current - num
        if self.current >= 0:
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
        return f"{self.name} the {self.kind}" if self.name else f"A {self.kind}" 


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