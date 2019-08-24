###########################################################
#
# Base for all physical objects that exist in the game space
#
###########################################################
from collections import namedtuple

class Entity:
    def __init__(self, name, glyph, loc=None):
        self.name = name
        self.glyph = glyph
        self.loc = Location()
        self.action = None
    
    def __str__(self):
        return self.name

    def use(self, tool):
        tool(self)

class Location:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
    def __call__(self):
        return self.x, self.y
        
    def set(self, x, y):
        self.x = x
        self.y = y
        
    def move(self, dx, dy, map):
        loc = (self.x + dx, self.y + dy)
        if not map.tiles[loc].blocked:
            self.x = loc[0]
            self.y = loc[1]