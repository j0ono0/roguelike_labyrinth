
class Tile:
    def __init__(self, glyph='#', blocked=True):
        self.glyph = glyph
        self.blocked = blocked
        self.visible = False
        
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