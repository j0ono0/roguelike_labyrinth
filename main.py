#!/usr/bin/env python
import random
import tcod
import tcod.event
import entity
from levels import field_of_view as fov 
import level_handler as lvl
from settings import *

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
player = entity.being('player_01','@', 16)
player.set_loc(lvl.env.random_unblocked_loc())

# Update players field of view
player.percept.scan(lvl.env.fov_array())
lvl.update_seen(player.percept.fov)

# Initialize the root console in a context.
with tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, order="F") as console:
    while True:
        # Update console and render.
        console.clear()
        lvl_con = lvl.render(player.percept.fov)
        
        # Print pathfinding
        for ex in lvl.exits():
            if ex.action.dest_id >= lvl.env.id:
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
                    try:
                        loc = player.proposed_loc(MOVEMENT_KEYS[event.sym])
                        dest_obj = lvl.move_interaction(loc)
                        if not dest_obj:
                            player.set_loc(loc)
                            player.percept.scan(lvl.env.fov_array())
                            lvl.update_seen(player.percept.fov)
                        else:
                            print('a {} is blocking your way.'.format(dest_obj.name))
                        
                    except KeyError as e:
                        print('There is no way through here!')
                elif event.sym in ACTION_KEYS:
                    item = [e for e in lvl.env.entities if e.loc() == player.loc][0]
                    #Player uses item at location
                    player.use(item)
                    

            if event.type == 'QUIT':
                # Halt the script using SystemExit
                raise SystemExit('The window has been closed.')