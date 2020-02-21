"""
Utilities file for snake logic.
"""
import algs

NAME = "ACHultman / Fer-de-lance"
FOOD = 2
WALKABLE = 1
SNAKE = -1
HEAD = -2
TAIL = 0


def in_bounds(x, y, data):
    limit = data['board']['height'] - 1
    if x > limit or x < 0 or y > limit or y < 0:
        return False
    else:
        return True


def grid_init(data):
    """
    Function for initializing the board.
    """
    json_data_board = data['board']
    height = json_data_board['height']
    you = data['you']  # Dictionary for own snake
    barriers = []
    enemy_head = []
    grid = [[1 for col in range(height)] for row in range(height)]  # initialize 2d grid
    for snake in json_data_board['snakes']:

        if snake['name'] != you['name']:
            for coord in snake['body']:
                coord = (coord['x'], coord['y'])

                if coord == (snake['body'][0]['x'], snake['body'][0]['y']):
                    enemy_head = coord
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                        x2 = coord[0] + dx
                        y2 = coord[1] + dy
                        if not in_bounds(x2, y2, data):
                            continue
                        # barriers.append((x2, y2))
                        grid[coord[1]][coord[0]] = HEAD
                    continue
                elif coord == (snake['body'][-1]['x'], snake['body'][-1]['y']):
                    if adj_food(enemy_head, data, grid):
                        grid[coord[1]][coord[0]] = SNAKE
                    grid[coord[1]][coord[0]] = TAIL
                    continue
                else:
                    grid[coord[1]][coord[0]] = SNAKE  # Documents other snake's bodies for later evasion.
                    barriers.append((coord[0], coord[1]))

        else:
            for coord in snake['body']:  # Skip adding own tail to barriers in this loop
                if coord is not snake['body'][-1]:
                    grid[coord['y']][coord['x']] = SNAKE
                    barriers.append((coord['x'], coord['y']))

    for food in json_data_board['food']:  # For loop for marking all food on grid.
        grid[food['y']][food['x']] = FOOD

    return you, grid, barriers


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


def get_enemy(pos, data):
    snakes = data['board']['snakes']
    for snake in snakes:
        for coord in snake['body']:
            # print('pos==coord? ', pos, coord)
            if pos == (coord['x'], coord['y']):
                return snake
    print('No snake found there')
    return None


def enemy_size(pos, data):
    """
    Finds enemy snake at given position and returns its size.
    :param pos: position of enemy snake
    :param data: game data
    :return: size of snake at the position
    """
    snake = get_enemy(pos, data)
    if snake:
        return len(snake['body'])
    else:
        raise RuntimeError('No snake found in enemy_size')


def is_dead_end(pos, grid, data, snake):
    if algs.bfs(grid, data, pos) <= len(snake['body']) + 1:
        return True
    else:
        return False


def adj_food(pos, data, grid):
    neighbours = algs.get_vertex_neighbours(pos, data, grid)
    for neighbour in neighbours:
        if grid[neighbour[1]][neighbour[0]] == 2:
            return True
    return False
