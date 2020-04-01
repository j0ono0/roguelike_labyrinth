#!/usr/bin/env python
import random
import tcod

from elements import library as el
import level_handler as lvl
from settings import *


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

# Setup player
player = el.being('player_01','@', 16)
player.set_loc(lvl.env.random_unblocked_loc())

# Update players field of view
player.percept.scan(lvl.env.fov_array())
lvl.update_seen(player.percept.fov)

# Initialize the root console in a context.
with tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, order="F") as console:
    while True:
        
        # update player field of view
        player.percept.scan(lvl.env.fov_array())
        lvl.update_seen(player.percept.fov)
        
        # Update console and render.
        console.clear()
        lvl_con = lvl.render(player.percept.fov)
        
        # Print pathfinding
        for ex in lvl.exits():
            if ex.glyph == '>':
                color = [60,255,100]
                glyph = '+'
            else:
                color = [255,100,100]
                glyph = '-'
            
            for loc in lvl.find_path(player.loc(), ex.loc())[1:]:
                lvl_con.print(*loc, glyph, color)
        
        lvl_con.print_(*player.loc(), player.glyph)
        
        console.print_frame(MAP_OFFSET[0] - 1, MAP_OFFSET[1] - 1, MAP_WIDTH + 2, MAP_HEIGHT + 2)
        lvl_con.blit(console, *MAP_OFFSET)
        tcod.console_flush()

        # User input
        for event in tcod.event.wait():
            if event.type == 'KEYDOWN':

                if event.sym in MOVEMENT_KEYS:
                    # Movement interacts with tile only 
                    try:
                        x, y = player.proposed_loc(MOVEMENT_KEYS[event.sym])
                        target = lvl.env.tiles[x][y]
                        try:
                            target.action(player, target, lvl)
                        except AttributeError:
                            print('The {} blocks your way.'.format(target.name))
                        
                    except IndexError as e:
                        # Player reached edge of environment
                        print('There is no way through here!')
                elif event.sym in ACTION_KEYS:
                    # Action keys interact with elements ion tile
                    # or tile if no elements are present
                    target = lvl.get_target(player.loc(), blocked=False)
                    try:
                        target.action(player, target, lvl)
                    except AttributeError:
                        print('You see no way to use the {}.'.format(target.name))
                    

            if event.type == 'QUIT':
                # Halt the script using SystemExit
                raise SystemExit('The window has been closed.')