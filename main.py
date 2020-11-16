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