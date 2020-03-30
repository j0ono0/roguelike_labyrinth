import tcod.event

SCREEN_WIDTH = 30
SCREEN_HEIGHT = 30
# Map must be odd dimensions. 
# This allows 100% fill with alternating corridor/walls
MAP_WIDTH = 9
MAP_HEIGHT = 9
MAP_OFFSET = (3,1)

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
