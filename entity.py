###########################################################
#
# Base for all physical objects that exist in the game space
#
###########################################################
from collections import namedtuple
from levels import field_of_view

class Entity():
    def __init__(self, name, glyph, coords=(0,0)):
        self.name = name
        self.glyph = glyph
        self._x = coords[0]
        self._y = coords[1]
        
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
        
    def use(self, tool):
        tool.action(self)


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

# Build 'beings' ie: monsters & player character
def being(name, glyph, vision):
    b = Entity(name, glyph)
    percept = Vision(vision, b.loc)
    setattr(b, 'percept', percept)
    return b