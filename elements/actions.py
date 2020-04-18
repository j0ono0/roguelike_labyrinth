import tcod
from settings import *
import consoles
from consoles import root_console as console
from . import entity
import interface as ui
import keyboard
from pathfinding import dijkstra
from environment import environment_manager as em


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
        em.save()
        
        try:
            em.load(self.env_id)
            print(f'level {em.terrain.id} loaded')
        except FileNotFoundError:
            print('Level not found. Creating new level')
            em.create(self.parent.loc())
            if self.return_entity:
                self.return_entity.loc.update(self.parent.loc())
                em.entities.append(self.return_entity)

        em.entities.insert(0, target)
                

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

        entities = [e for e in em.entities if e.glyph == char]
        for e in entities:
            path = em.find_path(target.loc(), e.loc())
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
        kb = keyboard.CharInput()
        emap = consoles.TerrainConsole()
        graph = em.terrain.unblocked_tiles()
        costmap = dijkstra(graph, {self.parent.loc(): 0})[1]
        # Reverse movement costs so entity flees starting points
        # Recalculate Dijkstra algorithm
        costmap = {key:value * -1.175 for (key, value) in costmap.items()}
        influence_map, resistance_map = dijkstra(graph, costmap)
        
        
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
        kb.capture_keypress()


class FleeTarget:
    def __init__(self, parent):
        self.parent = parent

    # Temporarly renders a contigueous section of map around parent.
    def __call__(self, target):
        graph = em.terrain.unblocked_tiles()
        resistance_map = dijkstra(graph, {target.loc(): 0})[1]
        # Reverse movement costs so entity flees starting points
        # Recalculate Dijkstra algorithm
        resistance_map = {key:value * -1.175 for (key, value) in resistance_map.items()}
        paths = dijkstra(graph, resistance_map)[0]
        
        loc = paths[self.parent.loc()]
        target = em.get_target(loc, True)
        try:
            target.action(self.parent)
        except AttributeError:
            ui.narrative.add('The {} needs less haste and more speed.'.format(target.kind))
        

    

################################################

class PersonalityA:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self):
        
        # TODO: stop from walking through blocking entities

        if len(self.path) > 0:
            loc = self.path.pop()
            target = em.get_target(loc, True)
            try:
                target.action(self.parent)
            except AttributeError:
                ui.narrative.add('A {} blocks the {}\'s way.'.format(target.kind, self.parent.kind))
            
            # replace loc if entity was unable to move
            if self.parent.loc() != loc:
                self.path.append(loc)

class PlayerInput:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self):

        # update player field of view
        self.parent.percept.see(em.terrain.field_of_view())
        em.terrain.mark_as_seen(self.parent.percept.fov)
        
        # Render game to screen
        console.clear()
        consoles.render_base()
        
        em.blit(self.parent.percept.fov)
        ui.narrative.blit()
        console.print(*(x + y for x, y in zip(MAP_OFFSET, self.parent.loc())), self.parent.glyph, self.parent.fg)
        
        tcod.console_flush()

        # Process player's input
        fn, args = keyboard.GameInput().capture_keypress()
        try:
            fn(self.parent, args)
        except TypeError as e:
            print('The keyboard cmd does not have a function:', e)
        