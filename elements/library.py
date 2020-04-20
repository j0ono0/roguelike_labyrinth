import random
from . import entity
from . import actions
from settings import *

## Map features ##########

def ground(loc):
    return entity.Tile(
        'ground', 
        {'action': (actions.MoveTarget,[loc])}
    )
    

def wall():
    return entity.Tile(
        'wall',
        {'action': (actions.BlockTarget, [])}
    )


## Items ##########

def stairs_up(env_id, loc=(-1,-1), return_entity=None):
    return  entity.Entity(
        'stairs up', 
        None, 
        entity.Location(loc), 
        {'action': (actions.MoveToLevel,[env_id, return_entity])}
    )


def stairs_down(env_id, loc=(-1,-1), return_entity=None):
    return entity.Entity(
        'stairs down',
        None,
        entity.Location(loc),
        {'action': (actions.MoveToLevel,[env_id, return_entity])}
    )


def locator(loc):
    return entity.Entity(
        'tech device',
        'locator', 
        loc if isinstance(loc, entity.Location) else entity.Location(loc), 
        {'action': (actions.DisplayEntity, [])}
    )


def radar(loc):
    return entity.Entity(
        'tech device', 
        'radar', 
        loc if isinstance(loc, entity.Location) else entity.Location(loc), 
        {'action': (actions.FleeMap, [])}
    )

## Characters and monsters ##########


def player_character(name, loc):
    max_vision = max(MAP_WIDTH, MAP_HEIGHT)
    b = entity.Entity(
        'human', 
        name, 
        entity.Location(loc), 
        {
            'life': (entity.Life, [4, 'good']),
            'percept': (entity.Perception, [max_vision]),
            'inventory': (entity.Inventory, [10]),
            'perform': (actions.PlayerInput, []),
            'action': (actions.Defend,[]),
        }
    )
    # Customise appearance
    b.fg = [255,255,255]
    # Equip with initial starting items
    b.inventory.items.extend([locator(b.loc), radar(b.loc)])
    return b

def human(loc):
    max_vision = max(MAP_WIDTH, MAP_HEIGHT)
    return entity.Entity(
        'human',
        None,
        entity.Location(loc),
        {
            'life': (entity.Life, [random.randint(3,5), 'bad']),
            'percept': (entity.Perception, [max_vision]),
            'inventory': (entity.Inventory, [10]),
            'perform': (actions.PersonalityA,[]),
            'action': (actions.Defend, []),
        }        
    ) 
