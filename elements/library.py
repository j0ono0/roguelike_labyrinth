from . import entity
from . import actions

## Map features ##########

def ground(loc):
    return entity.Tile('ground', '.', False, actions.MoveToLoc(loc))
    

def wall():
    return entity.Tile('wall', '#', True, actions.BlockUser())


## Items ##########

def stairs_up(env_id, loc=(-1,-1), return_entity=None):
    return  entity.Entity(
                'stairs up', 
                '<', 
                entity.Location(loc),
                False, 
                actions.MoveToLevel(env_id, return_entity)
            )


def stairs_down(env_id, loc=(-1,-1), return_entity=None):
    return  entity.Entity(
                'stairs down', 
                '>', 
                entity.Location(loc),
                False, 
                actions.MoveToLevel(env_id, return_entity)
            )


def locator(loc):
    return entity.Entity('mysterious thing', '+', entity.Location(loc), False, actions.DisplayEntity())


## Characters and monsters ##########


def human(name, glyph, vision):
    b = entity.Entity(name, glyph)
    setattr(b, 'percept', entity.Perception(vision, b.loc))
    setattr(b, 'inventory', entity.Inventory(5))
    return b
