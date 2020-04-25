"""

Dashboard interface components

"""
from collections import deque
import tcod
from user_interface import keyboard
from user_interface import consoles
from settings import *


class Narrative:
    def __init__(self):
        self.history = deque(['Monkey was born form a stone egg.'],100)
        self.queue = [
            "Welcome to roguelike!",
            "Progress has been slow due to having to babysit my little one constantly. The days I get off I still seem to be spending quite some time dadding.",
            "'u' use item.",
            "',' pickup item.",
            "'d' drop item.",
        ]

    def add(self, msg):
        self.queue.append(msg)

    def archive(self):
        while self.queue:
            self.history.appendleft(self.queue.pop(0))

    def blit(self):
        display = consoles.NarrativeConsole()
        display.clear()
        y = 0
        """
        while self.queue:
            y = y + 1 + display.con.print_box(1, y, NAR_WIDTH, NAR_HEIGHT, self.queue[0], [255, 255, 255], [0, 0, 0])
            self.history.appendleft(self.queue.pop(0))
        """
        for msg in self.queue:
            y = y + 1 + display.con.print_box(1, y, NAR_WIDTH, NAR_HEIGHT, msg, [255, 255, 255], [0, 0, 0])
        display.blit()


class SelectMenu:
    """
    Display a list of option for a user to select from
    """
    def __init__(self, title):
        self.title = title

    @staticmethod
    def move(index, direction, max_index):
        return max(0, min(index + direction, max_index))


    def select(self, options):
        
        # Resolve edge cases first
        if len(options) == 0:
            return None
        elif len(options) == 1:
            return options[0]
        
        display = consoles.NarrativeConsole()
        display.clear()

        kb = keyboard.MenuInput()
        index = 0
        selection = None
        
        while selection == None:
            
            display.con.print(1, 0, self.title)
            y = 2
            for i, option in enumerate(options):
                if i == index:
                    fg = [0,0,0]
                    bg = [200,200,200]
                else:
                    fg = [255,255,255]
                    bg = [0,0,0]
                    
                y = y + display.con.print_box(1, y, NAR_WIDTH, 10, option.__str__(), fg, bg)

            display.blit(True)
            
            fn, args = kb.capture_keypress()
            if fn == 'move':
                index = self.move(index, args[0], len(options) - 1)
            elif fn == 'select':
                selection = options[index]
            elif fn == 'exit':
                break
            
        return selection


def render_character_info(character):
    fg = [160,160,160]
    bg = [0,0,0]
    display = consoles.CharacterConsole()
    display.con.print(0,0, character.name, [0,0,0], [160,160,160])
    display.con.print(0,1, f"{character.life.current}/{character.life.max}", fg, bg)
    display.blit()


def render_game(entities, terrain, fov):
    display = consoles.TerrainConsole()

    # Add terrain tiles to console
    for x in range(MAP_WIDTH): 
        for y in range(MAP_HEIGHT):
            t = terrain.tiles[x][y]
            if (x,y) in fov:
                display.con.tiles[(x,y)] = (
                    ord(t.glyph),
                    t.fg + [255],
                    t.bg + [255]
                )
            elif t.seen:
                # Reduce color by 50% for unseen tiles
                fg = [c*.5 for c in t.fg]
                bg = [c*.5 for c in t.bg]
                display.con.tiles[(x,y)] = (
                    ord(t.glyph),
                    fg + [255],
                    bg + [255]
                )
            
    # Add entities to console
    for e in entities:
        if e.loc() in fov:
            display.con.print(*e.loc(), e.glyph, e.fg)

    display.blit()

#################
narrative = Narrative()