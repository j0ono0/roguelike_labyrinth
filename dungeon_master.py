import os
import pickle
import re 
import random
from copy import deepcopy

import tcod

from user_interface import consoles
from user_interface import interfaces as ui
from environment import terrain as terra
from environment import library as el
from environment import build
import pathfinding as pf
from settings import LEVEL_PREFIX, MAP_HEIGHT, MAP_WIDTH


class DungeonMaster:
    def __init__(self):
        self.entities = None
        self.terrain = None
        self.pc = None

        self.create_pc()
        self.create_lvl()

        # update player field of view
        self.pc.percept.look(self.terrain)
        # DOTO: can this be include in the above function?
        self.terrain.mark_as_seen(self.pc.percept.fov)

        self.entities.append(self.pc)

        # Assign player to display and do initial render of screen
        self.render_game()

    def create_pc(self, name='Dekard'):
        self.pc = el.player_character(name, (random.randint(4, MAP_WIDTH - 4), random.randint(4, MAP_HEIGHT - 4)))

    def create_lvl(self, entry_loc=None):    
        #find highest id in gamedata
        filenames = os.listdir('gamedata')
        p = re.compile(r'_(?P<id>\d+)\.')
        ids = [int(p.search(i).group('id')) for i in filenames]
        try:
            envid = max(ids) + 1
        except ValueError:
            # New game
            envid = 1
        entry_loc = entry_loc or self.pc.loc()
        self.entities, self.terrain = build.environment(envid, entry_loc)

    def get_target(self, loc, block_motion=False):
        # Return first item (or tile) at location
        if block_motion == True:
            return next(iter([e for e in self.entities if e.loc() == loc and e.block.motion == True]), self.terrain.get_tile(loc))
        return next(iter([e for e in self.entities if e.loc() == loc]), self.terrain.get_tile(loc))
    
    def find_path(self, start, end, avoid_blocking_entities=False):
        if avoid_blocking_entities == True:
            motionmap = deepcopy(self.terrain.motionmap)
            for x, y in [e.loc() for e in self.entities if e.block.motion == True and e.loc() not in [start, end]]:
                motionmap[x][y] = False
        else:
            motionmap = self.terrain.motionmap
        
        path = pf.astar(motionmap, start, end)
        return path
    
    def vacant_locs(self):
        # List of locs that are not blocked by terrain or entities
        blocked_locs = (e.loc() for e in self.entities if e.block.motion)
        return [loc for loc in self.terrain.unblocked_tiles() if loc not in blocked_locs]

    def render_game(self):
        
        consoles.root_console.clear()
        consoles.render_base()
        
        ui.render_character_info(self.pc)
        ui.narrative.blit()
        ui.render_game(self.entities, self.terrain, self.pc.percept.fov)
        
        tcod.console_flush()

    def progress_game(self):
        # TODO: 'roll' initiative
        for e in self.entities:
            if hasattr(e, 'initiative'):
                try:
                    # Pass dm into entity act fn.
                    e.act(self)

                except (TypeError, UnboundLocalError):
                    """ entity has no act attribute """

                # Update entities field of view
                if e is self.pc:
                    e.percept.look(self.terrain)
                    self.terrain.mark_as_seen(e.percept.fov)
                
                # Rerender after each turn
                self.render_game()




#################
# Module variables
entities = None
terrain = None
#pc = el.player_character('Deckard', (random.randint(4, MAP_WIDTH - 4), random.randint(4, MAP_HEIGHT - 4)))
pc = None
#################

def create_pc(name='Dekard'):
    global pc
    pc = el.player_character(name, (random.randint(4, MAP_WIDTH - 4), random.randint(4, MAP_HEIGHT - 4)))

def delete_all():
    levels = [n for n in os.listdir('gamedata') if n[:len(LEVEL_PREFIX)] == LEVEL_PREFIX]
    for filename in levels:
        path = os.path.join('gamedata', filename)
        os.remove(path)


def create(entry_loc=None):
    global entities, terrain
    
    #find highest id in gamedata
    filenames = os.listdir('gamedata')
    p = re.compile(r'_(?P<id>\d+)\.')
    ids = [int(p.search(i).group('id')) for i in filenames]
    try:
        envid = max(ids) + 1
    except ValueError:
        # New game
        envid = 1

    entities, terrain = build.environment(envid, entry_loc)


def load(id):
    global entities, terrain
    filepath = os.path.join('gamedata', f'{LEVEL_PREFIX}{id}.pickle')
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    terrain = data['environment']
    entities = data['entities']


def save():
    # remove player character(s) before saving
    game = {
        'environment': terrain,
        'entities': [e for e in entities if e != pc]
    }

    filepath = os.path.join('gamedata', f'{LEVEL_PREFIX}{terrain.id}.pickle')
    with open(filepath, 'wb') as f:
        pickle.dump(game, f)
    print(f'game environment {terrain.id} saved')


def render_game():
        fov = pc.percept.fov
        
        consoles.root_console.clear()
        consoles.render_base()
        
        ui.render_character_info(pc)
        ui.narrative.blit()
        ui.render_game(entities, terrain, fov)
        
        tcod.console_flush()


def get_target(loc, block_motion=False):
    # Return first item (or tile) at location
    if block_motion == True:
        return next(iter([e for e in entities if e.loc() == loc and e.block.motion == True]), terrain.get_tile(loc))
    return next(iter([e for e in entities if e.loc() == loc]), terrain.get_tile(loc))
    

def find_path(start, end, avoid_blocking_entities=False):
    if avoid_blocking_entities == True:
        motionmap = deepcopy(terrain.motionmap)
        for x, y in [e.loc() for e in entities if e.block.motion == True and e.loc() not in [start, end]]:
            motionmap[x][y] = False
    else:
        motionmap = terrain.motionmap
    
    path = pf.astar(motionmap, start, end)
    return path


def random_empty_loc():
    entity_locs = set([e.loc for  e in entities])
    unblocked_locs = set([(x, y) for x in range(MAP_WIDTH) for y in range(MAP_HEIGHT) if (terrain.tiles[x][y].block.motion == False)])
    return random.choice(list(unblocked_locs.difference(entity_locs)))

def random_unblocked_loc():
    return random.choice([(x, y) for x in range(MAP_WIDTH) for y in range(MAP_HEIGHT) if (terrain.tiles[x][y].block.motion == False)])
