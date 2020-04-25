import random
import bisect
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
import input_commands as cmd
from line_of_sight import LineOfSight as los


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


class RelocateTarget:
    """
    Move target to both new terrain and new location 
    """
    def __init__(self, parent, envid, coords):
        self.parent = parent
        self.envid = envid
        self.coords = coords
    
    def __call__(self, target):
        
        dm.save()
        
        try:
            dm.load(self.envid)
            print(f'level {dm.terrain.id} loaded')
        except FileNotFoundError:
            print('Level not found. Creating new level')
            dm.create(target.loc())

        target.loc.update(self.coords)
        dm.entities.append(target)


class RangeAttack: 
    def __init__(self, parent):
        self.parent = parent    
      
    def __call__(self, target):
        ui.narrative.add('You aim the gun...')
        loc = cmd.target_select(target, None)
        aim = los(target.loc(), loc)
        path = aim.path(map=dm.terrain.motionmap)
        ui.narrative.add('And dial distance;')
        ui.narrative.add('The gun kicks as charged metal crackles through the air.')

        for victim in [e for e in dm.entities if e.loc() in path and e != target]:
            try:
                victim.life.damage(random.randint(2,10))
            except AttributeError:
                ui.narrative.add(f'The {victim.name} smokes a little.')
                

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

    def __call__(self, target):
        """ DEFEND """
        self.parent.life.damage(1)
        if self.parent.life() == True:
            ui.narrative.add(f"{target} inflicts 1pt of damage on {self.parent}.")
        else:
            dm.entities.sort()
        

################################################
#
# Personalities: triggered from 'perform' attr
#
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
            
        if self.parent.life.current > 1:
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
        
        try:
            target.action(self.parent)
        except AttributeError:
            ui.narrative.add('The {} needs less haste and more speed.'.format(target.name))
            

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
        