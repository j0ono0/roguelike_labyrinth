#################################################
#
#   Keyboard input
#
#################################################
import tcod
from settings import *

class InputHandler:
    def capture_keypress(self):
        # Wait for a key stroke
        for event in tcod.event.wait():
        
        # Return content from keymap
            if event.type == 'KEYDOWN':
                try:
                    return self.keymap[event.sym]
                except KeyError as e:
                    print('key not registered.', e)

            elif event.type == 'QUIT':
                # Halt the script using SystemExit
                raise SystemExit('The window has been closed.')

            return (None, None, None)


class GameInput(InputHandler): 
    def __init__(self):
        self.keymap = {
            # Arrowkeys
            tcod.event.K_UP: ('move',[0,-1],{}),
            tcod.event.K_LEFT: ('move',[-1,0],{}),
            tcod.event.K_RIGHT: ('move',[1,0],{}),
            tcod.event.K_DOWN: ('move',[0,1],{}),
            # Numpad
            tcod.event.K_KP_9: ('move',[1,-1],{}),
            tcod.event.K_KP_8: ('move',[0,-1],{}),
            tcod.event.K_KP_7: ('move',[-1,-1],{}),
            tcod.event.K_KP_6: ('move',[1,0],{}),
            #tcod.event.K_KP_5: 5 on numpad
            tcod.event.K_KP_4: ('move',[-1,0],{}),
            tcod.event.K_KP_3: ('move',[1,1],{}),
            tcod.event.K_KP_2: ('move',[0,1],{}),
            tcod.event.K_KP_1: ('move',[-1,1],{}),
            #tcod.event.K_KP_0: 0 on numpad
        
            tcod.event.K_ESCAPE:  ('application_menu',[],{}),
            tcod.event.K_COMMA:  ('pickup_select',[],{}),
            tcod.event.K_PERIOD:  ('look',[],{}),
            tcod.event.K_a:  ('action_select',[],{}),
            tcod.event.K_d: ('drop_select',[],{}),
            #tcod.event.K_i: ('use',['inventory'],{}),
            tcod.event.K_o: ('operate',[],{}),
            tcod.event.K_r: ('replay',[],{}),
            tcod.event.K_t: ('targeting',[],{}),
            tcod.event.K_u: ('use',[],{}),
            tcod.event.K_w: ('wield',[],{}),
        }


class MenuInput(InputHandler): 
    def __init__(self):
        self.vk = {
            # Arrowkeys
            14: ('move',[-1],{}),      # up
            15: ('move',[-1],{}),      # left
            16: ('move', [1],{}),      # right
            17: ('move', [1],{}),      # down
            # Numpad
            #35: 0 on numpad
            36: ('move', [1],{}),           # down
            38: ('move',[-1],{}),           # left
            39: ('call_selected',[],{}),    # 5 numpad
            40: ('move', [1],{}),           # right
            42: ('move',[-1],{}),           # up
            49: ('call_selected',[],{}),    # enter (numpad)
        }
        self.c = {
            13: ('call_selected',[],{}),    # enter (main)
            27: ('exit',[],{}),             # esc
        }    


class TargetInput(InputHandler):
    def __init__(self):
        self.vk = {
            # Arrowkeys
            14: ('move_cursor',[0,-1],{}),     # up
            15: ('move_cursor',[-1,0],{}),     # left
            16: ('move_cursor',[1,0],{}),      # right
            17: ('move_cursor',[0,1],{}),      # down
            # Numpad
            43: ('move_cursor',[1,-1],{}),     # up right
            42: ('move_cursor',[0,-1],{}),     # up
            41: ('move_cursor',[-1,-1],{}),    # up left
            40: ('move_cursor',[1,0],{}),      # right
            39: ('select',[],{}),              # 5 numpad
            38: ('move_cursor',[-1,0],{}),     # left
            37: ('move_cursor',[1,1],{}),      # down right
            36: ('move_cursor',[0,1],{}),      # down
            35: ('move_cursor',[-1,1],{}),     # down left
            49: ('select',[],{}),              # enter (numpad)
            #35: 0 on numpad
        }
        self.c = {
            13: ('select',[],{}),  # enter (main)
            27: ('exit',[],{}),  # esc
        }

class DirectionInput(InputHandler):
        def __init__(self):
            self.vk = {
                14: ('use_direction',[0,-1],{}),     # up
                15: ('use_direction',[-1,0],{}),     # left
                16: ('use_direction',[1,0],{}),      # right
                17: ('use_direction',[0,1],{}),      # down
                # Numpad
                43: ('use_direction',[1,-1],{}),     # up right
                42: ('use_direction',[0,-1],{}),     # up
                41: ('use_direction',[-1,-1],{}),    # up left
                40: ('use_direction',[1,0],{}),      # right
                38: ('use_direction',[-1,0],{}),     # left
                37: ('use_direction',[1,1],{}),      # down right
                36: ('use_direction',[0,1],{}),      # down
                35: ('use_direction',[-1,1],{}),     # down left
            }

class alphaInput(InputHandler):
    def __init__(self):
        self.vk = {
            49: ('select',[],{}),           # enter (numpad)
        }
        self.c = {
            27:  ('yes', [], {}),       # esc
            44:  (',', [], {}),         # ,
            46:  ('.', [], {}),         # .
            100: ('d', [], {}),         # d
            105: ('i', [], {}),         # i
            110: ('n', [], {}),         # n
            114: ('r', [], {}),         # r
            116: ('t', [], {}),         # t
            117: ('u', [], {}),         # u
            121: ('y', [], {}),         # y
        }