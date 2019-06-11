import random
import tcod


class PrimsMaze():
    def __init__(self, width = 20, height = 20):
        self.width = width
        self.height = height
        self.tiles = None
        self.entry = None
        self.exit = None
    
    def random_loc(self):
        x = random.randrange(1, (self.width - 1), 2)
        y = random.randrange(1, (self.height -1 ), 2)
        return (x, y)
    
    def build(self):
        self.entry = self.exit or self.random_loc()
        self.exit = self.random_loc()
        self.tiles = {(x,y): Tile('#', True) for x in range(self.width) for y in range(self.height)}
        
        x_range = range(1, (self.width - 1), 2)
        y_range = range(1, (self.height -1 ), 2)
        graph = {(x,y): None for x in x_range for y in y_range}
        start = self.random_loc()
        graph[start] = start
        frontier = [start]
        
        while frontier:
            loc = frontier.pop(random.randint(0, len(frontier)-1))
            cn = self.cardinal_neighbours(*loc)
            random.shuffle(cn)
            for path in cn:
                if graph[path] != None:
                    graph[loc] = path
                elif path not in frontier:
                    frontier.append(path)
        # Update tiles
        for t, k in graph.items():
            tx, ty = t
            kx, ky = k or t
            for x in range(min(tx, kx), max(tx, kx) + 1):
                for y in range(min(ty, ky), max(ty, ky) + 1):
                    self.tiles[(x, y)].glyph = ' '
                    self.tiles[(x, y)].blocked = False

    def cardinal_neighbours(self, x, y):
        locs = [(x-2, y), (x+2, y), (x, y-2), (x, y+2)]
        valid = []
        for loc in locs:
            if loc in self.tiles:
                valid.append(loc)
        return valid

    def con(self):
        con = tcod.console.Console(self.width, self.height, order='F')
        for k, t in self.tiles.items():
            con.tiles[k] = (
                ord(t.glyph),
                (100, 100, 100, 255),
                (*tcod.black, 255)
            )
        return con
        

class Tile:
    def __init__(self, glyph='#', blocked=True):
        self.glyph = glyph
        self.blocked = blocked