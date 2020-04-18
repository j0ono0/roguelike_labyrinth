from . import entity
from . import actions
from settings import *

## Map features ##########

def ground(loc):
    return entity.Tile(
        'ground', 
        'ground', 
        {'action': (actions.MoveTarget,[loc])}
    )
    

def wall():
    return entity.Tile(
        'wall', 
        'wall',
        {'action': (actions.BlockTarget, [])}
    )


## Items ##########

def stairs_up(env_id, loc=(-1,-1), return_entity=None):
    return  entity.Entity(
        'stairs up', 
        'stairs up', 
        entity.Location(loc), 
        {'action': (actions.MoveToLevel,[env_id, return_entity])}
    )


def stairs_down(env_id, loc=(-1,-1), return_entity=None):
    return entity.Entity(
                'stairs down',
                'stairs down',
                entity.Location(loc),
                {'action': (actions.MoveToLevel,[env_id, return_entity])}
            )


def locator(loc):
    return entity.Entity(
        'mysterious thing', 
        'tech device',
        loc if isinstance(loc, entity.Location) else entity.Location(loc), 
        {'action': (actions.DisplayEntity, [])}
    )


def radar(loc):
    return entity.Entity(
        'Radar', 
        'tech device', 
        loc if isinstance(loc, entity.Location) else entity.Location(loc), 
        {'action': (actions.FleeMap, [])}
    )

## Characters and monsters ##########


def player_character(name, loc):
    max_vision = max(MAP_WIDTH, MAP_HEIGHT)
    b = entity.Entity(
        name, 
        'player character', 
        entity.Location(loc), 
        {
            'action': (actions.BlockTarget,[]),
            'percept': (entity.Perception, [max_vision]),
            'inventory': (entity.Inventory, [10]),
            'perform': (actions.PlayerInput, [])
        }
    )
    # Equip with initial starting items
    b.inventory.items.extend([locator(b.loc), radar(b.loc)])
    return b

def human(name, loc):
    max_vision = max(MAP_WIDTH, MAP_HEIGHT)
    return entity.Entity(
        name, 
        'human', 
        entity.Location(loc),
        {
            'percept': (entity.Perception, [max_vision]),
            'inventory': (entity.Inventory, [10]),
            'perform': (actions.PersonalityA,[]),
            'action': (actions.FleeTarget, [])
        }        
    ) 
