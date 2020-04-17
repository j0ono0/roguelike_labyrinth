import heapq
import math
from settings import *

def distance(start, end, manhattan=False):
        sx, sy = start
        ex, ey = end
        if manhattan:
            return abs(ey - sy) + abs(ex - sx)
        else:
            return math.sqrt((ey - sy)**2 + (ex - sx)**2)


def cardinal_neighbours(x, y):
        return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    

def neighbours(valid_locs, x, y):
    return [(dx, dy) for dx in range(x-1, x+2) for dy in range(y-1, y+2) if (dx, dy) in valid_locs and (dx, dy) != (x, y)]


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

        for loc in neighbours(graph, *current):
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
    
def dijkstra(graph, start):
    # create a dijkstra map calculating cost of moving
    # 'start' is a dict of coordinates (keys) and movement costs for location (values)
    # 'graph' is a list of valid locations in form of a tuple (x, y)
    frontier = []
    visited = {}
    cost_tally = {}
    
    for key, value in start.items():
        heapq.heappush(frontier, (value,key))
        visited[key] = None
        cost_tally[key] = value
        
    while len(frontier) > 0:
        current = heapq.heappop(frontier)[1]
        for next in neighbours(graph, *current):
            priority = cost_tally[current] + 1
            if next not in visited or priority < cost_tally[next]:
                cost_tally[next] = priority
                visited[next] = current
                heapq.heappush(frontier, (priority, next))
    return (visited, cost_tally)
