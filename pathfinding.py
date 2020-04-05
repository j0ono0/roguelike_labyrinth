import heapq
import math

def distance(start, end, manhattan=False):
        sx, sy = start
        ex, ey = end
        if manhattan:
            return abs(ey - sy) + abs(ex - sx)
        else:
            return math.sqrt((ey - sy)**2 + (ex - sx)**2)

def cardinal_neighbours(x, y):
        return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    
def astar(graph, start, end):
    # Algorith starts at destination and works backwards to find current location
    frontier = []
    # Items are tuple: (<priority>, <location>)
    heapq.heappush(frontier, (0, start))
    visited = {start: None}
    cost_tally = {start: 0}
    
    while len(frontier) > 0:
        current = heapq.heappop(frontier)[1]

        if current == end:
            # Extract shortest path from visited
            path = []
            while current != start:
                path.append(current)
                current = visited[current]
            #path.append(start)
            return path

        for loc in cardinal_neighbours(*current):
            try:
                if graph[loc] == True:
                    priority = cost_tally[current] + distance(end, loc)
                    if loc not in visited or priority < cost_tally[loc]:
                        cost_tally[loc] = priority
                        heapq.heappush(frontier, (priority, loc))
                        visited[loc] = current
            except KeyError:
                """ coordinates out of map area """
            
    return []
    