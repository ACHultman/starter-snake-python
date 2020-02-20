"""
Utilities file for snake logic.
"""
import astarsearch


def in_bounds(x, y, data):
    limit = data['board']['height'] - 1
    if x > limit or x < 0 or y > limit or y < 0:
        return False
    else:
        return True


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


def enemy_size(pos, data):
    """
    Finds enemy snake at given position and returns its size.
    :param pos: position of enemy snake
    :param data: game data
    :return: size of snake at the position
    """
    snakes = data['board']['snakes']
    for snake in snakes:
        for coord in snake['body']:
            # print('pos==coord? ', pos, coord)
            if pos == (coord['x'], coord['y']):
                # print('enemy_size is ', len(snake['body']))
                return len(snake['body'])
    raise RuntimeError('No snake found in enemy_size')


def is_dead_end(pos, grid, data, snake):
    if astarsearch.bfs(grid, data, pos) <= len(snake['body']):
        return True
    else:
        return False
