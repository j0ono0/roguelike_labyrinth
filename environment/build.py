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
    """ 
    # Exits
    if envid > 1:
        exit_up = el.stairs_up(entry_loc, terrain.id-1)
        entities.add(exit_up)
    
    
    if envid < 6:
        exit_down = el.stairs_down(vacant_locs.pop(), terrain.id+1)
        entities.add(exit_down)
    """
    # Items
    radar = el.radar(vacant_locs.pop())
    entities.add(radar)

    # test cat
    cat = el.cat(vacant_locs.pop())
    entities.add(cat)

    # Beings
    for i in range(random.randint(5,8)):
        entities.add(el.citizen(vacant_locs.pop()))
    
    entities.add(el.detective(vacant_locs.pop()))
    
    for i in range(random.randint(2,4)):
        entities.add(el.police(vacant_locs.pop()))
    
    # Convert 3 humans to androids
    candidates = ['police officer', 'detective', 'citizen']
    for a in random.sample([e for e in entities if e.kind in candidates], 3):
        a.life.android = True
        a.fg = [100, 255, 120]

        
    return (entities, terrain)
