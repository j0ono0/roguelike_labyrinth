"""

Input commands are functions that are called from player input.
All functions take a 'parent' (player's character) and 'args' (list of arguments). 

"""
from settings import *
import dungeon_master as dm
from user_interface import interfaces as ui
from user_interface import consoles
from user_interface import keyboard

def move(parent, args):
    try:
        loc = parent.loc.proposed(args)
        target = dm.get_target(loc, True)
        try:
            target.action(parent)
        except AttributeError as e:
            print(e)
            ui.narrative.add('The {} blocks your way.'.format(target.name))
    except IndexError as e:
        # Player reached edge of environment
        ui.narrative.add('There is no way through here!')


def use(parent, args):
    menu = ui.SelectMenu('Use from inventory:')
    target = menu.select(parent.inventory.items)
    
    # TODO enable player initiated use of items on ground
    
    try:
        target.action(parent)
    except AttributeError as e:
        ui.narrative.add('You see no way to use the {}.'.format(target.name))
        print(e)


def use_from_ground(parent, args):
    menu = ui.SelectMenu('Use from nearby:')
    items = [e for e in dm.entities if e.loc() == parent.loc() and e is not parent]
    target = menu.select(items)
    
    # TODO enable player initiated use of items on ground
    
    try:
        target.action(parent)
    except AttributeError as e:
        ui.narrative.add('You see no way to use the {}.'.format(target.name))
        print(e)

def pickup_select(parent, args):
        targets = [t for t in dm.entities if t.loc() == parent.loc() and t != parent]
        menu = ui.SelectMenu('Pickup:')
        target = menu.select(targets)
        
        try:
            parent.inventory.add(target)
            dm.entities.remove(target)
            
        except ValueError:
            """ no target exists """
            ui.narrative.add('There is nothing here to pickup.')
   

def drop_select(parent, args):
    menu = ui.SelectMenu('Drop from inventory')
    target = menu.select(parent.inventory.items)
    
    dm.entities.add(target)
    parent.inventory.remove(target)
    
    ui.narrative.add('{} drops a {}.'.format(parent.name, target.name))



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
    seen_tiles = [(x, y) for x in range(MAP_WIDTH) for y in range(MAP_HEIGHT) if dm.terrain.tiles[x][y].seen == True]
    
    narrative = consoles.NarrativeConsole()
    display = consoles.EntityConsole()
    
    while True:
        narrative.clear()
        if loc in seen_tiles:
            try:
                entities = [e for e in dm.entities if e.loc() == loc]
                glyph = entities[0].glyph
                if len(entities) > 7:
                    txt = '{} and many other items.'.format(entities[0])
                elif len(entities) > 1:
                    txt = '{} and a few other items.'.format(entities[0])
                else:
                    txt = '{}.'.format(entities[0])
            except IndexError:
                """ No entities are at this location """
                x, y = loc
                txt = dm.terrain.tiles[x][y].name
                glyph = dm.terrain.tiles[x][y].glyph

            fg = [0,0,0]
            bg = [255,255,255]
            narrative.con.print_box(1, 1, NAR_WIDTH, NAR_HEIGHT, txt, [255, 255, 255], [0, 0, 0])
        else:
            glyph = ' '
            fg = [0,0,0]
            bg = [120,120,120]
            
        display.con.print(0, 0, glyph, fg, bg)
        
        # Update screen
        dm.render_game()
        #narrative.blit()
        display.blit(loc, True)
        
        # Wait for keypress
        fn, args = kb.capture_keypress()
        if fn == 'target':
            loc = tuple([a+b for (a, b) in zip(loc, args)])
        else:
            return loc