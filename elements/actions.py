import tcod
from settings import *
import consoles
from consoles import root_console as console
from . import entity
import interface as ui
import keyboard
from pathfinding import dijkstra


class Interact:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self, target, lvl):
        ui.narrative.add("{} interacts with {}".format(self.parent.name, target.name))
        

class BlockTarget:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self, target, lvl):
        ui.narrative.add("The {} does not move, that way is blocked".format(target.name))


class MoveToLoc:
    def __init__(self, parent ,loc):
        self.loc = loc
    
    def __call__(self, target, lvl):
        target.loc.update(self.loc)


class MoveToLevel:
    def __init__(self, parent, env_id=None, return_entity=None):
        self.parent = parent
        self.env_id = env_id
        self.return_entity = return_entity

    def __call__(self, target, lvl):
        lvl.save()
        
        try:
            lvl.load(self.env_id)
            print(f'level {lvl.env.id} loaded')
        except FileNotFoundError:
            print('Level not found. Creating new level')
            lvl.create(MAP_WIDTH, MAP_HEIGHT, self.parent.loc())
            if self.return_entity:
                self.return_entity.loc.update(self.parent.loc())
                lvl.env.entities.append(self.return_entity)
        
        lvl.env.entities.append(target)
                

class DisplayEntity:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self, target, lvl):
        
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
            path = lvl.find_path(target.loc(), e.loc())
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
    def __call__(self, target, lvl):
        kb = keyboard.CharInput()
        emap = consoles.EnvironmentConsole()
        graph = lvl.env.unblocked_tiles()
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
    def __call__(self, target, lvl):
        graph = lvl.env.unblocked_tiles()
        resistance_map = dijkstra(graph, {target.loc(): 0})[1]
        # Reverse movement costs so entity flees starting points
        # Recalculate Dijkstra algorithm
        resistance_map = {key:value * -1.175 for (key, value) in resistance_map.items()}
        paths = dijkstra(graph, resistance_map)[0]
        
        loc = paths[self.parent.loc()]
        target = lvl.get_target(loc, True)
        try:
            target.action(self.parent, lvl)
        except AttributeError:
            ui.narrative.add('The {} needs less haste and more speed.'.format(target.kind))
        

    

################################################

class PersonalityA:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self, lvl):
        
        # TODO: stop from walking through blocking entities

        if len(self.path) > 0:
            loc = self.path.pop()
            target = lvl.get_target(loc, True)
            try:
                target.action(self.parent, target, lvl)
            except AttributeError:
                ui.narrative.add('A {} blocks the {}\'s way.'.format(target.kind, self.parent.kind))
            
            # replace loc if entity was unable to move
            if self.parent.loc() != loc:
                self.path.append(loc)

    def flee(self, target, lvl):
        ui.narrative.add('The {} menaces a {}'.format(self.parent.kind, target.kind))
        ui.narrative.add('The {} flees!'.format(target.kind))
        FleeTarget()(self.parent, target, lvl)
        #self.path = lvl.find_path(target.loc(), lvl.env.random_empty_loc())


class PlayerInput:
    def __init__(self, parent):
        self.parent = parent

    def __call__(self, lvl):

        # update player field of view
        self.parent.percept.see(lvl.env.fov_array())
        lvl.update_seen(self.parent.percept.fov)
        
        # Render game to screen
        console.clear()
        consoles.render_base()
        
        lvl.blit(self.parent.percept.fov)
        ui.narrative.blit()
        console.print(*(x + y for x, y in zip(MAP_OFFSET, self.parent.loc())), self.parent.glyph, self.parent.fg)
        
        tcod.console_flush()

        kb = keyboard.GameInput()
        # Process player's input
        fn, args, kwargs = kb.capture_keypress()
        if fn == 'move':
            try:
                loc = self.parent.loc.proposed(args)
                target = lvl.get_target(loc, True)
                try:
                    target.action(self.parent, lvl)
                except AttributeError as e:
                    print(e)
                    ui.narrative.add('The {} blocks your way.'.format(target.name))
            except IndexError as e:
                # Player reached edge of environment
                ui.narrative.add('There is no way through here!')

        elif fn == 'use':
            menu = ui.SelectMenu('Inventory')
            target = menu.select(self.parent.inventory.items) or lvl.get_target(self.parent.loc())
            
            # TODO enable player initiated use of items on ground
            
            try:
                target.action(self.parent, lvl)
            except AttributeError as e:
                ui.narrative.add('You see no way to use the {}.'.format(target.name))

        elif fn == 'pickup_select':
            targets = [t for t in lvl.env.entities if t.loc() == self.parent.loc() and t != self.parent]
            if len(targets) > 1:
                """ display select menu here """
            elif len(targets) == 1:
                self.parent.inventory.pickup(targets.pop(), lvl)
            else:
                ui.narrative.add('There is nothing here to pickup.')

        elif fn == 'drop_select':
            menu = ui.SelectMenu('Inventory')
            target = menu.select(self.parent.inventory.items)
            self.parent.inventory.drop(target, lvl)
