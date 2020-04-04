#!/usr/bin/env python
import random
import tcod

from elements import library as el
import level_handler as lvl
import keyboard
import interface as ui
import narrative
from settings import *

# Setup keyboard input
kb = keyboard.GameInput()

# Setup the font.
tcod.console_set_custom_font(
    "terminal8x12_gs_tc.png",
    tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
)

# Delete existing saved levels
lvl.delete_all()

# Create first environment
print('Creating starting level')
lvl.create(MAP_WIDTH, MAP_HEIGHT)

# Setup player
player = el.being('player_01','@', 16)
player.loc.update(lvl.env.random_unblocked_loc())

# Update players field of view
player.percept.scan(lvl.env.fov_array())
lvl.update_seen(player.percept.fov)

# Initialize the root console in a context.
with tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, order="F") as console:
    console.default_fg = [80,80,80]
    console.default_bg = [0,0,0]
    console.default_bg_blend = 0
    while True:

        # update player field of view
        player.percept.scan(lvl.env.fov_array())
        lvl.update_seen(player.percept.fov)
        
        # Update console and render.
        console.clear()
        console.draw_frame(MAP_OFFSET[0] - 1, MAP_OFFSET[1] - 1, MAP_WIDTH + 2, MAP_HEIGHT + 2)
        console.draw_frame(NAR_OFFSET[0] - 1, NAR_OFFSET[1] - 1, NAR_WIDTH + 2, NAR_HEIGHT + 2)

        """
        # Print pathfinding
        for ex in lvl.exits():
            if ex.glyph == '>':
                color = [60,255,100]
                glyph = '.'
            else:
                color = [255,100,100]
                glyph = '.'
            
            for loc in lvl.find_path(player.loc(), ex.loc())[1:]:
                lvl_con.print(*loc, glyph, color)
        """
        
        lvl.blit(console, player.percept.fov)
        ui.narrative.blit(console)
        console.print(*(x + y for x, y in zip(MAP_OFFSET, player.loc())), player.glyph, ELEMENTS['player'].color)
        tcod.console_flush()
        
        # User input
        fn, args, kwargs = kb.capture_keypress()
        if fn == 'move':
            try:
                loc = player.loc.proposed(args)
                target = lvl.get_target(loc, True)
                try:
                    target.action(player, target, lvl)
                except AttributeError:
                    ui.narrative.add('The {} blocks your way.'.format(target.name))
            except IndexError as e:
                # Player reached edge of environment
                ui.narrative.add('There is no way through here!')

        elif fn == 'use':
            menu = ui.SelectMenu('Inventory', console)
            target = menu.select(player.inventory.items) or lvl.get_target(player.loc())
            try:
                target.action(player, target, lvl)
            except AttributeError:
                ui.narrative.add('You see no way to use the {}.'.format(target.name))

        elif fn == 'pickup_select':
            targets = [t for t in lvl.env.entities if t.loc() == player.loc()]
            if len(targets) > 1:
                """ display select menu here """
            elif len(targets) == 1:
                player.inventory.pickup(player, targets.pop(), lvl)
            else:
                ui.narrative.add('There is nothing here to pickup.')

        elif fn == 'drop_select':
            menu = ui.SelectMenu('Inventory', console)
            target = menu.select(player.inventory.items)
            player.inventory.drop(player, target, lvl)