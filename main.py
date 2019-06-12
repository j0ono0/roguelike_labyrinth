#!/usr/bin/env python
import random
import tcod
import tcod.event
from maps.maze import PrimsMaze
from maps.dungeon import Dungeon
from entity import Entity

#################

MAP_WIDTH = 15
MAP_HEIGHT = 15

#################

# Create a dictionary that maps keys to vectors.
# Names of the available keys can be found in the online documentation:
# http://packages.python.org/tdl/tdl.event-module.html
MOVEMENT_KEYS = {
    # standard arrow keys
    tcod.event.K_UP: [0, -1],
    tcod.event.K_DOWN: [0, 1],
    tcod.event.K_LEFT: [-1, 0],
    tcod.event.K_RIGHT: [1, 0],
}
ACTION_KEYS = {
    tcod.event.K_SPACE: True
}

# Setup the font.
tcod.console_set_custom_font(
    "arial10x10.png",
    tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
)

map = PrimsMaze(MAP_WIDTH, MAP_HEIGHT)
map.build()

# Setup player
player = Entity('Player_01', '@')
player.loc.set(*map.entry)

# Update map with player fov
map.fov.scan(player.loc())

# Setup exit
exit = Entity('Exit', '>')
exit.loc.set(*map.exit)
entities = [exit, player]


# Initialize the root console in a context.
with tcod.console_init_root(MAP_WIDTH, MAP_HEIGHT, order="F") as console:
    while True:
        # Update console and render.
        console.clear()
        map.con().blit(console)
        
        for en in entities:
            if map.tiles[en.loc()].visible:
                console.print_(*en.loc(), en.glyph)
            
        # Test for maze completion
        if player.loc() == exit.loc():
            msg = ['Next level:{}'.format(map.level + 1), '<space>']
            y = (MAP_HEIGHT - len(msg)) // 2
            for i, ln in enumerate(msg):
                x = (MAP_WIDTH - len(ln)) // 2
                console.print_(x, y + i, ln)
        
        tcod.console_flush()

        # User input
        for event in tcod.event.wait():
            if event.type == 'KEYDOWN':
                if event.sym in MOVEMENT_KEYS:
                    player.loc.move(*MOVEMENT_KEYS[event.sym], map)
                    map.fov.scan(player.loc())
                elif event.sym in ACTION_KEYS and player.loc() == exit.loc():
                    map.build()
                    exit.loc.set(*map.exit)

            if event.type == 'QUIT':
                # Halt the script using SystemExit
                raise SystemExit('The window has been closed.')