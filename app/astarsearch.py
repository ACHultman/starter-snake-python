"""
Edited A* search code from https://rosettacode.org/wiki/A*_search_algorithm#Python
"""
from utils import *
from collections import deque


class AStarGraph(object):
    barriers = None  # type: List[Any]

    # Define a board-like grid

    def __init__(self):
        self.graph = [[]]
        self.barriers = []

    def heuristic(self, start, goal):
        # Use Manhattan distance heuristic
        # print('HEURISTIC')
        # print('start: ', start)
        # print('goal: ', goal)
        dx = abs(start[0] - goal[0])
        dy = abs(start[1] - goal[1])
        # print('dx + dy = ', dx+dy)
        # print('')
        return dx + dy

    def get_vertex_neighbours(self, pos, data, grid):
        n = []
        # Moves allowed are Manhattan-style
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x2 = pos[0] + dx
            y2 = pos[1] + dy
            if not in_bounds(x2, y2, data):
                continue
            elif grid.graph[y2][x2] == -1:
                continue
            n.append((x2, y2))
        return n

    def move_cost(self, b):
        # print('self.barriers: ', self.barriers)
        for barrier in self.barriers:
            if b == barrier:
                return 100000  # Extremely high cost to enter barrier squares
        return 1  # Normal movement cost


def AStarSearch(start, end, graph, data):
    # print('*********ASTARSEARCH***********')
    # print('start: ', start)
    # print('end: ', end)
    # print('barriers: ', graph.barriers)
    G = {}  # Actual movement cost to each position from the start position
    F = {}  # Estimated movement cost of start to end going via this position
    # Initialize starting values
    G[start] = 0
    F[start] = graph.heuristic(start, end)

    closedVertices = set()
    openVertices = set([start])
    cameFrom = {}

    while len(openVertices) > 0:
        # Get the vertex in the open list with the lowest F score
        current = None
        # print('current: ', current)
        currentFscore = None
        for pos in openVertices:
            if current is None or F[pos] < currentFscore:
                currentFscore = F[pos]
                current = pos
        # print('current: ', current)
        # Check if we have reached the goal
        if current == end:
            # Retrace our route backward
            path = [current]
            while current in cameFrom:
                current = cameFrom[current]
                path.append(current)
            path.reverse()
            # print('path: ', path)
            return path, F[end]  # Done!

        # Mark the current vertex as closed
        openVertices.remove(current)
        closedVertices.add(current)

        # Update scores for vertices near the current position
        for neighbour in graph.get_vertex_neighbours(current, data, graph):
            if neighbour in closedVertices:
                continue  # We have already processed this node exhaustively
            candidateG = G[current] + 1

            if neighbour not in openVertices:
                openVertices.add(neighbour)  # Discovered a new vertex

            elif candidateG >= G[neighbour]:
                continue  # This G score is worse than previously found
            elif candidateG > 100:
                continue

            # Adopt this G score
            cameFrom[neighbour] = current
            G[neighbour] = candidateG
            H = graph.heuristic(neighbour, end)
            F[neighbour] = G[neighbour] + H
            # print('neighbour: :', neighbour)
            # print('F[neighbour]', F[neighbour])
            # print('current: ', current)
    path = [start]
    return path, 0


def bfs(grid, data, start):
    count = 1
    queue = deque([start])
    visited = set()
    while queue:
        curr_node = queue.popleft()
        visited.add(curr_node)

        neighbours = grid.get_vertex_neighbours(curr_node, data, grid)
        for neighbour in neighbours:
            if neighbour not in visited:
                count = count + 1
                visited.add(neighbour)
                queue.append(neighbour)
    return count
