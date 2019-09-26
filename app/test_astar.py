from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import numpy as np

NAME = "ACHultman / Fer-de-lance"
WALKABLE = 1
SNAKE = -1
FOOD = 2


def distance(p, q):
    """
    Helper function for finding Manhattan distance between two cartesian points.
    """
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
        item_distance = distance(ref, item)
        if item_distance < closest_distance:
            closest_item = item
            closest_distance = item_distance

    return closest_item


def direction(path):
    """
    :param path:
    :return: "up", "down", "left", or "right"
    """
    x_delta = path[1][0] - path[0][0]  # Get delta of the first two path x coordinates.
    y_delta = path[1][1] - path[0][1]  # Get delta of the first two path y coordinates.

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


data = \
    {

        'you': {
            'body': [
                {
                    'y': 10,
                    'x': 10
                },
                {
                    'y': 9,
                    'x': 10
                },
                {
                    'y': 9,
                    'x': 9
                },
                {
                    'y': 9,
                    'x': 8
                },
                {
                    'y': 8,
                    'x': 8
                },
                {
                    'y': 7,
                    'x': 8
                },
                {
                    'y': 6,
                    'x': 8
                },
                {
                    'y': 5,
                    'x': 8
                },
                {
                    'y': 4,
                    'x': 8
                },
                {
                    'y': 3,
                    'x': 8
                },
                {
                    'y': 3,
                    'x': 7
                },
                {
                    'y': 3,
                    'x': 7
                }
            ],
            'health': 100,
            'id': 'gs_qtpgYWvxRP4QxDJJQKvybbKB',
            'name': 'ACHultman / Fer-de-lance'
        },
        'turn': 60,
        'game': {
            'id': 'b48b201e-bcbc-4689-bfdd-20cb893ed300'
        },
        'board': {
            'food': [

            ],
            'width': 11,
            'snakes': [
                {
                    'body': [
                        {
                            'y': 1,
                            'x': 9
                        },
                        {
                            'y': 1,
                            'x': 8
                        },
                        {
                            'y': 0,
                            'x': 8
                        }
                    ],
                    'health': 40,
                    'id': 'gs_DxpxxhbGGjkqdTWDdKDRD6CY',
                    'name': 'shoya4000 / Battlesnake-Hordes'
                },
                {
                    'body': [
                        {
                            'y': 10,
                            'x': 10
                        },
                        {
                            'y': 9,
                            'x': 10
                        },
                        {
                            'y': 9,
                            'x': 9
                        },
                        {
                            'y': 9,
                            'x': 8
                        },
                        {
                            'y': 8,
                            'x': 8
                        },
                        {
                            'y': 7,
                            'x': 8
                        },
                        {
                            'y': 6,
                            'x': 8
                        },
                        {
                            'y': 5,
                            'x': 8
                        },
                        {
                            'y': 4,
                            'x': 8
                        },
                        {
                            'y': 3,
                            'x': 8
                        },
                        {
                            'y': 3,
                            'x': 7
                        },
                        {
                            'y': 3,
                            'x': 7
                        }
                    ],
                    'health': 100,
                    'id': 'gs_qtpgYWvxRP4QxDJJQKvybbKB',
                    'name': 'ACHultman / Fer-de-lance'
                }
            ],
            'height': 11
        }
    }
'''
grid = Grid(matrix=matrix)

finder = AStarFinder()
path, runs = finder.find_path(start, end, grid)

print('operations:', runs, 'path length:', len(path))
print(grid.grid_str(path=path, start=start, end=end))
print(path)
'''


def init(datas):
    """
    Function for initializing the board.
    """
    json_data_board = datas['board']
    height = json_data_board['height']
    you = datas['you']  # Dictionary for own snake

    grid = [[1 for col in range(height)] for row in range(height)]
    print(np.matrix(grid))  # initialize 2d grid
    for snake in json_data_board['snakes']:
        if snake['name'] is not you['name']:
            for coord in snake['body']:
                grid[coord['y']][coord['x']] = SNAKE  # Documents other snake's bodies for later evasion.
        else:
            next(iter(snake['body']))  # Skips adding own snake's head to snake body grid.
            tail_coord = None
            print("Is there food? Answer: " + str(json_data_board['food']))
            for coord in snake['body']:
                grid[coord['y']][coord['x']] = SNAKE
                tail_coord = (coord['y'], coord['x'])
            if not json_data_board['food']:
                grid[tail_coord[0]][tail_coord[1]] = WALKABLE
                print("Tail now walkable: y: " + str(tail_coord[0]) + " x: " + str(tail_coord[1]))
    for food in json_data_board['food']:  # For loop for marking all food on grid.
        grid[food['y']][food['x']] = FOOD

    astar_grid = Grid(matrix=grid)

    return you, grid, astar_grid


def move():
    snake, grid, astar_grid = init(data)
    print(np.matrix(grid))
    json_data_board = data['board']

    print("Snake head x: " + str(snake['body'][0]['x']) + " snake head y: " + str(snake['body'][0]['y']))
    print("nodes" + str(astar_grid.nodes))

    snake_tail = (snake['body'][-1]['x'], snake['body'][-1]['y'])
    snake_head = (snake['body'][0]['x'], snake['body'][0]['y'])  # Coordinates for own snake's head
    source = astar_grid.node(snake_head[0], snake_head[1])

    foods = []  # Tuple list of food coordinates
    for food in data['board']['food']:
        x = food['x']
        y = food['y']
        foods.append((x, y))

    # middle = [data['width'] / 2, data['height'] / 2]
    # foods = sorted(data['food'], key=lambda p: distance(p, middle))
    foods = sorted(foods, key=lambda p: distance(p, snake_head))  # Sorts food list by distance to snake's head
    target = None
    path = None
    finder = AStarFinder()  # Initialize AStarFinder
    for food in foods:
        target = astar_grid.node(food[0], food[1])
        path, runs = finder.find_path(source, target, astar_grid)  # get A* shortest path
        if not path:
            # print "no path to food"
            continue
        else:
            print("Path to food: " + str(path))
            break

    if not path:
        print("Snake Tail x: " + str(snake_tail[0]) + " y: " + str(snake_tail[1]))
        target = astar_grid.node(snake_tail[0], snake_tail[1])  # Make target snake's own tail
        path, runs = finder.find_path(source, target, astar_grid)  # get A* shortest path to tail
        print("Path to tail:" + str(path))

    path_length = len(path)
    # snek_length = len(snake_coords) + 1
    '''
        in_trouble = False
        for enemy in json_data_board['snakes']:
            if enemy['name'] == NAME:
                continue
            if path_length > distance((enemy['body'][0]['x'], enemy['body'][0]['y']), food):
                in_trouble = True
        if in_trouble:
            continue
    '''
    print(path)

    print('path length:', path_length)
    print(astar_grid.grid_str(path=path, start=source, end=target))
    print(path)
    print(direction(path))


move()
