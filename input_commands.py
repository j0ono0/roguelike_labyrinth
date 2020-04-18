
from settings import *
from environment import environment_manager as em
import interface as ui
import consoles
import keyboard

def move(parent, args):
    try:
        loc = parent.loc.proposed(args)
        target = em.get_target(loc, True)
        try:
            target.action(parent)
        except AttributeError as e:
            print(e)
            ui.narrative.add('The {} blocks your way.'.format(target.name))
    except IndexError as e:
        # Player reached edge of environment
        ui.narrative.add('There is no way through here!')


def use(parent, args):
    menu = ui.SelectMenu('Inventory')
    target = menu.select(parent.inventory.items) or em.get_target(self.parent.loc())
    
    # TODO enable player initiated use of items on ground
    
    try:
        target.action(parent)
    except AttributeError as e:
        ui.narrative.add('You see no way to use the {}.'.format(target.name))
        print(e)

def pickup_select(parent, args):
    targets = [t for t in em.entities if t.loc() == parent.loc() and t != parent]
    if len(targets) > 1:
        """ display select menu here """
    elif len(targets) == 1:
        parent.inventory.pickup(targets.pop())
    else:
        ui.narrative.add('There is nothing here to pickup.')


def drop_select(parent, args):
    menu = ui.SelectMenu('Inventory')
    target = menu.select(parent.inventory.items)
    parent.inventory.drop(target)


def help(parent, args):
    help_ui = consoles.NarrativeConsole()
    help_ui.clear()
    help_ui.blit(True)
    help_ui.con.print_box(1, 1, NAR_WIDTH, NAR_HEIGHT, HELP_TEXT, [255,255,255], [0,0,0])
    help_ui.blit(True)
    keyboard.CharInput().capture_keypress()

def target_select(parent, args):
    kb = keyboard.TargetInput()
    loc = parent.loc()
    display = consoles.EntityConsole()
    seen_tiles = [(x, y) for x in range(MAP_WIDTH) for y in range(MAP_HEIGHT) if em.terrain.tiles[x][y].seen == True]
    while True:
        if loc in seen_tiles:
            target = em.get_target(loc)
            glyph = target.glyph
            fg = [0,0,0]
            bg = [255,255,255]
        else:
            glyph = ' '
            fg = [0,0,0]
            bg = [120,120,120]
        display.con.print(0, 0, glyph, fg, bg)
        em.blit(parent.percept.fov)
        display.blit(loc, True)
        fn, args = kb.capture_keypress()
        if fn == 'target':
            loc = tuple([a+b for (a, b) in zip(loc, args)])
        else:
            return loc