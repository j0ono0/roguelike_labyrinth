import os, pickle, re
from levels import environment
from entity import Entity

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