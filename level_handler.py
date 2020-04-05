import os, pickle, re
import tcod
import consoles
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
    stairs_up = el.stairs_up(newid)
    stairs_down = el.stairs_down(newid+1, env.random_empty_loc(), stairs_up)
    # Populate environment with some items
    locator = el.locator(env.random_empty_loc())
    person = el.human('Jaffles', 'human')

    env.entities.extend([stairs_down, locator])


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


def get_target(loc, blocked=False):
    # Return first item (or tile) at location
    return next(iter([e for e in env.entities if e.loc() == loc and e.blocked == blocked]), get_tile(loc))

def get_tile(loc):
    x, y = loc
    return env.tiles[x][y]
    
def find_path(start, end):
    return astar(env.fov_array(), start, end)


def blit(fov):
    disp = consoles.EnvironmentConsole()

    con = tcod.console.Console(env.width, env.height, order="F")
    # Add env tiles to console
    for x in range(MAP_WIDTH): 
        for y in range(MAP_HEIGHT):
            t = env.tiles[x][y]
            if (x,y) in fov:
                disp.con.tiles[(x,y)] = (
                    ord(ELEMENTS[t.kind].glyph),
                    t.fg + [255],
                    [8, 8, 8, 255]
                )
            elif t.seen:
                key = t.kind + '--unseen'
                disp.con.tiles[(x,y)] = (
                    ord(ELEMENTS[key].glyph),
                    ELEMENTS[key].color + [150],
                    (*tcod.black, 255)
                )
            
    # Add entities to console
    for e in env.entities:
        if e.loc() in fov:
            disp.con.print_(*e.loc(), e.glyph)

    disp.blit()

