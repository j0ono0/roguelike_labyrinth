import random
from collections import namedtuple

from . import entity
from . import actions
from settings import *


Block = namedtuple('Block', ['motion', 'sight'])

##############################
#
# Map features
#
##############################
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


##############################
#
# Items
#
##############################


def scanner(loc):
    return entity.Entity(
        'scanner', 
        loc,
        *COMMON_TRAITS['tech device'],
        {'action': (actions.DisplayEntity, [])}
    )


def radar(loc):
    return entity.Entity(
        'radar',
        loc, 
        '+',
        [120, 150, 110], 
        [0, 0, 0], 
        Block(False, False),
        {'action': (actions.FleeMap, [])}
    )


def stairs_down(loc, envid, coords=None):
    coords = coords or loc
    # Ensure coords are not a location object
    if isinstance(coords, entity.Location):
        coords = coords()

    return entity.Entity(
        'stairs down',
        loc,
        *COMMON_TRAITS['exit down'],
        {'action': (actions.RelocateTarget, [envid, coords])}
    )

def stairs_up(loc, envid, coords=None):
    coords = coords or loc
    # Ensure coords are not a location object
    if isinstance(coords, entity.Location):
        coords = coords()

    return entity.Entity(
        'stairs up',
        loc,
        *COMMON_TRAITS['exit up'],
        {'action': (actions.RelocateTarget, [envid, coords])}
    )


##############################
#
# Beings 
#
##############################

def player_character(name, loc):
    e = human(loc)
    # Customise character
    e.name = name
    e.fg = [255,255,255]
    e.perform = actions.PlayerInput(e)
    e.life = entity.Life(e, random.randint(4,10), 'good')
    e.inventory.max = 10

    # Equip with initial starting items
    e.inventory.items.extend([scanner(e.loc), radar(e.loc)])
    
    return e


def human(loc):
    return entity.Entity(
        'human',
        loc, 
        *COMMON_TRAITS['human'],
        {
            'life': (entity.Life, [random.randint(2,5), 'neutral']),
            'percept': (entity.Perception, [max(MAP_WIDTH, MAP_HEIGHT)]),
            'inventory': (entity.Inventory, [5]),
            'perform': (actions.PersonalityA,[]),
            'action': (actions.Defend, []),
        }
    )

