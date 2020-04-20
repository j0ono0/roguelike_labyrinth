
# Shadowcasting method to calculate visible tiles
# pov: point of view from which to cast shadows
# DEPRECIATED__vismap: visibility map: dict of sight non/blocking locations (False = blocking)
# radius: max visible distance

def scan(pov, sightmap, radius=16):
    visible = [pov]
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
        visible += _scan_octant(pov, sightmap, radius, transform = t)
    
    return visible

def _scan_octant(pov, sightmap, radius, start = 0, end = 1, distance = 0, transform = [1, 1, 0, 0]):
    xx, yy, xy, yx = transform
    sx, sy = pov
    visible = []
    final = False
    scan_queue = []
    # Examine tiles in row
    for dist in range(distance, radius):
        if final:
            # Note: at this line 'dist' is +1 from when 'final' was detected!
            for start, end in scan_queue:
                visible += _scan_octant(pov, sightmap, radius, start, end, dist, transform)
            break
        scan_queue = []

        for j in range(0, dist + 1):
            # Map location is translated to octant
            x = sx + dist * xx + j * xy
            y = sy + j * yy + dist * yx
        
            # Test if coordinate is valid map location
            if  not 0 <= x < len(sightmap) or not 0 <= y < len(sightmap[0]):
                continue
                            
            angle_min = min((j - 0.5) / (dist - 0.5), (j - 0.5) / (dist + 0.5)) 
            angle_max = (j + 0.5) / (dist - 0.5)
            
            if angle_min > end:
                break
            
            if start < angle_max:
                visible.append((x, y))
                
                if sightmap[x][y] == False:
                    final = True
                    if start < angle_min:
                        scan_queue.append((start, angle_min))
                    start = angle_max
                elif final and angle_max > end:
                    scan_queue.append((start, end))
    
    return visible