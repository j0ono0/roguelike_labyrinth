import heapq
import math
from collections import deque

def distance(start, end, manhattan=False):
        sx, sy = start
        ex, ey = end
        if manhattan:
            return abs(ey - sy) + abs(ex - sx)
        else:
            return math.sqrt((ey - sy)**2 + (ex - sx)**2)

def cardinal_neighbours(graph, x, y):
        locs = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        while locs:
            loc = locs.pop()
            if loc in graph and not graph[loc].blocked:
                yield loc

    
def neighbours(graph, id):
    (x, y) = id
    n = []
    for dx in range(x-1, x+2):
        for dy in range(y-1, y+2):
            if graph[(dx, dy)] and graph[(dx, dy)].blocked == False and (dx, dy) != id:
                n.append((dx, dy))
    return n
    
def astar_path(graph, start, end):
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

        for next in cardinal_neighbours(graph, *current):
            priority = cost_tally[current] + distance(end, next)
            if next not in visited or priority < cost_tally[next]:
                cost_tally[next] = priority
                heapq.heappush(frontier, (priority, next))
                visited[next] = current
    return []
    