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
    return entity.Entity(
        'scanner', 
        loc,
        *COMMON_TRAITS['tech device'],
        (actions.no_act, []),
        (actions.display_entity_type, []),
    )

def radar(loc):
    return entity.Entity(
        'radar',
        loc, 
        '+',
        [120, 150, 110], 
        [0, 0, 0], 
        Block(False, False),
        (actions.no_act, []),
        (actions.flee_map, []),
    )
    
def handgun(loc):
    return entity.Entity(
        'handgun',
        loc, 
        *COMMON_TRAITS['weapon'],
        (actions.no_act, []),
        (actions.no_react, []),
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
        (actions.no_act, []),
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
        (actions.no_act, []),
        (actions.no_react, []),
    )


##############################
#
# Beings 
#
##############################

def player_character(name, loc):
    e = human(loc)
    # Customise character
    e.title = name
    e.fg = [255,255,255]
    e.life = entity.Life(e, random.randint(4,10), 5)
    e.inventory.max = 10
    e.act = (actions.player_input, [])

    # Equip with initial starting items
    e.inventory.items.extend([scanner(e.loc), radar(e.loc), handgun(e.loc)])
    
    return e


def human(loc):
    return entity.Entity(
        'human',
        loc, 
        *COMMON_TRAITS['human'],
        (actions.personality_a, []),
        (actions.personality_a_react, []),
        abilities = {
            'life': (entity.Life, [random.randint(2,5), random.randint(-2,5)]),
            'percept': (entity.Perception, [max(MAP_WIDTH, MAP_HEIGHT)]),
            'inventory': (entity.Inventory, [5]),
        }
    )

def android(loc, version = 'a'):
    andr_type = 'android ' + version
    return entity.Entity(
        andr_type,
        loc, 
        *COMMON_TRAITS[andr_type],
        (actions.personality_a, []),
        (actions.personality_a_react, []),
        {
            'life': (entity.Life, [random.randint(2,5), random.randint(-7,2)]),
            'percept': (entity.Perception, [max(MAP_WIDTH, MAP_HEIGHT)]),
            'inventory': (entity.Inventory, [5]),
        }
    )
