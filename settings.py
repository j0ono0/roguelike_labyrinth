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
NAR_HEIGHT = 29
NAR_OFFSET = (58,2)

# Player's character details
PC_WIDTH  = 40
PC_HEIGHT = 8
PC_OFFSET = (58, 33)

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

Obj = namedtuple('Obj', ['glyph','fg', 'bg', 'block'])
Block = namedtuple('Block', ['motion', 'sight'])

AUTHORITIES = ['detective', 'police officer', 'player character']

COMMON_TRAITS = {
    'player character': Obj('@', [255, 255, 255], [0, 0, 0], Block(True,  False)),
    'citizen':          Obj('c', [210, 150, 180], [0, 0, 0], Block(True,  False)),
    'police officer':   Obj('P', [100, 150, 255], [0, 0, 0], Block(True,  False)),
    'detective':        Obj('D', [ 50,  50, 100], [0, 0, 0], Block(True,  False)),
    'feline':           Obj('f', [180, 120,  80], [0, 0, 0], Block(True,  False)),
    'sheep':            Obj('s', [200, 200, 200], [0 ,0 ,0], Block(True,  False)),
    'exit down':        Obj('>', [255, 255, 255], [0, 0, 0], Block(False, False)),
    'exit up':          Obj('<', [255, 255, 255], [0, 0, 0], Block(False, False)),
    'tech device':      Obj('+', [120, 150, 110], [0, 0, 0], Block(False, False)),
    'weapon':           Obj('/', [220, 220, 255], [0, 0, 0], Block(False, False)),
    'consumable':       Obj('%', [200, 120, 120], [0, 0, 0], Block(False, False)),
    'ground':           Obj('.', [ 60,  60,  60], [25, 25, 25], Block(False, False)),
    'wall':             Obj('#', [120, 120, 120], [25, 25, 25], Block(True, True)),
}

HELP_TEXT = "\
Roguelike development game is a work in progress. The basic mechanics are almost completed.\n\n\
move: arrow keys & numpad\n\
select: enter, numpad 5\n\
u use from pack\n\
U use from ground\n\
d drop\n\
I interrogate\n\
, pickup\n\
. look\n\
"

