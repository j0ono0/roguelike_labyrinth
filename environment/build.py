"""

Build terrain and populate with entities

"""
import bisect
import random
from settings import MAP_HEIGHT, MAP_WIDTH
from . import terrain as t
from . import library as el
from . import entity


class EntityList(list):
    def add(self, item):
        bisect.insort_left(self, item)


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
    
    entities = EntityList()
    
    vacant_locs = terrain.unblocked_tiles()
    random.shuffle(vacant_locs)
    
    # Exits
    if envid > 1:
        exit_up = el.stairs_up(entry_loc, terrain.id-1)
        entities.add(exit_up)
    
    
    if envid < 6:
        exit_down = el.stairs_down(vacant_locs.pop(), terrain.id+1)
        entities.add(exit_down)

    # Items
    radar = el.radar(vacant_locs.pop())
    entities.add(radar)


    # Beings
    for i in range(random.randint(4,7)):
        j = random.randint(1,100)
        if j >= 10:
            e = el.android(vacant_locs.pop(), random.choice(['a','b']))
        elif j >= 30:
            e = el.android(vacant_locs.pop(), random.choice(['a','b']))
        else:
            e = el.human(vacant_locs.pop())
        
        entities.add(e)
    
    return (entities, terrain)
