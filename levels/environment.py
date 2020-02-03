import random
import copy
from collections import namedtuple
import tcod

Location = namedtuple('Location',['x', 'y'])

class Map():
    def __init__(self, width, height, entry=None, id=0):
        self.id = id
        self.width = width
        self.height = height
        self.fov = FieldOfView(self)
        self.tiles = None
        self.entities = []
    
    def random_empty_loc(self):
        entity_locs = [e.loc for  e in self.entities]
        return random.choice([k for k, v in self.tiles.items() if not v.blocked and k not in entity_locs])

    def random_unblocked_loc(self):
        return random.choice([k for k, v in self.tiles.items() if not v.blocked])

    def fill_tiles(self, tile):
        self.tiles = {(x,y): copy.copy(tile) for x in range(self.width) for y in range(self.height)}
    
    def random_tile_loc(self):
        x = random.randrange(0, (self.width))
        y = random.randrange(0, (self.height))
        return Location(x, y)
    
    def con(self):
        con = tcod.console.Console(self.width, self.height, order='F')
        for k, t in self.tiles.items():
            if t.visible:
                con.tiles[k] = (
                    ord(t.glyph),
                    (100, 100, 100, 255),
                    (27, 27, 27, 255)
                )
            elif t.seen:
                con.tiles[k] = (
                    ord(t.glyph),
                    (70, 70, 70, 255),
                    (*tcod.black, 255)
                )
        return con

class MazeMap(Map):
    def __init__(self, width, height, entry=None, id=0):
        super().__init__(width, height, entry, id)
        self.build()
    
    def random_unblocked_loc(self):
        # Select from only odd x/y tiles locations
        # ensures location will be unblocked on new maze levels
        return random.choice([(x * 2 + 1, y * 2 + 1) for x in range(self.width//2) for y in range(self.height//2)])

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
        # Build new graph and clear existing tiles
        graph = self.build_graph((self.width-1) // 2, (self.height-1) // 2)
        self.fill_tiles(Tile('#', True))
        
        # Update tiles from graph data
        for loc, edges in graph.items():
            path = [(loc.x * 2, loc.y * 2)]
            for (x, y) in edges:
                dx = x - loc.x
                dy = y - loc.y
                path.append((loc.x * 2 + dx, loc.y * 2 + dy))
            for p in path:
                # offset tiles by +1 to create solid border
                p = (p[0] + 1, p[1] + 1)
                self.tiles[p].glyph = '.'
                self.tiles[p].blocked = False

class Tile:
    def __init__(self, glyph='#', blocked=True):
        self.glyph = glyph
        self.blocked = blocked
        self.visible = False
        self.seen = False
        
        
class FieldOfView:
    # Shadowcasting method to calculate visible tiles
    
    def __init__(self, parent, radius = 16):
        self.parent = parent
        self.radius = radius
        print('initilizing fov')
    
    def scan(self, source):
        visible = [source]
        # Transformation multipliers [xx, yy, xy, yx]
        octant_transforms = [
            [ 1,  1,  0,  0],
            [-1,  1,  0,  0],
            [ 1, -1,  0,  0],
            [-1, -1,  0,  0],
            [ 0,  0,  1,  1],
            [ 0,  0, -1,  1],
            [ 0,  0,  1, -1],
            [ 0,  0, -1, -1],
        ]
        
        for t in octant_transforms:
            visible += self.scan_octant(source, transform = t)
        
        # Update tiles of parent map
        for k, v in self.parent.tiles.items():
            if k in visible:
                v.visible = True
                v.seen = True
            else:
                v.visible = False
    
    def scan_octant(self, source, start = 0, end = 1, distance = 0, transform = [1, 1, 0, 0]):
        xx, yy, xy, yx = transform
        sx, sy = source
        visible = []
        final = False
        scan_queue = []
        # Examine tiles in row
        for dist in range(distance, self.radius):
            if final:
                # Note: at this line 'dist' is +1 from when 'final' was detected!
                for start, end in scan_queue:
                    visible += self.scan_octant(source, start, end, dist, transform)
                break
            scan_queue = []

            for j in range(0, dist + 1):
                # Map location is translated to octant
                loc = (
                    sx + dist * xx + j * xy, 
                    sy + j * yy + dist * yx
                )
            
                # Test if coordinate is valid map location
                if loc not in self.parent.tiles:
                    continue
                                
                angle_min = min((j - 0.5) / (dist - 0.5), (j - 0.5) / (dist + 0.5)) 
                angle_max = (j + 0.5) / (dist - 0.5)
                
                if angle_min > end:
                    break
                
                if start < angle_max:
                    visible.append(loc)
                    
                    if self.parent.tiles[loc].blocked:
                        final = True
                        if start < angle_min:
                            scan_queue.append((start, angle_min))
                        start = angle_max
                    elif final and angle_max > end:
                        scan_queue.append((start, end))
        
        return visible      