
import numpy as np
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

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
    try:
        x_delta = path[1][0] - path[0][0]  # Get delta of the first two path x coordinates.
        y_delta = path[1][1] - path[0][1]  # Get delta of the first two path y coordinates.
    except IndexError:
        print("It appears there is not path.")
        return "no path"  # Implement smarter method

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



def init(data):
    """
    Function for initializing the board.
    """
    json_data_board = data['board']
    height = json_data_board['height']
    you = data['you']  # Dictionary for own snake

    grid = [[1 for col in range(height)] for row in range(height)]  # initialize 2d grid
    for snake in json_data_board['snakes']:
        if snake['name'] is not you['name']:
            for coord in snake['body']:
                grid[coord['y']][coord['x']] = SNAKE  # Documents other snake's bodies for later evasion.
        else:
            next(iter(you['body']))  # Skips adding own snake's head to snake body grid.
            tail_coord = None
            print("Is there food? Answer: " + str(not not json_data_board['food']))
            for coord in you['body']:
                try:
                    grid[coord['y']][coord['x']] = SNAKE
                    tail_coord = (coord['y'], coord['x'])
                except IndexError:
                    print("Index out of range: ", coord)
                    return
            if not json_data_board['food']:
                grid[tail_coord[0]][tail_coord[1]] = WALKABLE
                print("Tail now walkable: y: " + str(tail_coord[0]) + " x: " + str(tail_coord[1]))
    for food in json_data_board['food']:  # For loop for marking all food on grid.
        grid[food['y']][food['x']] = FOOD

    astar_grid = Grid(matrix=grid)

    return you, grid, astar_grid


'''
# DATA OBJECT
{
    "board": {
                "food": 
                [
                    {"x": 0, "y": 6}, 
                    {"x": 3, "y": 1}, 
                    {"x": 11, "y": 5}, 
                    {"x": 5, "y": 10}, 
                    {"x": 14, "y": 16}, 
                    {"x": 15, "y": 13}, 
                    {"x": 16, "y": 8}
                    ]
                , 
                "height": 19
                , 
                "snakes": 
                [
                    {"body": 
                        [
                        {"x": 1, "y": 1}, 
                        {"x": 1, "y": 1}, 
                        {"x": 1, "y": 1}
                        ]
                        , 
                        "name": "sagargandhi33 / professor-severus-snake", 
                        "id": "gs_QK8x4j4hcCxKyv6Xv9BrXYv8", 
                        "health": 100}
                    , 
                    {"body": 
                    [
                        {"x": 17, "y": 17}, 
                        {"x": 17, "y": 17}, 
                        {"x": 17, "y": 17}
                        ], 
                        "name": "LiyaniL / Habushu", 
                        "id": "gs_MWBSxvFmBqQfqQpRpBrcdftW", 
                        "health": 100}
                    , 
                    {"body": 
                        [
                        {"x": 1, "y": 17}, 
                        {"x": 1, "y": 17}, 
                        {"x": 1, "y": 17}
                        ], 
                        "name": "JerryKott / Multiplicity", 
                        "id": "gs_tbYcW9MH9wSjcRdwc6THPWGX", 
                        "health": 100}
                    , 
                    {"body": 
                        [
                        {"x": 17, "y": 1}, 
                        {"x": 17, "y": 1}, 
                        {"x": 17, "y": 1}
                        ], 
                        "name": "zjt / zjt", 
                        "id": "gs_8H9hTVBv6TYd8FfXKr6gR6R4", 
                        "health": 100}
                    , 
                    {"body": 
                        [
                        {"x": 9, "y": 1}, 
                        {"x": 9, "y": 1}, 
                        {"x": 9, "y": 1}
                        ], 
                        "name": "vitterso / PopsVakt", 
                        "id": "gs_3vyBm9RMjW38v7mgjd7CvjwV", 
                        "health": 100}
                    , 
                    {"body": 
                        [
                        {"x": 17, "y": 9}, 
                        {"x": 17, "y": 9}, 
                        {"x": 17, "y": 9}
                        ], 
                        "name": "num46664 / sillysnake", 
                        "id": "gs_FKhg9GyhBk6jGK3w8F8ggWVS", 
                        "health": 100}
                    , 
                    {"body": 
                        [
                        {"x": 9, "y": 17}, 
                        {"x": 9, "y": 17}, 
                        {"x": 9, "y": 17}
                        ], 
                        "name": "ACHultman / Fer-de-lance", 
                        "id": "gs_YbHFSjy4VdvxmqykRqV79GGB", 
                        "health": 100}
                    ]
                    , 
                    "width": 19
                    }, 
                    "game": 
                        {
                        "id": "494d6962-b227-4bf9-aa5c-a72bca7d64fe"
                        }, 
                        "turn": 0, 
                        "you": 
                            {"body": 
                            [
                            {"x": 9, "y": 17}, 
                            {"x": 9, "y": 17}, 
                            {"x": 9, "y": 17}
                            ], 
                            "name": "ACHultman / Fer-de-lance", 
                            "id": "gs_YbHFSjy4VdvxmqykRqV79GGB", 
                            "health": 100
                            }
    }

'''


