import random 
from collections import namedtuple

Location = namedtuple('Location',['x', 'y'])
 
def cardinal_neighbours(x, y, x_max, y_max):
    locs = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    while locs:
        # Return in random order
        x, y = locs.pop(random.randint(0, len(locs)-1))
        if 0 <= x < x_max and 0 <= y < y_max:
            yield Location(x, y) 
    
def build_graph(width, height):
    graph = {}
    start = Location(random.randrange(0, width), random.randrange(0, height))
    frontier = set([start])
    graph[start] = set([start])
    
    while frontier:
        connected = False
        loc = random.sample(frontier, 1)[0]
        frontier.remove(loc)
        for n in cardinal_neighbours(*loc, width, height):
            if n not in graph:
                frontier.add(n)
            elif not connected:
                graph[loc] = set([n])
                graph[n].add(loc)
                connected = True
    return graph