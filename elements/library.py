from . import entity
from . import actions
from settings import *

## Map features ##########

def ground(loc):
    return entity.Tile('ground', 'ground', False, actions.MoveToLoc(loc))
    

def wall():
    return entity.Tile('wall', 'wall', True, actions.BlockUser())


## Items ##########

def stairs_up(env_id, loc=(-1,-1), return_entity=None):
    return  entity.Entity(
                'stairs up', 
                'stairs_up', 
                entity.Location(loc),
                False, 
                actions.MoveToLevel(env_id, return_entity)
            )


def stairs_down(env_id, loc=(-1,-1), return_entity=None):
    return  entity.Entity(
                'stairs down',
                'stairs_down',
                entity.Location(loc),
                False, 
                actions.MoveToLevel(env_id, return_entity)
            )


def locator(loc):
    return entity.Entity('mysterious thing', 'tech_device', entity.Location(loc), False, actions.DisplayEntity())


## Characters and monsters ##########


def human(name, personality=None):
    b = entity.Entity(name, 'human')
    max_vision = max(MAP_WIDTH, MAP_HEIGHT)
    setattr(b, 'percept', entity.Perception(max_vision, b.loc))
    setattr(b, 'inventory', entity.Inventory(10))
    if personality != None:
        setattr(b, 'act', personality)
        
    return b
