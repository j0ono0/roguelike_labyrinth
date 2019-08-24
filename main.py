#!/usr/bin/env python
import random
import tcod
import tcod.event
from entity import Entity
from pathfinding import astar
import level_handler as lvl
import actions


# Create a dictionary that maps keys to vectors.
# Names of the available keys can be found in the online documentation:
# http://packages.python.org/tdl/tdl.event-module.html
MOVEMENT_KEYS = {
    # standard arrow keys
    tcod.event.K_UP: [0, -1],
    tcod.event.K_DOWN: [0, 1],
    tcod.event.K_LEFT: [-1, 0],
    tcod.event.K_RIGHT: [1, 0],
}
ACTION_KEYS = {
    tcod.event.K_SPACE: True
}

# Setup the font.
tcod.console_set_custom_font(
    "arial10x10.png",
    tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
)

# Create first environment
lvl.create()

# Setup exits
exit = Entity('Exit', '>')
exit.loc.set(*lvl.env.exit)
exit.action = actions.RelocateUser(exit.loc(), lvl.env.id + 1)

entry = Entity('Entry', '<')
entry.loc.set(*lvl.env.entry)
entry.action = actions.RelocateUser(entry.loc(), lvl.env.id - 1)

lvl.env.entities = [entry, exit]


# Setup player
player = Entity('Player_01', '@')
player.loc.set(*lvl.env.entry)

# Update environment with player fov
lvl.env.fov.scan(player.loc())


# Pathfinding demo
def path_to_loc(loc):
    start = player.loc()
    return astar(lvl.env.tiles, start, loc)


# Initialize the root console in a context.
with tcod.console_init_root(lvl.MAP_WIDTH, lvl.MAP_HEIGHT, order="F") as console:
    while True:
        # Update console and render.
        console.clear()
        lvl.env.con().blit(console)
        
        # Print pathfinding
        color = [200,40,40]
        for loc in path_to_loc(lvl.env.exit):
            console.print(*loc, '+', color)

        color = [60,255,100]
        for loc in path_to_loc(lvl.env.entry):
            console.print(*loc, '-', color)
        
        for en in lvl.env.entities:
            if lvl.env.tiles[en.loc()].visible:
                console.print_(*en.loc(), en.glyph)
        
        console.print_(*player.loc(), player.glyph)
            
        # Test for maze completion
        msg = None
        if player.loc() == lvl.env.exit:
            msg = ['Next level:{}'.format(lvl.env.id + 1), '<space>']
        elif player.loc() == lvl.env.entry:
            msg = ['Prev level:{}'.format(lvl.env.id - 1), '<space>']
        if msg:
            y = (lvl.MAP_HEIGHT - len(msg)) // 2
            for i, ln in enumerate(msg):
                x = (lvl.MAP_WIDTH - len(ln)) // 2
                console.print_(x, y + i, ln)
            
        
        tcod.console_flush()

        # User input
        for event in tcod.event.wait():
            if event.type == 'KEYDOWN':

                if event.sym in MOVEMENT_KEYS:
                    player.loc.move(*MOVEMENT_KEYS[event.sym], lvl.env)
                    lvl.env.fov.scan(player.loc())

                elif event.sym in ACTION_KEYS:
                    item = [e for e in lvl.env.entities if e.loc() == player.loc()][0]
                    #Player uses item at location
                    player.use(item.action)
                    

            if event.type == 'QUIT':
                # Halt the script using SystemExit
                raise SystemExit('The window has been closed.')