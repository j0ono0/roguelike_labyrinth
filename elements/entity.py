###########################################################
#
# Base for all physical objects that exist in the game space
#
###########################################################
from collections import namedtuple
import field_of_view
import interface as ui 
from settings import ELEMENTS


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
    def __init__(self, max):
        self.items = []
        self.max = max

    def add(self, item):
        self.items.insert(0, item)

    def pickup(self, user, target, lvl):
        e = lvl.env.entities
        i = e.index(target)
        self.add(e.pop(i))
        target.loc = user.loc
        ui.narrative.add('{} picks up a {}.'.format(user.name, target.name))

    def drop(self, user, target, lvl):
        i = self.items.index(target)
        target.loc = Location(target.loc())
        lvl.env.entities.append(self.items.pop(i))
        ui.narrative.add('{} drops a {}.'.format(user.name, target.name))


class Perception():
    def __init__(self, vision, loc):
        self.vision = vision
        self.loc = loc
        self.fov = []
 
    def see(self, vismap):
        self.fov = field_of_view.scan(self.loc(), vismap, self.vision)


    



###################
#
# Entities
#
###################

Block = namedtuple('Block', ['motion', 'sight'])

class Entity():
    def __init__(self, name, kind, loc=Location(), action=None):
        self.name = name
        self.kind = kind
        self.loc = loc
        self.action = action
        self.glyph = ELEMENTS[kind].glyph
        self.fg = ELEMENTS[kind].fg
        self.bg = ELEMENTS[kind].bg
        self.block = Block(ELEMENTS[kind].block_motion, ELEMENTS[kind].block_sight)

    def __str__(self):
        return self.name

class Tile:
    def __init__(self, name, kind, action):
        self.name = name
        self.kind = kind
        self.glyph = ELEMENTS[kind].glyph
        self.fg = ELEMENTS[kind].fg
        self.bg = ELEMENTS[kind].bg
        self.block = Block(ELEMENTS[kind].block_motion, ELEMENTS[kind].block_sight)
        self.action = action
        self.seen = False


