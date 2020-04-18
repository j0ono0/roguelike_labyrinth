#!/usr/bin/env python
import random
import tcod
from elements import library as el
import dungeon_master as dm
from user_interface import keyboard
from user_interface import interfaces as ui
# Setup keyboard input
kb = keyboard.GameInput()

# Delete existing saved levels
dm.delete_all()

# Create first environmentexit()
print('Creating starting level')
dm.create()
# Setup player

player = el.player_character('Deckard', dm.random_unblocked_loc())
dm.entities.append(player)

while True:

    # TODO: roll initiative
    for e in dm.entities:
        try:
            e.perform()
        except AttributeError:
            """ this entity has no personality """
