"""

Common rendering-to-screen processes

"""

import tcod
from settings import *


class NarrativeConsole:
    def __init__(self):
        self.con = tcod.console.Console(NAR_WIDTH, NAR_HEIGHT, order="F")
        
    def clear(self):
        self.con.clear(ord(' '), [0,0,0],[0,0,0])

    def blit(self, flush=False):
        self.con.blit(root_console, *NAR_OFFSET, 0, 0, NAR_WIDTH, NAR_HEIGHT, 1, 1, 0)
        if flush:
            tcod.console_flush()


class EnvironmentConsole:
    def __init__(self):
        self.con = tcod.console.Console(MAP_WIDTH, MAP_HEIGHT, order="F")

    def blit(self, flush=False):
        self.con.blit(root_console, *MAP_OFFSET, 0, 0, MAP_WIDTH, MAP_HEIGHT, 1, 1, 0)
        if flush:
            tcod.console_flush()


# Setup the font.
tcod.console_set_custom_font(
    "terminal8x12_gs_tc.png",
    tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
)

# Init root console
root_console = tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")

# Set defaults
root_console.default_fg = [80,80,80]
root_console.default_bg = [0,0,0]
root_console.default_bg_blend = 0

def render_base():
    root_console.draw_frame(MAP_OFFSET[0] - 1, MAP_OFFSET[1] - 1, MAP_WIDTH + 2, MAP_HEIGHT + 2)
    root_console.draw_frame(NAR_OFFSET[0] - 1, NAR_OFFSET[1] - 1, NAR_WIDTH + 2, NAR_HEIGHT + 2)