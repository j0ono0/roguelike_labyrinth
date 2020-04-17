from collections import namedtuple
import tcod.event

LEVEL_PREFIX = 'env_'


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

Obj = namedtuple('Obj', ['glyph','fg', 'bg', 'block_motion', 'block_sight'])
ELEMENTS = {
    'player_character': Obj('@', [255, 255, 255], [0, 0, 0],  True, False),
    'human':            Obj('@', [200, 160, 120], [0, 0, 0],  True, False),
    'stairs_down':      Obj('>', [255, 255, 255], [0, 0, 0], False, False),
    'stairs_up':        Obj('<', [255, 255, 255], [0, 0, 0], False, False),
    'tech_device':      Obj('+', [120, 150, 110], [0, 0, 0], False, False),
    'ground':           Obj('.', [60, 60, 60], [25, 25, 25], False, False),
    'wall':             Obj('#', [120, 120, 120], [25, 25, 25], True,  True),
}

HELP_TEXT = "\
Roguelike development game is a work in progress. The basic mechanics are almost completed.\n\n\
move: arrow keys & numpad\n\
select: enter, numpad 5\n\
u use\n\
d drop\n\
, pickup\n\
. look\n\
"