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
    loc = loc if isinstance(loc, entity.Location) else entity.Location(loc)
    return entity.Entity('mysterious thing', 'tech_device', loc, False, actions.DisplayEntity())


## Characters and monsters ##########


def player_character(name, loc):
    b = entity.Entity(name, 'player_character', entity.Location(loc), True)
    max_vision = max(MAP_WIDTH, MAP_HEIGHT)
    setattr(b, 'percept', entity.Perception(max_vision, b.loc))
    setattr(b, 'inventory', entity.Inventory(10))
    b.inventory.items.append(locator(b.loc))
    return b

def human(name, loc):
    b = entity.Entity(name, 'human', entity.Location(loc), True)
    max_vision = max(MAP_WIDTH, MAP_HEIGHT)
    setattr(b, 'percept', entity.Perception(max_vision, b.loc))
    setattr(b, 'inventory', entity.Inventory(10))
    setattr(b, 'ai', actions.PersonalityA())
    b.action = b.ai.flee
        
    return b
