#!/usr/bin/env python

from elements import library as el
import dungeon_master as dm
from user_interface import interfaces as ui



# Delete existing saved levels
dm.delete_all()

# Create first environmentexit()
print('Creating starting level')
dm.create()
# Setup player

player = el.player_character('Deckard', dm.random_unblocked_loc())
# update player field of view
player.percept.see(dm.terrain.field_of_view())
dm.terrain.mark_as_seen(player.percept.fov)

dm.entities.append(player)
ui.player_display.c = player

# Initial render of screen
dm.render_game(player.percept.fov)

while True:

    # TODO: roll initiative
    for e in dm.entities:

        # Entities perform in turn
        try:
            e.perform()
        except AttributeError:
            """ this entity has no personality """
        
        # Rerender after each turn
        dm.render_game(player.percept.fov)

