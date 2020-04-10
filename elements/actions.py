import tcod
from settings import *
import consoles
from consoles import root_console as console
from . import entity
import interface as ui
import keyboard


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
            lvl.create(MAP_WIDTH, MAP_HEIGHT, user.loc())
            if self.return_entity:
                self.return_entity.loc.update(user.loc())
                lvl.env.entities.append(self.return_entity)
        
        lvl.env.entities.append(user)
                

class DisplayEntity:
    def __call__(self, user, target, lvl):
        
        kb = keyboard.CharInput()
        
        narr = consoles.NarrativeConsole()
        narr.con.print_box(1, 1, NAR_WIDTH, NAR_HEIGHT, 'Type the symbol your seek.')
        narr.blit(True)
        
        char = kb.capture_keypress()

        narr.con.print_box(1, 1, NAR_WIDTH, NAR_HEIGHT, "You sense the device searching.")
        narr.blit()
        
        emap = consoles.EnvironmentConsole()

        entities = [e for e in lvl.env.entities if e.glyph == char]
        for e in entities:
            path = lvl.find_path(user.loc(), e.loc())
            for loc in path[1:]:
                emap.con.print(*loc, '.', [200,255,0])
            emap.con.print(*e.loc(), e.glyph, e.fg)
        
        emap.blit(True)
            
        # Pause before returning to game loop
        char = kb.capture_keypress()
        

class PersonalityA:
    def __init__(self):
        self.path = []

    def __call__(self, user, lvl):
        
        # TODO: stop from walking through blocking entities

        if len(self.path) > 0:
            loc = self.path.pop()
            target = lvl.get_target(loc, True)
            try:
                target.action(user, target, lvl)
            except AttributeError:
                ui.narrative.add('A {} blocks the {}\'s way.'.format(target.kind, user.kind))
            
            # replace loc if entity was unable to move
            if user.loc() != loc:
                self.path.append(loc)

    def flee(self, user, target, lvl):
        ui.narrative.add('The {} menaces a {}'.format(user.kind, target.kind))
        ui.narrative.add('The {} flees!'.format(target.kind))
        self.path = lvl.find_path(target.loc(), lvl.env.random_empty_loc())


class PlayerInput:
    def __call__(self, user, lvl):

        # update player field of view
        user.percept.see(lvl.env.fov_array())
        lvl.update_seen(user.percept.fov)
        
        # Render game to screen
        console.clear()
        consoles.render_base()
        
        lvl.blit(user.percept.fov)
        ui.narrative.blit()
        console.print(*(x + y for x, y in zip(MAP_OFFSET, user.loc())), user.glyph, user.fg)
        
        tcod.console_flush()

        kb = keyboard.GameInput()
        # Process user input
        fn, args, kwargs = kb.capture_keypress()
        if fn == 'move':
            try:
                loc = user.loc.proposed(args)
                target = lvl.get_target(loc, True)
                try:
                    target.action(user, target, lvl)
                except AttributeError:
                    ui.narrative.add('The {} blocks your way.'.format(target.name))
            except IndexError as e:
                # Player reached edge of environment
                ui.narrative.add('There is no way through here!')

        elif fn == 'use':
            menu = ui.SelectMenu('Inventory')
            target = menu.select(user.inventory.items) or lvl.get_target(user.loc())
            try:
                target.action(user, target, lvl)
            except AttributeError:
                ui.narrative.add('You see no way to use the {}.'.format(target.name))

        elif fn == 'pickup_select':
            targets = [t for t in lvl.env.entities if t.loc() == user.loc() and t != user]
            if len(targets) > 1:
                """ display select menu here """
            elif len(targets) == 1:
                user.inventory.pickup(user, targets.pop(), lvl)
            else:
                ui.narrative.add('There is nothing here to pickup.')

        elif fn == 'drop_select':
            menu = ui.SelectMenu('Inventory')
            target = menu.select(user.inventory.items)
            user.inventory.drop(user, target, lvl)
