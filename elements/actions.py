import tcod
from settings import *
import consoles
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
        
        kb = keyboard.CharInput()
        
        narr = consoles.NarrativeConsole()
        narr.con.print_box(1, 1, NAR_WIDTH, NAR_HEIGHT, 'Type the symbol your seek.')
        narr.blit(True)
        
        char = kb.capture_keypress()

        narr.con.print_box(1, 1, NAR_WIDTH, NAR_HEIGHT, "You sense the device searching.")
        narr.blit()
        
        emap = consoles.EnvironmentConsole()

        entities = [e for e in lvl.env.entities if e.glyph == char]
        for e in entities:
            for loc in lvl.find_path(user.loc(), e.loc())[1:]:
                emap.con.print(*loc, '.', [200,255,0])
            emap.con.print(*e.loc(), e.glyph, e.fg)
        
        emap.blit(True)
        
        # Pause before returning to game loop
        char = kb.capture_keypress()
        
