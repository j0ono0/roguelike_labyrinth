###########################################################
#
# Base for all physical objects that exist in the game space
#
###########################################################
from collections import namedtuple
import field_of_view

class Entity():
    def __init__(self, name, glyph, blocked=True, coords=(0,0), action=None):
        self.name = name
        self.glyph = glyph
        self._x = coords[0]
        self._y = coords[1]
        self.blocked = blocked
        self.action = action

    def __str__(self):
        return self.name

    def loc(self):
        return (self._x, self._y)
    
    def set_loc(self, coords):
        self._x = coords[0]
        self._y = coords[1]
    
    def proposed_loc(self, coords):
        return (self._x + coords[0], self._y + coords[1])
    
    def move(self, coords):
            self.set_loc(self.proposed_loc(coords))

class Tile:
    def __init__(self, name, glyph, blocked, action):
        self.name = name
        self.base_glyph = glyph
        self.blocked = blocked
        self.action = action
        self.inventory = Inventory(5)
        self.seen = False
    
    @property
    def glyph(self):
        return self.inventory.first() or self.base_glyph


###################
#
# Entity attributes
#
###################

class Inventory:
    def __init__(self, max):
        self.items = []
        self.max = max

    def add(self, item):
        self.items.insert(0, item)

    def first(self):
        try:
            return self.items[0].glyph
        except IndexError:
            return None

class Vision():
    def __init__(self, vision, loc):
        self.vision = vision
        self.loc = loc
        self.fov = []
 
    def scan(self, vismap):
        self.fov = field_of_view.scan(self.loc(), vismap, self.vision)
    

class Being(Entity):
    def __init__(self, name, glyph):
        super.__init__(name, glyph)
