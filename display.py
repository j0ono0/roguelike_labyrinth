import tcod
from settings import *


# Setup the font.
tcod.console_set_custom_font(
    "terminal8x12_gs_tc.png",
    tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
)

# Init root console
console = tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")

# Set defaults
console.default_fg = [80,80,80]
console.default_bg = [0,0,0]
console.default_bg_blend = 0

def render_base():
    console.draw_frame(MAP_OFFSET[0] - 1, MAP_OFFSET[1] - 1, MAP_WIDTH + 2, MAP_HEIGHT + 2)
    console.draw_frame(NAR_OFFSET[0] - 1, NAR_OFFSET[1] - 1, NAR_WIDTH + 2, NAR_HEIGHT + 2)
