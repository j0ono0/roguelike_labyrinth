#!/usr/bin/env python
import random
import tcod
import tcod.event
from entity import Entity
from pathfinding import astar
import level_handler as lvl
from settings import *

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
# Delete existing saved levels
lvl.delete_all()

# Create first environment
print('Creating starting level')
lvl.create(MAP_WIDTH, MAP_HEIGHT)
lvl.add_exit(lvl.env.random_unblocked_loc(), 2)

# Setup player
player = Entity('Player_01', '@')
player.loc.set(*lvl.env.random_unblocked_loc())

# Update environment with player placed
lvl.update_fov(player.loc())

# Pathfinding demo
def path_to_loc(loc):
    start = player.loc()
    return astar(lvl.env.tiles, start, loc)

# Initialize the root console in a context.
with tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, order="F") as console:
    while True:
        # Update console and render.
        console.clear()
        lvl_con = lvl.env.con()
        
        # Render player fov
        for loc in player.fov:
            glyph = lvl.env.tiles[loc].glyph
            color = [120, 120, 120]
            lvl_con.print(*loc, glyph, color)

        # Print pathfinding
        exits = lvl.exits()
        for ex in lvl.exits():
            if ex.action.dest_id >= lvl.env.id:
                color = [60,255,100]
                glyph = '+'
            else:
                color = [255,100,100]
                glyph = '-'
            for loc in path_to_loc(ex.loc()):
                lvl_con.print(*loc, glyph, color)
        
        # Print entities list
        for en in lvl.env.entities:
            if en.loc() in player.fov:
                lvl_con.print_(*en.loc(), en.glyph)
        
        lvl_con.print_(*player.loc(), player.glyph)
        
        #console.print_frame(0, 0, MAP_WIDTH + 2, MAP_HEIGHT + 2)
        lvl_con.blit(console, *MAP_OFFSET)
        tcod.console_flush()

        # User input
        for event in tcod.event.wait():
            if event.type == 'KEYDOWN':

                if event.sym in MOVEMENT_KEYS:
                    try:
                        player.loc.move(*MOVEMENT_KEYS[event.sym], lvl.env)
                        lvl.update_fov(player.loc())
                        lvl.update_entity_fov(player)
                        
                    except KeyError as e:
                        print('That way appears blocked!')
                elif event.sym in ACTION_KEYS:
                    item = [e for e in lvl.env.entities if e.loc() == player.loc()][0]
                    #Player uses item at location
                    player.use(item)
                    

            if event.type == 'QUIT':
                # Halt the script using SystemExit
                raise SystemExit('The window has been closed.')