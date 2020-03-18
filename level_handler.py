import os, pickle, re
from levels import environment
from entity import Entity
from levels import field_of_view as fov 
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
    global env
    #find highest id in gamedata
    filenames = os.listdir('gamedata')
    p = re.compile(r'_(?P<id>\d+)\.')
    ids = [int(p.search(i).group('id')) for i in filenames]
    try:
        newid = max(ids) + 1
    except ValueError:
        newid = 1
    env = environment.MazeMap(width, height, id=newid)


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
    env.entities.append(Entity(label, glyph, loc, RelocateUser(loc, id)))


def update_fov(loc):
    vismap = {k: t.blocked==False for (k, t) in env.tiles.items()}
    vis_tiles = fov.scan(loc, vismap, 16)
    for k, v in env.tiles.items():
        if k in vis_tiles:
            v.visible = True
            v.seen = True
        else:
            v.visible = False

def update_entity_fov(e):
    vismap = {k: t.blocked==False for (k, t) in env.tiles.items()}
    e.fov = fov.scan(e.loc(), vismap, e.fov_max)

class RelocateUser:
    global env
    def __init__(self, loc, dest_id):
        self.loc = loc
        self.dest_id = dest_id

    def __call__(self, user):
        print('relocation triggered.')
        user.loc.set(*self.loc)
        save()
        try:
            load(self.dest_id)
            print(f'level {env.id} loaded')
        except FileNotFoundError:
            print('Level not found. Creating new level')
            create(MAP_WIDTH, MAP_HEIGHT)
            add_exit(self.loc, self.dest_id - 1)
            add_exit(env.random_empty_loc(), self.dest_id + 1)
        update_fov(user.loc())