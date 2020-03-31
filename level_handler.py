import os, pickle, re
import tcod
from levels import environment
from pathfinding import astar
from settings import *
from elements import library as el


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

def instantiate_env(env_id):
    """
    Save current level, 
    load requested level if it exists 
    otherwise create a new level
    """
    save()
    try:
        load(env_id)
        print(f'level {env.id} loaded')
    except FileNotFoundError:
        print('Level not found. Creating new level')
        create(MAP_WIDTH, MAP_HEIGHT)

def create(width, height):
    global env
    #find highest id in gamedata
    filenames = os.listdir('gamedata')
    p = re.compile(r'_(?P<id>\d+)\.')
    ids = [int(p.search(i).group('id')) for i in filenames]
    try:
        newid = max(ids) + 1
        env = environment.MazeMap(width, height, id=newid)
    except ValueError:
        newid = 1
        env = environment.BigRoom(width, height, id=newid)

    # Populate environment with some exits
    exit_up = el.stairs_up(newid)
    x,y = env.random_empty_loc()
    exit_down = el.stairs_down(newid+1, (x,y), exit_up)
    #env.entities.append(exit_down)
    env.tiles[x][y].inventory.add(exit_down)



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
    return [e for e in env.entities if e.glyph in ['<','>']]
    

def update_seen(vismap):
    for loc in vismap:
        x, y = loc
        env.tiles[x][y].seen = True


def get_target(loc, blocked=True):
    # Return entities (or tile) at location
    entities = [e for  e in env.entities if e.loc() == loc and e.blocked == blocked]
    if  len(entities) != 0:
        return entities[0]
    x, y = loc
    return env.tiles[x][y]

    
def find_path(start, end):
    return astar(env.tiles, start, end)


def render(fov):
    con = tcod.console.Console(env.width, env.height, order='F')
    # Add env tiles to console
    for x in range(MAP_WIDTH): 
        for y in range(MAP_HEIGHT):
            t = env.tiles[x][y]
            if (x,y) in fov:
                con.tiles[(x,y)] = (
                    ord(t.glyph),
                    (120, 120, 120, 255),
                    (*tcod.black, 255)
                )
            elif t.seen:
                con.tiles[(x,y)] = (
                    ord(t.glyph),
                    (60, 60, 60, 255),
                    (*tcod.black, 255)
                )
            
    # Add entities to console
    for en in env.entities:
        if en.loc() in fov:
            con.print_(*en.loc(), en.glyph)

    return con

