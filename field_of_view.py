
# Shadowcasting method to calculate visible tiles
# pov: point of view from which to cast shadows
# vismap: visibility map: dict of sight non/blocking locations (False = blocking)
# radius: max visible distance

def scan(pov, vismap, radius=16):
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
        visible += _scan_octant(pov, vismap, radius, transform = t)
    
    return visible

def _scan_octant(pov, vismap, radius, start = 0, end = 1, distance = 0, transform = [1, 1, 0, 0]):
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
                visible += _scan_octant(pov, vismap, radius, start, end, dist, transform)
            break
        scan_queue = []

        for j in range(0, dist + 1):
            # Map location is translated to octant
            loc = (
                sx + dist * xx + j * xy, 
                sy + j * yy + dist * yx
            )
        
            # Test if coordinate is valid map location
            if loc not in vismap:
                continue
                            
            angle_min = min((j - 0.5) / (dist - 0.5), (j - 0.5) / (dist + 0.5)) 
            angle_max = (j + 0.5) / (dist - 0.5)
            
            if angle_min > end:
                break
            
            if start < angle_max:
                visible.append(loc)
                
                if vismap[loc] == False:
                    final = True
                    if start < angle_min:
                        scan_queue.append((start, angle_min))
                    start = angle_max
                elif final and angle_max > end:
                    scan_queue.append((start, end))
    
    return visible