import random
import tcod
from settings import *
from user_interface import consoles
from user_interface import keyboard
from user_interface.consoles import root_console as console
from user_interface import interfaces as ui
import pathfinding as pf
import field_of_view
from line_of_sight import LineOfSight as los


def interact(dm, parent, args):
    ui.narrative.add("{} interacts with {}".format(self.parent.name, target.name))


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
        # target has not moved loc so needs forced fov update
        target.percept.look(dm.terrain)
        dm.entities.append(target)



def display_entity_type(weilder, dm):
    
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
        path = dm.find_path(weilder.loc(), e.loc())
        for loc in path[1:]:
            emap.con.print(*loc, '.', [200,255,0])
        emap.con.print(*e.loc(), e.glyph, e.fg)
    
    emap.blit(True)
        
    # Pause before returning to game loop
    char = kb.capture_keypress()


# Temporarly renders a contigueous section of map around parent.
def flee_map(target, dm):
    emap = consoles.TerrainConsole()
    graph = dm.terrain.motionmap
    costmap = pf.dijkstra(graph, {target.loc(): 0})[1]
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


def block_path(dm, parent, other):
    ui.narrative.add(f'the {parent} blocks {other}.')

def target_select(dm, parent, args):
    kb = keyboard.TargetInput()
    loc = parent.loc()
    seen_tiles = [(x, y) for x in range(MAP_WIDTH) for y in range(MAP_HEIGHT) if dm.terrain.tiles[x][y].seen == True]
    
    display = consoles.EntityConsole()
    label = consoles.LabelConsole()
    
    while True:
        label.update('')
        if loc in seen_tiles:
            try:
                entities = [e for e in dm.entities if e.loc() == loc]
                glyph = entities[0].glyph
                if len(entities) > 7:
                    txt = '{} and many other items.'.format(entities[0])
                elif len(entities) > 1:
                    txt = '{} and a few other items.'.format(entities[0])
                else:
                    txt = '{}.'.format(entities[0])

                label.update(txt)
                
            except IndexError:
                """ No entities are at this location """
                x, y = loc
                txt = dm.terrain.tiles[x][y].name
                glyph = dm.terrain.tiles[x][y].glyph
                

            fg = [0,0,0]
            bg = [255,255,255]

        else:
            glyph = ' '
            fg = [0,0,0]
            bg = [120,120,120]

        display.con.print(0, 0, glyph, fg, bg)
        
        # Update screen
        dm.render_game()
        label.blit(loc)
        display.blit(loc, True)
        
        
        # Wait for keypress
        fn, args = kb.capture_keypress()
        if fn == 'target':
            loc = tuple([a+b for (a, b) in zip(loc, args)])
        else:
            return loc