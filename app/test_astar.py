from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import numpy as np

NAME = "ACHultman / Fer-de-lance"
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
        "board": {
            "snakes": [
                {
                    "health": 100,
                    "id": "gs_c8yh3Tf46hkvKG7TchrBkFj3",
                    "body": [
                        {
                            "y": 1,
                            "x": 1
                        },
                        {
                            "y": 1,
                            "x": 1
                        },
                        {
                            "y": 1,
                            "x": 1
                        }
                    ],
                    "name": "ruqaiya / fassst"
                },
                {
                    "health": 100,
                    "id": "gs_Bfv7CPym9Dy7Cm694SKgWhX3",
                    "body": [
                        {
                            "y": 9,
                            "x": 9
                        },
                        {
                            "y": 9,
                            "x": 9
                        },
                        {
                            "y": 9,
                            "x": 9
                        }
                    ],
                    "name": "dmoneyUK / JDSnake"
                },
                {
                    "health": 100,
                    "id": "gs_CSpYdFvRWvKSHgjYF6b3J6SB",
                    "body": [
                        {
                            "y": 9,
                            "x": 1
                        },
                        {
                            "y": 9,
                            "x": 1
                        },
                        {
                            "y": 9,
                            "x": 1
                        }
                    ],
                    "name": "noalbalint / qwertyman1"
                },
                {
                    "health": 100,
                    "id": "gs_FHjMJSxDHpjMkBbPm4WT7RpY",
                    "body": [
                        {
                            "y": 1,
                            "x": 9
                        },
                        {
                            "y": 1,
                            "x": 9
                        },
                        {
                            "y": 1,
                            "x": 9
                        }
                    ],
                    "name": "geekforbrains / Outlander"
                },
                {
                    "health": 100,
                    "id": "gs_x9GPq4GSp6J3J8bRBMcF9mx3",
                    "body": [
                        {
                            "y": 1,
                            "x": 5
                        },
                        {
                            "y": 1,
                            "x": 5
                        },
                        {
                            "y": 1,
                            "x": 5
                        }
                    ],
                    "name": "zjt / zjt"
                },
                {
                    "health": 100,
                    "id": "gs_dtTS6kT8xbwyx6b9JX9WVytC",
                    "body": [
                        {
                            "y": 5,
                            "x": 9
                        },
                        {
                            "y": 5,
                            "x": 9
                        },
                        {
                            "y": 5,
                            "x": 9
                        }
                    ],
                    "name": "adriaanwm / dontdie"
                },
                {
                    "health": 100,
                    "id": "gs_TfDW6rTkXGqqcG9wQy8PcJxD",
                    "body": [
                        {
                            "y": 9,
                            "x": 5
                        },
                        {
                            "y": 9,
                            "x": 5
                        },
                        {
                            "y": 9,
                            "x": 5
                        }
                    ],
                    "name": "colemacdonald / this-is-the-real-snake"
                },
                {
                    "health": 100,
                    "id": "gs_6HxcWB7v4wfKgFXjQ88wQpKd",
                    "body": [
                        {
                            "y": 5,
                            "x": 1
                        },
                        {
                            "y": 5,
                            "x": 1
                        },
                        {
                            "y": 5,
                            "x": 1
                        }
                    ],
                    "name": "ACHultman / Fer-de-lance"
                }
            ],
            "height": 11,
            "food": [
                {
                    "y": 4,
                    "x": 0
                },
                {
                    "y": 0,
                    "x": 4
                },
                {
                    "y": 3,
                    "x": 4
                },
                {
                    "y": 10,
                    "x": 7
                },
                {
                    "y": 7,
                    "x": 10
                },
                {
                    "y": 6,
                    "x": 2
                },
                {
                    "y": 0,
                    "x": 8
                },
                {
                    "y": 1,
                    "x": 7
                }
            ],
            "width": 11
        },
        "turn": 0,
        "game": {
            "id": "0d8d77e7-cb7e-446d-89f6-3bab7a3f4e2e"
        },
        "you": {
            "health": 100,
            "id": "gs_6HxcWB7v4wfKgFXjQ88wQpKd",
            "body": [
                {
                    "y": 5,
                    "x": 1
                },
                {
                    "y": 5,
                    "x": 1
                },
                {
                    "y": 5,
                    "x": 1
                }
            ],
            "name": "ACHultman / Fer-de-lance"
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
        if snake is not you:
            for coord in snake['body']:
                grid[coord['x']][coord['y']] = SNAKE  # Documents other snake's bodies for later evasion.
        else:
            next(snake['body'])  # Skips adding own snake's head to snake body grid.
            for coord in snake['body']:
                grid[coord['x']][coord['y']] = SNAKE

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
    for food in foods:
        target = astar_grid.node(food[0], food[1])
        finder = AStarFinder()  # Initialize AStarFinder
        path, runs = finder.find_path(source, target, astar_grid)  # get A* shortest path
        if not path:
            # print "no path to food"
            continue
        else:
            break
    path_length = len(path)
    print(path)
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
