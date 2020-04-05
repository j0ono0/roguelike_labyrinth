#!/usr/bin/env python
import random
import tcod
import consoles
from consoles import root_console as console
from elements import library as el
import level_handler as lvl
import keyboard
import interface as ui
from settings import *
# Setup keyboard input
kb = keyboard.GameInput()



# Delete existing saved levels
lvl.delete_all()

# Create first environment
print('Creating starting level')
lvl.create(MAP_WIDTH, MAP_HEIGHT)

# Setup player
player = el.human('Deckard', 'player')
player.loc.update(lvl.env.random_unblocked_loc())

while True:

    # update player field of view
    player.percept.see(lvl.env.fov_array())
    lvl.update_seen(player.percept.fov)
    
    # Render game to screen
    console.clear()
    consoles.render_base()
    
    lvl.blit(player.percept.fov)
    ui.narrative.blit()
    console.print(*(x + y for x, y in zip(MAP_OFFSET, player.loc())), player.glyph, player.fg)
    
    tcod.console_flush()
    
    # Process user input
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
        menu = ui.SelectMenu('Inventory')
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
        menu = ui.SelectMenu('Inventory')
        target = menu.select(player.inventory.items)
        player.inventory.drop(player, target, lvl)

    