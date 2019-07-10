import random
from collections import namedtuple
import tcod
from . import maze

Location = namedtuple('Location',['x', 'y'])

class TileMap():
    def __init__(self, width, height):
        self.level = 0
        self.width = width
        self.height = height
        self.fov = FieldOfView(self)
        self.graph = None
        self.titles = None
        self.entry = None
        self.exit = None
        
    def random_tile_loc(self):
        x = random.randrange(0, (self.width))
        y = random.randrange(0, (self.height))
        return Location(x, y)
    
    def build(self):
        # Build new graph and clear existing tiles
        self.graph = maze.build_graph(self.width // 2, self.height // 2)
        self.tiles = {(x,y): Tile('#', True) for x in range(self.width) for y in range(self.height)}
        
        # Update tiles from graph data
        for loc, edges in self.graph.items():
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
        
        # Place entry and exit on unblocked tiles
        self.entry = self.exit or [i * 2 + 1 for i in random.choice(list(self.graph.keys()))]
        self.exit = [i * 2 + 1 for i in random.choice(list(self.graph.keys()))]
    
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