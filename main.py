#!/usr/bin/env python

from environment import library as el
import dungeon_master as dm
from user_interface import interfaces as ui
from user_interface import keyboard


# Delete existing saved levels
dm.delete_all()

# Create first environmentexit()
print('Creating starting level')
dm.create()
# Setup player

player = el.player_character('Deckard', dm.random_unblocked_loc())
# update player field of view
player.percept.see(dm.terrain.sightmap)
dm.terrain.mark_as_seen(player.percept.fov)

dm.entities.append( player)

# Assign game assets to displays
ui.player.c = player
ui.game.entities = dm.entities
ui.game.terrain = dm.terrain

# Assign player to display and do initial render of screen
dm.render_game(player.percept.fov)


while player.life():

    # TODO: roll initiative
    for e in dm.entities:

        # Entities perform in turn
        try:
            e.perform()
        except AttributeError:
            """ this entity has no personality """
        
        # Rerender after each turn
        dm.render_game(player.percept.fov)

print('the game is over. The player character is dead beyond repair.')
print('press a key to exit.')
keyboard.CharInput().capture_keypress()