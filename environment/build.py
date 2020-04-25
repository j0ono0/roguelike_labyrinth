"""

Build terrain and populate with entities

"""
import bisect
import random
from settings import MAP_HEIGHT, MAP_WIDTH
from . import terrain as t
from . import library as el
from . import entity



def environment(envid, entry_loc):
    
    ######################################
    # Select and init terrain
    ######################################
    
    if envid < 4:
        terrain = t.BasicDungeon(envid)
    elif envid < 5:
        terrain = t.MazeMap(envid)
    else:
        terrain = t.BigRoom(envid)

    terrain.build(entry_loc)
    
    ######################################
    # Create entities and place in terrain
    ######################################
    
    entities = []
    
    vacant_locs = terrain.unblocked_tiles()
    random.shuffle(vacant_locs)
    
    # Create and place entities
    if envid > 1:
        exit_up = el.stairs_up(entry_loc, terrain.id-1)
        bisect.insort_left(entities, exit_up)
    
    
    if envid < 6:
        exit_down = el.stairs_down(vacant_locs.pop(), terrain.id+1)
        bisect.insort_left(entities, exit_down)

    radar = el.radar(vacant_locs.pop())
    bisect.insort_left(entities, radar)


    for i in range(random.randint(3,5)):
        e = el.human(vacant_locs.pop())
        bisect.insort_left(entities, e)

    return (entities, terrain)
