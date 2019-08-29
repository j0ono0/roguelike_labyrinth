##########################
# "Action" classes       #
##########################
import level_handler as lvl 
from entity import Entity
from settings import *


def add_exit(loc=None, id=None):
    loc = loc or lvl.env.random_unblocked_loc()
    id = id or lvl.env.id
    if id >= lvl.env.id:
        glyph = '>'
        label = 'Exit down'
    else:
        glyph = '<'
        label = 'Exit up'
    lvl.env.entities.append(Entity(label, glyph, loc, RelocateUser(loc, id)))

class RelocateUser:
    def __init__(self, loc, dest_id):
        self.loc = loc
        self.dest_id = dest_id

    def __call__(self, user):
        print('relocation triggered.')
        user.loc.set(*self.loc)
        lvl.save()
        try:
            lvl.load(self.dest_id)
            print(f'level {lvl.env.id} loaded')
        except FileNotFoundError:
            print('Level not found. Creating new level')
            lvl.create(MAP_WIDTH, MAP_HEIGHT)
            add_exit(self.loc, self.dest_id - 1)
            add_exit(lvl.env.random_unblocked_loc(), self.dest_id + 1)
        lvl.env.fov.scan(user.loc())