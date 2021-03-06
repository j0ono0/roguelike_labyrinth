import random
import copy
from collections import namedtuple
from . import library as el
from settings import *

Location = namedtuple('Location',['x', 'y'])


class LimitList(list):
    """
    Prohibit negative index values. 
    Used for tracking map locations where negative 
    values would leave the valid map
    """
    def __getitem__(self, index):
        if index < 0:
            raise IndexError('Index out of range (negative value in LimitList)')
        return super().__getitem__(index)


class Rect:
    """ Rectangle on the map. used to characterize a room """
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)
 
    def intersects(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Terrain():
    def __init__(self, id=0):
        self.id = id
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.tiles = LimitList([LimitList([el.wall() for y in range(self.height)]) for x in range(self.width)])
        # Save 2d array of tiles that allow sight for easy & fast reference
        self.sightmap = None
        self.motionmap = None
    
    def create_sightmap(self):
        # Create new sightmap if it does not exist.
        self.sightmap = [[self.tiles[x][y].block.sight == False for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    def create_motionmap(self):
        # Create new sightmap if it does not exist.
        self.motionmap = [[self.tiles[x][y].block.motion == False for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    def unblocked_tiles(self):
        return [(x, y) for x in range(self.width) for y in range(self.height) if self.tiles[x][y].block.motion == False]

    def get_tile(self, loc):
        x, y = loc
        return self.tiles[x][y]
    
    def mark_as_seen(self, locs):
        for loc in locs:
            x, y = loc
            self.tiles[x][y].seen = True

class BigRoom(Terrain):
    def __init__(self, id=0):
        super().__init__(id)

    def build(self, entry_loc=None):
        for x, y in [(x,y) for x in range(1, self.width - 1) for y in range(1, self.height - 1)]:
            self.tiles[x][y] = el.ground((x,y))

        
        self.create_motionmap()
        self.create_sightmap()


class BasicDungeon(Terrain):
    def __init__(self, id=0):
        super().__init__(id)
        self.rooms = []
        self.min_size = 4
        self.max_size = 15
        self.max_rooms = 10
    
    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                try:
                    self.tiles[x][y] = el.ground((x,y))
                except IndexError:
                    """ Outside valid terrain coordinates """
    
    def create_room_at(self, loc):
            x, y = loc
            w = random.randint(self.min_size, self.max_size)
            h = random.randint(self.min_size, self.max_size)
            x = x - w // 2
            y = y - h // 2
            self.rooms.append(Rect(x, y, w, h))

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y] = el.ground((x,y))

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y] = el.ground((x,y))

    def build(self, entry_loc=None):
        try:
            self.create_room_at(entry_loc)
        except TypeError: 
            """ no loc provided """

        for r in range(self.max_rooms):
            w = random.randint(self.min_size, self.max_size)
            h = random.randint(self.min_size, self.max_size)
            x = random.randint(0, self.width - w - 1)
            y = random.randint(0, self.height - h - 1)
            rm = Rect(x, y, w, h)
            
            if len([r for r in self.rooms if r.intersects(rm)]) == 0:
                self.rooms.append(rm)
        
        for i, r in enumerate(self.rooms):
            self.create_room(r)
            try:
                x1, y1 = r.center()
                x2, y2 = self.rooms[i+1].center()
                self.create_h_tunnel(x1, x2, y1)
                self.create_v_tunnel(y1, y2, x2)
            except IndexError:
                pass

        self.create_motionmap()
        self.create_sightmap()


class MazeMap(Terrain):
    def __init__(self, id=0):
        super().__init__(id)
    
    def random_unblocked_loc(self):
        # Select from only even x/y tiles locations
        # ensures location will be unblocked on new maze levels
        return random.choice([(x * 2, y * 2) for x in range(self.width//2) for y in range(self.height//2)])

    def cardinal_neighbours(self, loc):
        x, y = loc
        locs = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        while locs:
            # Return in random order
            x, y = locs.pop(random.randint(0, len(locs)-1))
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                yield Location(x, y) 

    def build_graph(self, width, height):
        sx = random.randrange(0, (self.width))
        sy = random.randrange(0, (self.height))
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
            for n in self.cardinal_neighbours(loc):
                if n in graph and not connected:
                    graph[loc] = set([n])
                    graph[n].add(loc)
                    connected = True
                if n not in visited:
                    frontier.add(n)

        return graph

    def build(self, entry_loc=None):
        if self.width % 2 == 0 or self.height % 2 == 0:
            raise ValueError('mazeMap must be odd width and height.')
        # Build new graph and clear existing tiles
        graph = self.build_graph((self.width // 2) + 1, (self.height // 2) + 1)
        
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

        
        self.create_motionmap()
        self.create_sightmap()