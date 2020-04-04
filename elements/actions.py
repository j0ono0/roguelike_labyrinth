from settings import *
from . import entity
import interface as ui


class Interact:
    def __call__(self, user, target, lvl):
        ui.narrative.add("{} interacts with {}".format(user.name, target.name))
        

class BlockUser:
    def __call__(self, user, target, lvl):
        ui.narrative.add("The {} does not move, that way is blocked".format(target.name))


class MoveToLoc:
    def __init__(self, loc):
        self.loc = loc
    
    def __call__(self, user, target, lvl):
        user.loc.update(self.loc)


class MoveToLevel:
    def __init__(self, env_id, return_entity):
        self.env_id = env_id
        self.return_entity = return_entity

    def __call__(self, user, target, lvl):
        lvl.save()
        try:
            lvl.load(self.env_id)
            print(f'level {lvl.env.id} loaded')
        except FileNotFoundError:
            print('Level not found. Creating new level')
            lvl.create(MAP_WIDTH, MAP_HEIGHT)
            if self.return_entity:
                self.return_entity.loc.update(user.loc())
                lvl.env.entities.append(self.return_entity)
                

