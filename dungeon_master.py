import os
import pickle
import re 
import random
import bisect

import tcod

from user_interface import consoles
from user_interface import interfaces as ui
from environment import terrain as terra
from environment import library as el
from environment import build
from pathfinding import astar
from settings import *



#################
# Module variables
entities = []
terrain = None
#################


def delete_all():
    levels = [n for n in os.listdir('gamedata') if n[:len(LEVEL_PREFIX)] == LEVEL_PREFIX]
    for filename in levels:
        path = os.path.join('gamedata', filename)
        os.remove(path)

def create(entry_loc=None):
    global entities, terrain
    
    #find highest id in gamedata
    filenames = os.listdir('gamedata')
    p = re.compile(r'_(?P<id>\d+)\.')
    ids = [int(p.search(i).group('id')) for i in filenames]
    try:
        envid = max(ids) + 1
    except ValueError:
        envid = 1

    entities, terrain = build.environment(envid, entry_loc)


def load(id):
    global entities, terrain
    filepath = os.path.join('gamedata', f'{LEVEL_PREFIX}{id}.pickle')
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    terrain = data['environment']
    entities = data['entities']

def save():
    # remove player character(s) before saving
    game = {
        'environment': terrain,
        #'entities': [e for e in entities if e.kind != 'player character']
        'entities': entities
    }

    filepath = os.path.join('gamedata', f'{LEVEL_PREFIX}{terrain.id}.pickle')
    with open(filepath, 'wb') as f:
        pickle.dump(game, f)
    print(f'game environment {terrain.id} saved')


def blit(fov):
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


def render_game(fov):
        # Render updated interfaces to screen
        consoles.root_console.clear()
        consoles.render_base()
        
        ui.player_display.blit()
        ui.narrative.blit()
        blit(fov)
        
        tcod.console_flush()



def get_target(loc, block_motion=False):
    # Return first item (or tile) at location
    if block_motion == True:
        return next(iter([e for e in entities if e.loc() == loc and e.block.motion == True]), terrain.get_tile(loc))
    return next(iter([e for e in entities if e.loc() == loc]), terrain.get_tile(loc))
    

def find_path(start, end):
    return astar(terrain.sightmap, start, end)


def random_empty_loc():
    entity_locs = set([e.loc for  e in entities])
    unblocked_locs = set([(x, y) for x in range(MAP_WIDTH) for y in range(MAP_HEIGHT) if (terrain.tiles[x][y].block.motion == False)])
    return random.choice(list(unblocked_locs.difference(entity_locs)))


def random_unblocked_loc():
    return random.choice([(x, y) for x in range(MAP_WIDTH) for y in range(MAP_HEIGHT) if (terrain.tiles[x][y].block.motion == False)])
