"""
Edited A* search code from https://rosettacode.org/wiki/A*_search_algorithm#Python
"""
from collections import deque

from app.board import *

FOOD = 2
WALKABLE = 1
SNAKE = -1
HEAD = -2
ADJ_HEAD = -3
TAIL = 0


def get_vertex_neighbours(pos, data, grid, all_types):
    n = []
    # Moves allowed are Manhattan-style
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        x2 = pos[0] + dx
        y2 = pos[1] + dy
        if not in_bounds(x2, y2, data):
            continue
        elif not all_types and grid[y2][x2] in (SNAKE, HEAD):
            continue
        n.append((x2, y2))
    return n


def heuristic(start, goal):
    # Use Manhattan distance heuristic
    dx = abs(start[0] - goal[0])
    dy = abs(start[1] - goal[1])
    return dx + dy


class AStarGraph(object):
    barriers = None  # type: List[Any]

    # Define a board-like grid

    def __init__(self):
        self.graph = [[]]
        self.barriers = []


def astarsearch(start, end, grid, data):
    # print('*********ASTARSEARCH***********')
    # print('start: ', start)
    # print('end: ', end)
    G = {}  # Actual movement cost to each position from the start position
    F = {}  # Estimated movement cost of start to end going via this position
    # Initialize starting values
    G[start] = 0
    F[start] = heuristic(start, end)

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
        for neighbour in get_vertex_neighbours(current, data, grid, False):
            if neighbour in closedVertices:
                continue  # We have already processed this node exhaustively
            candidateG = G[current] + 1

            if neighbour not in openVertices:
                openVertices.add(neighbour)  # Discovered a new vertex

            elif candidateG >= G[neighbour]:
                continue  # This G score is worse than previously found

            # Adopt this G score
            cameFrom[neighbour] = current
            G[neighbour] = candidateG
            H = heuristic(neighbour, end)
            F[neighbour] = G[neighbour] + H
            # print('neighbour: :', neighbour)
            # print('F[neighbour]', F[neighbour])
            # print('current: ', current)
    path = [start]
    return path, 0


def bfs(grid, data, start):
    count = 1
    bodies = []
    tails = []
    has_adj = False
    queue = deque([start])
    if grid[start[1]][start[0]] == 0:
        tails.append(start)
    visited = set()
    while queue:
        curr_node = queue.popleft()
        visited.add(curr_node)
        neighbours = get_vertex_neighbours(curr_node, data, grid, all_types=True)
        for neighbour in neighbours:
            if grid[neighbour[1]][neighbour[0]] in (HEAD, SNAKE):
                bodies.append(neighbour)
                continue
            if grid[neighbour[1]][neighbour[0]] == ADJ_HEAD:
                has_adj = True
                #print('bfs found adj_head at ', neighbour)
                continue
            if grid[neighbour[1]][neighbour[0]] == TAIL:  # TODO also count heads
                tails.append(neighbour)
            if neighbour not in visited:
                count = count + 1
                visited.add(neighbour)
                queue.append(neighbour)
    return count, tails, bodies, has_adj
