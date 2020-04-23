"""
Utilities file for snake logic.
"""
import app.algs

NAME = "ACHultman / Fer-de-lance"
FOOD = 2
WALKABLE = 1
SNAKE = -1
HEAD = -2
TAIL = 0


def distance(p, q):
    """
    Helper function for finding Manhattan distance between two cartesian points.
    """
    # print('p: ', p)
    # print('q: ', q)
    dx = abs(int(p[0]) - q[0])
    dy = abs(int(p[1]) - q[1])
    return dx + dy


def closest(items, ref):
    """
    Helper function for finding closest item from reference point.
    """
    closest_item = None
    closest_distance = 10000

    # TODO: use builtin min for speed up
    for item in items:
        # print('item: ', item)
        item_distance = distance(ref, item)
        if item_distance < closest_distance:
            closest_item = item
            closest_distance = item_distance

    return closest_item, closest_distance


def direction(path):
    """
    :param path:
    :return: "up", "down", "left", or "right"
    """
    try:
        x_delta = path[1][0] - path[0][0]  # Get delta of the first two path x coordinates.
        y_delta = path[1][1] - path[0][1]  # Get delta of the first two path y coordinates.
    except IndexError:
        # print("It appears there is no path.")
        return "no path"  # TODO Implement smarter method

    if x_delta is 1:
        return "right"
    elif x_delta is -1:
        return "left"
    elif y_delta is -1:
        return "up"
    elif y_delta is 1:
        return "down"
    else:
        raise RuntimeError('No return direction found in direction(path) where path = ' + str(path))


def is_dead_end(pos, grid, data, snake):
    tail_vals = []
    area_size, tails, heads = app.algs.bfs(grid, data, pos)
    #neighbours = app.algs.get_vertex_neighbours(data, grid, pos)
    #for neighbour in neighbours:
    #    if grid[neighbour[1]][neighbour[0]]
    for tail in tails:
        tail_vals.append(grid[tail[1]][tail[0]])
    if TAIL in tail_vals:
        print('is_dead_end found tail, returning false')
        print('tails: ', tails)
        print('pos in question: ', pos)
        return False
    elif area_size <= snake.size + 1:  # TODO Account for moving tail
        # Look backwards from tail to find first body part on edge of area
        print('Looks like dead-end, size: ', area_size)
        return True
    else:
        print('No dead end found at ', pos)
        return False


def adj_food(pos, data, grid):
    neighbours = app.algs.get_vertex_neighbours(pos, data, grid)
    for neighbour in neighbours:
        if grid[neighbour[1]][neighbour[0]] == 2:
            return True
    return False


def is_adjacent(coord, snake_head, data, grid):
    neighbours = app.algs.get_vertex_neighbours(coord, data, grid)
    if snake_head in neighbours:
        print('Head next to tail')
        return True
    else:
        return False

