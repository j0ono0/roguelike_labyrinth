from collections import deque
import tcod
from settings import *


history = deque(['Monkey was born form a stone egg.'],100)
queue = [
    "Welcome to roguelike!",
    "Progress has been slow due to having to babysit my little one constantly. The days I get off I still seem to be spending quite some time dadding.",
    "'u' to use items.",
    "',' to pickup items.",
]

def add(msg):
    queue.append(msg)

def blit(console):
    y = 0
    con = tcod.console.Console(NAR_WIDTH, NAR_HEIGHT)
    while queue:
        print(queue[0])
        y = y + 1 + con.print_box(1, y, NAR_WIDTH-1, NAR_HEIGHT, queue[0])
        history.appendleft(queue.pop(0))

    con.blit(console, *NAR_OFFSET, 0, 0, NAR_WIDTH+2, NAR_HEIGHT+2, 1, 0, 0)
