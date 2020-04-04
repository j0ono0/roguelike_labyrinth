import tcod
from settings import *
from display import console
from . import entity
import interface as ui
import keyboard


class Interact:
    def __call__(self, user, target, lvl):
        ui.narrative.add("{} interacts with {}".format(user.name, target.name))
        

class BlockUser:
    def __call__(self, user, target, lvl):
        ui.narrative.add("The {} does not move, that way is blocked".format(target.name))


class MoveToLoc:
    def __init__(self, loc):
        self.loc = loc
    
    def __call__(self, user, target, lvl):
        user.loc.update(self.loc)


class MoveToLevel:
    def __init__(self, env_id, return_entity):
        self.env_id = env_id
        self.return_entity = return_entity

    def __call__(self, user, target, lvl):
        lvl.save()
        try:
            lvl.load(self.env_id)
            print(f'level {lvl.env.id} loaded')
        except FileNotFoundError:
            print('Level not found. Creating new level')
            lvl.create(MAP_WIDTH, MAP_HEIGHT)
            if self.return_entity:
                self.return_entity.loc.update(user.loc())
                lvl.env.entities.append(self.return_entity)
                

class DisplayEntity:
    def __call__(self, user, target, lvl):
        """
        # Print pathfinding
        for ex in lvl.exits():
            if ex.glyph == '>':
                color = [60,255,100]
                glyph = '.'
            else:
                color = [255,100,100]
                glyph = '.'
            
            for loc in lvl.find_path(player.loc(), ex.loc())[1:]:
                lvl_con.print(*loc, glyph, color)
        """
        ncon = tcod.console.Console(NAR_WIDTH, NAR_HEIGHT, order="F")
        kb = keyboard.CharInput()

        ncon.print_box(1, 1, NAR_WIDTH, NAR_HEIGHT, 'Type the symbol your seek.')
        ncon.blit(console, *NAR_OFFSET, 0, 0, NAR_WIDTH+2, NAR_HEIGHT+2, 1, 1, 0)
        tcod.console_flush()

        char = kb.capture_keypress()
        #ui.narrative.add("The device searches for all '{}'".format(char))
        #ui.narrative.add("Press a key to continue.")


        ncon.print_box(1, 1, NAR_WIDTH, NAR_HEIGHT, "You sense the device searching.")
        ncon.blit(console, *NAR_OFFSET, 0, 0, NAR_WIDTH+2, NAR_HEIGHT+2, 1, 1, 0)
        
        mcon = tcod.console.Console(MAP_WIDTH, MAP_HEIGHT, order="F")
        entities = [e for e in lvl.env.entities if e.glyph == char]
        for e in entities:
            for loc in lvl.find_path(user.loc(), e.loc())[1:]:
                mcon.print(*loc, '.', [200,255,0])
            mcon.print(*e.loc(), e.glyph, ELEMENTS[e.name].color)
        
        mcon.blit(console, *MAP_OFFSET, 0, 0, MAP_WIDTH+2, MAP_HEIGHT+2, 1, 0, 0)
        tcod.console_flush()
        
        # Pause before returning to game loop
        char = kb.capture_keypress()
        