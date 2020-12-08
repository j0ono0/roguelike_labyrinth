"""

Input commands are functions that are called from player input.
All functions take a 'parent' (player's character) and 'args' (list of arguments). 

"""
import math
import random
from settings import *
from user_interface import interfaces as ui
from user_interface import consoles
from user_interface import keyboard
from environment import actions
import pathfinding as pf
from environment import entity


def move(dm, parent, args):
    try:
        loc = parent.loc.proposed(args)
        target = dm.get_target(loc, True)

        if not target.block.motion:
            parent.loc.update(loc)
        else:
            try:
                parent.combat.attack(target)
            except Exception as e:
                # Player cannot attack
                print('player cannot attack!', e)

    except IndexError:
        # Player reached edge of environment
        ui.narrative.add('There is no way through here!')


def use(dm, parent, args):
    menu = ui.SelectMenu('Use from inventory:')
    target = menu.select(parent.inventory.items)
    target.act(dm)


def use_from_ground(dm, parent, args):
    menu = ui.SelectMenu('Use from nearby:')
    items = [e for e in dm.entities if e.loc() == parent.loc() and e is not parent]
    target = menu.select(items)
    
    # TODO enable player initiated use of items on ground
    return target.react


def pickup_select(dm, parent, args):
        targets = [t for t in dm.entities if t.loc() == parent.loc() and t != parent]
        menu = ui.SelectMenu('Pickup:')
        target = menu.select(targets)
        
        try:
            parent.inventory.add(target)
            dm.entities.remove(target)
            
        except ValueError:
            """ no target exists """
            ui.narrative.add('There is nothing here to pickup.')
   

def drop_select(dm, parent, args):
    menu = ui.SelectMenu('Drop from inventory')
    target = menu.select(parent.inventory.items)
    
    dm.entities.add(target)
    parent.inventory.remove(target)
    
    ui.narrative.add('{} drops a {}.'.format(parent.name, target.name))


def help(dm, parent, args):
    help_ui = consoles.NarrativeConsole()
    help_ui.clear()
    help_ui.blit(True)
    help_ui.con.print_box(1, 1, NAR_WIDTH, NAR_HEIGHT, HELP_TEXT, [255,255,255], [0,0,0])
    help_ui.blit(True)
    keyboard.CharInput().capture_keypress()


def tag_entity(dm, parent, args):
    loc = target_select(parent, None)
    target = next((e for e in dm.entities if e.loc() == loc and hasattr(e, 'life')), None)
    tag = ' (suspect: android)'
    if tag in target.name:
        # Remove tag
        target.title = None
        target.fg = COMMON_TRAITS[target.kind].fg
        target.bg = COMMON_TRAITS[target.kind].bg
    else:
        # Tag target
        target.title = target.kind + tag
        target.fg = [0, 0, 0]
        target.bg = [100, 100, 200]


#TODO: this is broken
def range_attack(dm, parent, target):
    ui.narrative.add('You aim the gun...')
    loc = actions.target_select(dm, parent, target)
    aim = los(target.loc(), loc)
    path = aim.path(map=dm.terrain.motionmap)
    ui.narrative.add('And dial distance;')
    ui.narrative.add('The gun kicks as charged metal crackles through the air.')

    for victim in [e for e in dm.entities if e.loc() in path and e != target]:
        try:
            victim.life.damage(random.randint(2,10))
        except AttributeError:
            ui.narrative.add(f'The {victim.name} smokes a little.')
                

def interrogate(dm, parent, target):
    selected_loc = actions.target_select(dm, parent, None)
    target_entity = next((e for e in dm.entities if hasattr(e, 'life') and e.loc() == selected_loc), None)
    distance = math.ceil(pf.distance(parent.loc(), selected_loc))
    print(target_entity)
    if target_entity.life.android:
        confess = (1 / distance * 100) < random.randint(0,100)
        if confess:
            ui.narrative.add(f"{target_entity.name} cracks! It's an android!")
            target_entity.act = entity.Cat(target_entity)
        else:
            ui.narrative.add(f"{target_entity.name} indicates 2 in 3 detectives are andys.")
    else:
        ui.narrative.add(f'{target_entity.name} sweats but responds within reason.')