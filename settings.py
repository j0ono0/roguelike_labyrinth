from collections import namedtuple
import tcod.event

SCREEN_WIDTH = 102
SCREEN_HEIGHT = 43

# Map must be odd dimensions. 
# This allows 100% fill with alternating corridor/walls
MAP_WIDTH = 53
MAP_HEIGHT = 39
MAP_OFFSET = (3,2)

# narrative window
NAR_WIDTH = 40
NAR_HEIGHT = 39
NAR_OFFSET = (58,2)

# Create a dictionary that maps keys to vectors.
# Names of the available keys can be found in the online documentation:
# http://packages.python.org/tdl/tdl.event-module.html
MOVEMENT_KEYS = {
    # standard arrow keys
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
}
ACTION_KEYS = {
    tcod.event.K_SPACE: True
}

Obj = namedtuple('Obj', ['glyph','fg', 'block_sight', 'block_motion'])
ELEMENTS = {
    'player':       Obj('@', [255, 255, 255], False, False),
    'human':        Obj('@', [220, 220, 220], False, False),
    'ground':       Obj('.', [100, 100, 100], False, False),
    'stairs_down':  Obj('>', [255, 255, 255], False, False),
    'stairs_up':    Obj('<', [255, 255, 255], False, False),
    'wall':         Obj('#', [120, 120, 120], True,  True),
    'tech_device':      Obj('+', [120, 150, 110], False, False),
    ## Elements that render if unseen ##
    'ground--unseen':   Obj('.', [50, 50, 50], False, False),
    'wall--unseen':     Obj('#', [70, 70, 70], True,  True),
}