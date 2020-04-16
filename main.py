#!/usr/bin/env python
import random
import tcod
from elements import library as el
import level_handler as lvl
import keyboard
import interface as ui
from settings import *
# Setup keyboard input
kb = keyboard.GameInput()

# Delete existing saved levels
lvl.delete_all()

# Create first environmentexit()
print('Creating starting level')
lvl.create(MAP_WIDTH, MAP_HEIGHT)

# Setup player
player = el.player_character('Deckard', lvl.env.random_unblocked_loc())
lvl.env.entities.append(player)

while True:

    # TODO: roll initiative
    for e in lvl.env.entities:
        try:
            e.perform(lvl)
        except AttributeError:
            """ this entity has no personality """
