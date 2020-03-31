import random
import copy
from collections import namedtuple
from elements import library as el

Location = namedtuple('Location',['x', 'y'])

class Map():
    def __init__(self, width, height, id=0):
        self.id = id
        self.width = width
        self.height = height
        self.tiles = []
        self.entities = []
    
    def fov_array(self):
        return {(x,y): self.tiles[x][y].blocked == False for x in range(self.width) for y in range(self.height)}

    def random_empty_loc(self):
        entity_locs = set([e.loc for  e in self.entities])
        unblocked_locs = set([(x, y) for x in range(self.width) for y in range(self.height) if (self.tiles[x][y].blocked == False)])
        return random.choice(list(unblocked_locs.difference(entity_locs)))

    def random_unblocked_loc(self):
        return random.choice([(x, y) for x in range(self.width) for y in range(self.height) if (self.tiles[x][y].blocked == False)])

    def fill_tiles(self, tile):
        self.tiles = [[copy.copy(tile) for y in range(self.width)] for x in range(self.height)]
    
    def random_tile_loc(self):
        x = random.randrange(0, (self.width))
        y = random.randrange(0, (self.height))
        return Location(x, y)

class BigRoom(Map):
    def __init__(self, width, height, id=0):
        super().__init__(width, height, id)
        self.build()

    def build(self):
        self.fill_tiles(el.wall())
        for x, y in [(x,y) for x in range(1, self.width - 1) for y in range(1, self.height - 1)]:
            self.tiles[x][y] = el.ground((x,y))

class MazeMap(Map):
    def __init__(self, width, height, id=0):
        super().__init__(width, height, id)
        self.build()
    
    def random_unblocked_loc(self):
        # Select from only even x/y tiles locations
        # ensures location will be unblocked on new maze levels
        return random.choice([(x * 2, y * 2) for x in range(self.width//2) for y in range(self.height//2)])

    def cardinal_neighbours(self, loc, x_max, y_max):
        x, y = loc
        locs = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        while locs:
            # Return in random order
            x, y = locs.pop(random.randint(0, len(locs)-1))
            if 0 <= x < x_max and 0 <= y < y_max:
                yield Location(x, y) 

    def build_graph(self, width, height):
        sx, sy = self.random_tile_loc()
        start = Location(sx // 2, sy // 2)
        graph = {}
        frontier = set([start])
        visited = set()
        graph[start] = set([start])
        
        while frontier:
            connected = False
            loc = random.sample(frontier, 1)[0]
            visited.add(loc)
            frontier.remove(loc)
            for n in self.cardinal_neighbours(loc, width, height):
                if n in graph and not connected:
                    graph[loc] = set([n])
                    graph[n].add(loc)
                    connected = True
                if n not in visited:
                    frontier.add(n)

        return graph

    def build(self):
        if self.width % 2 == 0 or self.height % 2 == 0:
            raise ValueError('mazeMap must be odd width and height.')
        # Build new graph and clear existing tiles
        graph = self.build_graph((self.width // 2) + 1, (self.height // 2) + 1)
        self.fill_tiles(el.wall())
        
        # Update tiles from graph data
        for loc, edges in graph.items():
            path = [(loc.x * 2, loc.y * 2)]
            for (x, y) in edges:
                dx = x - loc.x
                dy = y - loc.y
                path.append((loc.x * 2 + dx, loc.y * 2 + dy))
                
            for p in path:
                x, y = p
                self.tiles[x][y] = el.ground(p)
