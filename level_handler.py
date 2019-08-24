import os, pickle, re
from levels import environment
from entity import Entity

#################
# Constants
MAP_WIDTH = 15
MAP_HEIGHT = 15

#################
# Module variables
env = None

#################

def change(id):
    save()
    try:
        load(id)
    except FileNotFoundError:
        print('Level not found. Creating new level')
        create()

def create():
    global env
    #find highest id in gamedata
    filenames = os.listdir('gamedata')
    p = re.compile(r'_(?P<id>\d+)\.')
    ids = [int(p.search(i).group('id')) for i in filenames]
    try:
        newid = max(ids) + 1
    except ValueError:
        newid = 0
    env = environment.MazeMap(MAP_WIDTH, MAP_HEIGHT, id=newid)

def load(id):
    global env
    filepath = os.path.join('gamedata', f'env_{id}.pickle')
    with open(filepath, 'rb') as f:
        env = pickle.load(f)
    
def save():
    filepath = os.path.join('gamedata', f'env_{env.id}.pickle')
    with open(filepath, 'wb') as f:
        pickle.dump(env, f)
    print(f'enviroment for level {env.id} saved.')
    