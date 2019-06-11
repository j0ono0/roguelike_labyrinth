import random
import tcod

from .map import Tile, FieldOfView

class Dungeon:
    def __init__(self, width = 20, height = 20):
        self.fov = FieldOfView(self)
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
        
        for x in range(2, self.width - 2):
            for y in range(2, self.height - 2):
                self.tiles[(x, y)] = Tile('.', False)
                
        
        for x in range(10, 12):
            for y in range(14, 16):
                self.tiles[(x, y)] = Tile('#', True)
                
        
        for x in range(12, 14):
            for y in range(8, 11):
                self.tiles[(x, y)] = Tile('$', True)
                
        self.entry = (3,3)
        self.exit = (3,5)
        

    def con(self):
        con = tcod.console.Console(self.width, self.height, order='F')
        for k, t in self.tiles.items():
            if t.visible:
                con.tiles[k] = (
                    ord(t.glyph),
                    #(100, 100, 100, 255),
                    (255, 255, 255, 255),
                    (*tcod.black, 255)
                )
        return con
        
