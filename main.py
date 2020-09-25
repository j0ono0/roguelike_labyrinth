#!/usr/bin/env python

import dungeon_master as dm
from user_interface import interfaces as ui
from user_interface import keyboard


###################################
dm2 = dm.DungeonMaster()

while dm2.pc.life():

    dm2.progress_game()
        

print('the game is over. The player character is dead beyond repair.')
print('press a key to exit.')
keyboard.CharInput().capture_keypress()


###################################
"""
# Delete existing saved levels
dm.delete_all()

# Create player character
dm.create_pc('Dekard')

# Create first environmentexit()
print('Creating starting level')
dm.create(dm.pc.loc())


# update player field of view
dm.pc.percept.look(dm.terrain)
dm.terrain.mark_as_seen(dm.pc.percept.fov)

dm.entities.append(dm.pc)

# Assign player to display and do initial render of screen
dm.render_game()


while dm.pc.life():

    # TODO: roll initiative
    for e in dm.entities:

        # Entities perform in turn
        try:
            e.perform()
            # Rerender after each turn
            dm.render_game()
        except AttributeError:
            #this entity has no personality
            pass
        

print('the game is over. The player character is dead beyond repair.')
print('press a key to exit.')
keyboard.CharInput().capture_keypress()
"""