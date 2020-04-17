#################################################
#
#   Keyboard input
#
#################################################
import tcod
from settings import *

mod_keys = {
    '1':'!',
    '2':'@',
    '3':'#',
    '4':'$',
    '5':'%',
    '6':'^',
    '7':'&',
    '8':'*',
    '9':'(',
    '0':')',
    '-':'_',
    '=':'+',
    '[':'{',
    ']':'}',
    '\\':'|',
    ';':':',
    "'":'"',
    ',':'<',
    '.':'>',
    '/':'?',
}

class InputHandler:
    def capture_keypress(self):
        while True:
            # Wait for a key stroke
            for event in tcod.event.wait():
            
            # Return content from keymap
                if event.type == 'KEYDOWN':
                    try:
                        return self.keymap[event.sym]
                    except KeyError as e:
                        print('key not registered.', e)
                        return (None, None)

                elif event.type == 'QUIT':
                    # Halt the script using SystemExit
                    raise SystemExit('The window has been closed.')

class CharInput:
    def capture_keypress(self):
        while True:
            # Wait for a key stroke
            for event in tcod.event.wait():
                # Return keyboard character
                if event.type == 'KEYDOWN':
                    try:
                        if event.mod & tcod.event.KMOD_SHIFT:
                            return mod_keys.get(chr(event.sym), chr(event.sym).upper())
                        return chr(event.sym)
                    except ValueError:
                        pass
                    
                elif event.type == 'QUIT':
                    # Halt the script using SystemExit
                    raise SystemExit('The window has been closed.')



class GameInput(InputHandler): 
    def __init__(self):
        self.keymap = {
            # Arrowkeys
            tcod.event.K_UP: ('move',[0,-1]),
            tcod.event.K_LEFT: ('move',[-1,0]),
            tcod.event.K_RIGHT: ('move',[1,0]),
            tcod.event.K_DOWN: ('move',[0,1]),
            # Numpad
            tcod.event.K_KP_9: ('move',[1,-1]),
            tcod.event.K_KP_8: ('move',[0,-1]),
            tcod.event.K_KP_7: ('move',[-1,-1]),
            tcod.event.K_KP_6: ('move',[1,0]),
            #tcod.event.K_KP_5: 5 on numpad
            tcod.event.K_KP_4: ('move',[-1,0]),
            tcod.event.K_KP_3: ('move',[1,1]),
            tcod.event.K_KP_2: ('move',[0,1]),
            tcod.event.K_KP_1: ('move',[-1,1]),
            #tcod.event.K_KP_0: 0 on numpad
        
            tcod.event.K_ESCAPE:  ('application_menu',[]),
            tcod.event.K_COMMA:  ('pickup_select',[]),
            tcod.event.K_PERIOD:  ('look',[]),
            tcod.event.K_a:  ('action_select',[]),
            tcod.event.K_d: ('drop_select',[]),
            tcod.event.K_h: ('help',[]),
            #tcod.event.K_i: ('use',['inventory']),
            tcod.event.K_o: ('operate',[]),
            tcod.event.K_r: ('replay',[]),
            tcod.event.K_t: ('targeting',[]),
            tcod.event.K_u: ('use',[]),
            tcod.event.K_w: ('wield',[]),
        }


class MenuInput(InputHandler): 
    def __init__(self):
        self.keymap = {
            # Arrowkeys
            tcod.event.K_UP: ('move',[-1]),
            tcod.event.K_LEFT: ('move',[-1]),
            tcod.event.K_RIGHT: ('move',[1]),
            tcod.event.K_DOWN: ('move',[1]),
            # Numpad
            tcod.event.K_KP_9: ('move',[-1]),
            tcod.event.K_KP_8: ('move',[-1]),
            tcod.event.K_KP_7: ('move',[-1]),
            tcod.event.K_KP_6: ('move',[1]),
            tcod.event.K_KP_5: ('select',[]),
            tcod.event.K_KP_4: ('move',[-1]),
            tcod.event.K_KP_3: ('move',[1]),
            tcod.event.K_KP_2: ('move',[1]),
            tcod.event.K_KP_1: ('move',[1]),

            tcod.event.K_RETURN: ('select',[]),
            tcod.event.K_SPACE: ('select',[]),
            tcod.event.K_ESCAPE: ('exit',[]),
        }    


class TargetInput(InputHandler):
    def __init__(self):
        self.vk = {
            # Arrowkeys
            tcod.event.K_UP:    ('move',[0,-1]),
            tcod.event.K_LEFT:  ('move',[-1,0]),
            tcod.event.K_RIGHT: ('move',[1,0]),
            tcod.event.K_DOWN:  ('move',[0,1]),
            # Numpad
            tcod.event.K_KP_9:  ('move',[1,-1]),
            tcod.event.K_KP_8:  ('move',[0,-1]),
            tcod.event.K_KP_7:  ('move',[-1,-1]),
            tcod.event.K_KP_6:  ('move',[1,0]),
            tcod.event.K_KP_5:  ('select',[1,0]),
            tcod.event.K_KP_4:  ('move',[-1,0]),
            tcod.event.K_KP_3:  ('move',[1,1]),
            tcod.event.K_KP_2:  ('move',[0,1]),
            tcod.event.K_KP_1:  ('move',[-1,1]),
            # Keyboard
            tcod.event.K_RETURN: ('select',[]),
            tcod.event.K_SPACE:  ('select',[]),
            tcod.event.K_ESCAPE: ('exit',[]),
        }