def move(data):
    print(data)
    snake, grid, astar_grid = init(data)
    print(np.array(grid))
    json_data_board = data['board']

    print("Snake head x: " + str(snake['body'][0]['x']) + " snake head y: " + str(snake['body'][0]['y']))

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

    print("\n\nDEBUGGING\n\n")
    print("Path: ", path)
    print("Snake Head: ", snake_head)
    print("Snake Tail: ", snake_tail)
    print("Grid: \n\n")
    print(np.array(astar_grid.grid_str(path=path, start=source, end=target)))
    print("\n\n")

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
    response = direction(path)
    if response is "no path":
        target = astar_grid.node(5, 5)
        response, runs = finder.find_path(source, target, astar_grid)
    print(response)



data = \
    {
        "turn": 31,
        "you": {
            "name": "ACHultman / Fer-de-lance",
            "body": [
                {
                    "x": 10,
                    "y": 2
                },
                {
                    "x": 9,
                    "y": 2
                },
                {
                    "x": 8,
                    "y": 2
                },
                {
                    "x": 7,
                    "y": 2
                },
                {
                    "x": 6,
                    "y": 2
                },
                {
                    "x": 6,
                    "y": 3
                },
                {
                    "x": 6,
                    "y": 4
                },
                {
                    "x": 6,
                    "y": 5
                },
                {
                    "x": 6,
                    "y": 6
                },
                {
                    "x": 6,
                    "y": 7
                },
                {
                    "x": 6,
                    "y": 8
                }
            ],
            "id": "gs_PJt8FHcR8hwrcvvMxwHHtmHV",
            "health": 97
        },
        "board": {
            "snakes": [
                {
                    "name": "sandeshakya / Snake Gyllenhaal",
                    "body": [
                        {
                            "x": 0,
                            "y": 3
                        },
                        {
                            "x": 0,
                            "y": 4
                        },
                        {
                            "x": 1,
                            "y": 4
                        },
                        {
                            "x": 1,
                            "y": 3
                        },
                        {
                            "x": 1,
                            "y": 2
                        }
                    ],
                    "id": "gs_x7CKfX9tvtVc8B8XTPQRbVB7",
                    "health": 96
                },
                {"body":
                    [
                        {"x": 9, "y": 1},
                        {"x": 9, "y": 1},
                        {"x": 9, "y": 1}
                    ],
                    "name": "ACHultman / Fer-de-lance",
                    "id": "gs_YbHFSjy4VdvxmqykRqV79GGB",
                    "health": 100}
            ]
            ,

            "food": [

            ],
            "width": 11,
            "height": 11
        },
        "game": {
            "id": "cb1dcd78-663c-4074-80d5-9a84a9012a76"
        }
    }

move(data)
