"""

Dashboard interface components

"""
from collections import deque
import tcod
import keyboard
from settings import *


class NarrativeConsole:
    def __init__(self):
        self.history = deque(['Monkey was born form a stone egg.'],100)
        self.queue = [
            "Welcome to roguelike!",
            "Progress has been slow due to having to babysit my little one constantly. The days I get off I still seem to be spending quite some time dadding.",
            "'u' use item.",
            "',' pickup item.",
            "'d' drop item.",
        ]
        self.con = tcod.console.Console(NAR_WIDTH+2, NAR_HEIGHT+2, order="F")

    def add(self, msg):
        self.queue.append(msg)

    def blit(self, console):
        y = 0
        con = tcod.console.Console(NAR_WIDTH, NAR_HEIGHT)
        while self.queue:
            y = y + 1 + con.print_box(1, y, NAR_WIDTH-1, NAR_HEIGHT, self.queue[0])
            self.history.appendleft(self.queue.pop(0))

        con.blit(console, *NAR_OFFSET, 0, 0, NAR_WIDTH+2, NAR_HEIGHT+2, 1, 0, 0)


class SelectMenu:
    """
    Display a list of option for a user to select from
    """
    def __init__(self, title, console):
        self.title = title
        self.console = console

    @staticmethod
    def move(index, direction, max_index):
        return max(0, min(index + direction, max_index))


    def select(self, options):
        
        con = tcod.console.Console(NAR_WIDTH, NAR_HEIGHT, order="F")
        kb = keyboard.MenuInput()
        index = 0
        selection = None
        
        while selection == None:
            
            con.print(1, 0, 'Inventory')
            y = 2
            for i, option in enumerate(options):
                if i == index:
                    fg = [0,0,0]
                    bg = [200,200,200]
                else:
                    fg = [255,255,255]
                    bg = [0,0,0]
                    
                y = y + con.print_box(1, y, NAR_WIDTH, 10, option.name, fg, bg)

            con.blit(self.console, *NAR_OFFSET)
            tcod.console_flush()
            
            fn, args, kwargs = kb.capture_keypress()
            if fn == 'move':
                index = self.move(index, args[0], len(options) - 1)
            elif fn == 'select':
                selection = options[index]
            elif fn == 'exit':
                break
            
        return selection

#################

narrative = NarrativeConsole()