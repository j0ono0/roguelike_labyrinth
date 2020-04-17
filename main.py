#!/usr/bin/env python
import random
import tcod
from elements import library as el
from environment import environment_manager as em
import keyboard
import interface as ui
# Setup keyboard input
kb = keyboard.GameInput()

# Delete existing saved levels
em.delete_all()

# Create first environmentexit()
print('Creating starting level')
em.create()
# Setup player

player = el.player_character('Deckard', em.random_unblocked_loc())
em.entities.append(player)

while True:

    # TODO: roll initiative
    for e in em.entities:
        try:
            e.perform()
        except AttributeError:
            """ this entity has no personality """
