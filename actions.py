##########################
# "Action" classes       #
##########################
import level_handler as lvl 
from entity import Entity

class RelocateUser:
    def __init__(self, loc, dest_id):
        self.loc = loc
        self.dest_id = dest_id

    def __call__(self, user):
        print('relocation triggered.')
        user.loc.set(*self.loc)
        lvl.change(self.dest_id)
        # Update entry/exit
        lvl.env.entry = self.loc
        lvl.env.exit = lvl.env.random_unblocked_loc()

        exit = Entity('Exit', '>')
        exit.loc.set(*lvl.env.exit)
        exit.action = RelocateUser(exit.loc(), self.dest_id + 1)

        entry = Entity('Entry', '<')
        entry.loc.set(*self.loc)
        entry.action = RelocateUser(entry.loc(), self.dest_id - 1)
        lvl.env.entities = [entry, exit]
        lvl.env.fov.scan(self.loc)
