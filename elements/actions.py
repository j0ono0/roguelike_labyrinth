import random
import tcod
from settings import *
from user_interface import consoles
from user_interface.consoles import root_console as console
from . import entity
from user_interface import interfaces as ui
from user_interface import keyboard
import pathfinding as pf
import field_of_view
import dungeon_master as dm


class Interact:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self, target):
        ui.narrative.add("{} interacts with {}".format(self.parent.name, target.name))
        

class BlockTarget:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self, target):
        ui.narrative.add("The {} does not move, that way is blocked".format(target.name))


class MoveTarget:
    def __init__(self, parent ,loc):
        self.loc = loc
    
    def __call__(self, target):
        target.loc.update(self.loc)


class MoveToLevel:
    def __init__(self, parent, env_id=None, return_entity=None):
        self.parent = parent
        self.env_id = env_id
        self.return_entity = return_entity

    def __call__(self, target):
        dm.save()
        
        try:
            dm.load(self.env_id)
            print(f'level {dm.terrain.id} loaded')
        except FileNotFoundError:
            print('Level not found. Creating new level')
            dm.create(self.parent.loc())
            if self.return_entity:
                self.return_entity.loc.update(self.parent.loc())
                dm.entities.append(self.return_entity)

        dm.entities.insert(0, target)
                

class DisplayEntity:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self, target):
        
        kb = keyboard.CharInput()
        
        narr = consoles.NarrativeConsole()
        narr.con.print_box(1, 1, NAR_WIDTH, NAR_HEIGHT, 'Type the symbol your seek.')
        narr.blit(True)
        
        char = kb.capture_keypress()

        narr.con.print_box(1, 1, NAR_WIDTH, NAR_HEIGHT, "You sense the device searching.")
        narr.blit()
        
        emap = consoles.TerrainConsole()

        entities = [e for e in dm.entities if e.glyph == char]
        for e in entities:
            path = dm.find_path(target.loc(), e.loc())
            for loc in path[1:]:
                emap.con.print(*loc, '.', [200,255,0])
            emap.con.print(*e.loc(), e.glyph, e.fg)
        
        emap.blit(True)
            
        # Pause before returning to game loop
        char = kb.capture_keypress()

class FleeMap:
    def __init__(self, parent):
        self.parent = parent

    # Temporarly renders a contigueous section of map around parent.
    def __call__(self, target):
        emap = consoles.TerrainConsole()
        graph = dm.terrain.motionmap
        costmap = pf.dijkstra(graph, {self.parent.loc(): 0})[1]
        # Reverse movement costs so entity flees starting points
        # Recalculate Dijkstra algorithm
        costmap = {key:value * -1.175 for (key, value) in costmap.items()}
        resistance_map = pf.dijkstra(graph, costmap)[1]
        
        # transpose value range to 0 to 255
        vmax = 0
        vmin = 0
        for key, val in resistance_map.items():
            if val > vmax:
                vmax = val
            elif val < vmin:
                vmin = val
        # Multiplier for fleeing
        vmax = vmax + abs(vmin)
        for key, val in resistance_map.items():
            val = val + abs(vmin)
            r = int(val / vmax * 255)
            g = int( max(0, val / vmax - 0.5) * 255)
            b = int((vmax - val) / vmax * 255)
            emap.con.draw_rect(*key, 1, 1, 0, bg=[r, g, b])

        emap.blit(True)
        keyboard.CharInput().capture_keypress()


class Defend:
    def __init__(self, parent):
        self.parent = parent

    # Temporarly renders a contigueous section of map around parent.
    def __call__(self, target):
        """ DEFEND """
        self.parent.life.damage(1)
        ui.narrative.add(f"{target} inflicts 1pt of damage on {self.parent}.")
        
    
################################################


class PersonalityA:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self):
        fov = field_of_view.scan(self.parent.loc(), dm.terrain.sightmap, 6)
        foes = [e for e in dm.entities if e.loc() in fov and e.life() and e.life.personality != self.parent.life.personality]
        try:
            foe = foes[0]
        except IndexError:
            """ No foes are in range """ 
            return

        if self.parent.life.current > 2:
            """ ATTACK """
            path = dm.find_path(self.parent.loc(), foe.loc())
            target = dm.get_target(path.pop(), True)

        else:
            """ FLEE """
            resistance_map = pf.dijkstra(dm.terrain.motionmap, {foe.loc(): 0})[1]
            # Reverse movement costs so entity flees starting points
            # Recalculate Dijkstra algorithm
            resistance_map = {key:value * -1.175 for (key, value) in resistance_map.items()}
            paths = pf.dijkstra(dm.terrain.motionmap, resistance_map)[0]
            loc = paths[self.parent.loc()]
            target = dm.get_target(loc, True)
            print('fleeing ', target.kind)
        
        try:
            target.action(self.parent)
        except AttributeError:
            ui.narrative.add('The {} needs less haste and more speed.'.format(target.kind))
            



class PlayerInput:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self):

        # Process player's input
        fn, args = keyboard.GameInput().capture_keypress()

        # Clear messages in narrative display
        ui.narrative.archive()

        try:
            fn(self.parent, args)
        except TypeError as e:
            print('The keyboard cmd does not have a function:', e)

        # update player field of view
        self.parent.percept.see(dm.terrain.sightmap)
        dm.terrain.mark_as_seen(self.parent.percept.fov)
        