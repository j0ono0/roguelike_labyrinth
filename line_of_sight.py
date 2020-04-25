import math

class LineOfSight:
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
        
    @property
    def step_lengths(self):
        x0, y0, x1, y1  = *self.p0, *self.p1
        xlen = x1 - x0
        ylen = y1 - y0
        longer = max(abs(xlen), abs(ylen))
        return (xlen / longer, ylen / longer)
        
    @property
    def longer_dimension(self,):
        x0, y0, x1, y1 = *self.p0, *self.p1
        return max(abs(x1 - x0), abs(y1 - y0)) + 1
        
    def round_point(self, p):
        x, y = p
        # Note weird rounding to force odd and even numbers to round x.5 up always
        if x%0.5 != 0:
            x = round(x) 
        else:
            x = math.floor(x)
            
        if y%0.5 != 0:
            y = round(y)
        else:
            y = math.floor(y)
            
        return (x, y)

    def path(self, steps=None, map=None):
        steps = steps or self.longer_dimension
        xstep, ystep = self.step_lengths
        x, y = self.p0
        path = []
        for t in range(steps):
            tx, ty = self.round_point((x + t * xstep, y + t * ystep))
            if map and map[tx][ty] == False:
                    break
            path.append((tx,ty))
        return path
        
        
if __name__ == '__main__':
    p0 = (0, 0)
    p1 = (5, 2)
    line = LineOfSight(p0, p1)
    print('path:',line.path())