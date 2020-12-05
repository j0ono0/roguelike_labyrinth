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
        'ground'
    )
    

def wall():
    return entity.Tile(
        'wall'
    )


##############################
#
# Items
#
##############################


def scanner(loc):
    return entity.Scanner(loc)
    """ 
    return entity.Entity(
        'scanner', 
        loc,
        *COMMON_TRAITS['tech device'],
        (actions.display_entity_type, []),
    ) 
    """

def radar(loc):
    return entity.Radar(loc)
    """ 
    return entity.Entity(
        'radar',
        loc, 
        '+',
        [120, 150, 110], 
        [0, 0, 0], 
        Block(False, False),
        (actions.flee_map, []),
    )
    """
    
def handgun(loc):
    # return entity.HandGun(loc)
    
    return entity.Entity(
        'handgun',
        loc, 
        *COMMON_TRAITS['weapon'],
        abilities = {
            'act': (entity.RangeWeapon, [3]),
        }
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
        (actions.no_react, []),
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
        (actions.no_react, []),
    )


##############################
#
# Beings 
#
##############################

def player_character(name, loc):
    e = citizen(loc)
    # Customise character
    e.kind = 'player character'
    e.title = name
    e.fg = [255,255,255]
    e.glyph = '@'
    e.life = entity.Life(e, random.randint(8,16), 5)
    e.initiative.modifier += 1
    e.inventory.max = 10
    e.act = entity.PlayerInput(e)

    # Equip with initial starting items
    e.inventory.items.extend([scanner(e.loc), radar(e.loc), handgun(e.loc)])
    
    return e

def cat(loc):
    return entity.Entity(
        'cat',
        loc,
        *COMMON_TRAITS['feline'],
        abilities = {
            'act': (entity.Cat, []),
            'life': (entity.Life, [random.randint(2,4)]),
            'initiative': (entity.Initiative, [0]),
            'percept': (entity.Perception, [20]),
            'combat': (entity.Combat, [1, 1]),
        }
    )
        
def sheep(loc):
    return entity.Entity(
        'sheep',
        loc,
        *COMMON_TRAITS['sheep'],
        abilities = {
            'act': (entity.Cat, []),
            'life': (entity.Life, [random.randint(3,6)]),
            'initiative': (entity.Initiative, [0]),
            'percept': (entity.Perception, [10]),
            'combat': (entity.Combat, [1, 3]),
        }
    )

def citizen(loc):
    return entity.Entity(
        'citizen',
        loc, 
        *COMMON_TRAITS['citizen'],
        abilities = {
            'act': (entity.Citizen, []),
            'life': (entity.Life, [random.randint(2,5)]),
            'initiative': (entity.Initiative, [0]),
            'percept': (entity.Perception, [14]),
            'inventory': (entity.Inventory, [2]),
            'combat': (entity.Combat, [1, 1]),
        }
    )

def detective(loc):
    return entity.Entity(
        'detective',
        loc,
        *COMMON_TRAITS['detective'],
        abilities = {
            'act': (entity.Sentry, []),
            'life': (entity.Life, [random.randint(12,20)]),
            'initiative': (entity.Initiative, [0]),
            'percept': (entity.Perception, [18]),
            'inventory': (entity.Inventory, [5]),
            'combat': (entity.Combat, [7, 5]),
        }
    )
    
def police(loc):
    return entity.Entity(
        'police officer',
        loc,
        *COMMON_TRAITS['police officer'],
        abilities = {
            'act': (entity.Sentry, []),
            'life': (entity.Life, [random.randint(6,12)]),
            'initiative': (entity.Initiative, [0]),
            'percept': (entity.Perception, [16]),
            'inventory': (entity.Inventory, [5]),
            'combat': (entity.Combat, [3, 3]),
        }
    )