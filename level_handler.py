import os, pickle, re
import tcod
from levels import environment
import entity
from levels import field_of_view as fov 
from pathfinding import astar
from settings import *

#################
# Module variables
lvl_prefix = 'env_'
env = None

#################


def delete_all():
    levels = [n for n in os.listdir('gamedata') if n[:len(lvl_prefix)] == lvl_prefix]
    for filename in levels:
        path = os.path.join('gamedata', filename)
        os.remove(path)


def create(width, height):
    global env, tiles
    #find highest id in gamedata
    filenames = os.listdir('gamedata')
    p = re.compile(r'_(?P<id>\d+)\.')
    ids = [int(p.search(i).group('id')) for i in filenames]
    try:
        newid = max(ids) + 1
    except ValueError:
        newid = 1
    env = environment.MazeMap(width, height, id=newid)
    # Populate environment with entities
    add_exit(env.random_unblocked_loc(), env.id + 1)


def load(id):
    global env
    filepath = os.path.join('gamedata', f'{lvl_prefix}{id}.pickle')
    with open(filepath, 'rb') as f:
        env = pickle.load(f)
    

def save():
    filepath = os.path.join('gamedata', f'{lvl_prefix}{env.id}.pickle')
    with open(filepath, 'wb') as f:
        pickle.dump(env, f)
    print(f'enviroment for level {env.id} saved.')
    

def exits():
    lst = [e for e in env.entities if e.glyph in ['<','>'] and e.action.dest_id]
    return sorted(lst, key = lambda e: e.action.dest_id)


def update_seen(vismap):
    for loc in vismap:
        env.tiles[loc].seen = True


def add_exit(loc=None, id=None):
    global env
    loc = loc or env.random_empty_loc()
    id = id or env.id
    if id >= env.id:
        glyph = '>'
        label = 'Exit down'
    else:
        glyph = '<'
        label = 'Exit up'
    env.entities.append(entity.Entity(label, glyph, loc, Relocate(loc, id)))

def find_path(start, end):
    return astar(env.tiles, start, end)

def render(fov):
    con = tcod.console.Console(env.width, env.height, order='F')
    # Add env tiles to console
    for k, t in env.tiles.items():
        if k in fov:
            con.tiles[k] = (
                ord(t.glyph),
                (120, 120, 120, 255),
                (*tcod.black, 255)
            )
        elif t.seen:
            con.tiles[k] = (
                ord(t.glyph),
                (60, 60, 60, 255),
                (*tcod.black, 255)
            )
    # Add entities to console
    for en in env.entities:
        if en.loc() in fov:
            con.print_(*en.loc(), en.glyph)

    return con


class Relocate:
    global env
    def __init__(self, loc, dest_id):
        self.loc = loc
        self.dest_id = dest_id

    def __call__(self, entity):
        print('Transportation triggered.')
        entity.loc.set(*self.loc)
        save()
        try:
            load(self.dest_id)
            print(f'level {env.id} loaded')
        except FileNotFoundError:
            print('Level not found. Creating new level')
            create(MAP_WIDTH, MAP_HEIGHT)
            add_exit(self.loc, self.dest_id - 1)
