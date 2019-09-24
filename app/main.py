import json
import os

import bottle
from api import ping_response, start_response, end_response, move_response

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

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


def init(data):
    """
    Function for initializing the board.
    """
    json_data_board = data['board']
    height = json_data_board['height']
    you = data['you']  # Dictionary for own snake

    grid = [[1 for col in xrange(height + 1)] for row in xrange(height)]  # initialize 2d grid
    for snake in json_data_board['snakes']:
        if snake is not you:
            for coord in snake['body']:
                grid[coord['x']][coord['y']] = SNAKE  # Documents other snake's bodies for later evasion.
        else:
            next(snake['body'])  # Skips adding own snake's head to snake body grid.
            for coord in snake['body']:
                grid[coord['x']][coord['y']] = SNAKE

    for f in json_data_board['food']:  # For loop for marking all food on grid.
        grid[f['x']][f['y']] = FOOD

    astar_grid = Grid(grid)

    return you, grid, astar_grid


@bottle.route('/')
def index():
    head_url = 'https://preview.redd.it/gmqetvdruob01.png?width=640&crop=smart&auto=webp&s' \
               '=24f556ed33b3c401c9d0218d45d30e4e5697cf75 '

    return {
        'color': '#00ff00',
        'head': head_url
    }


@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')


@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()


@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    return start_response()


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


@bottle.post('/move')
def move():
    data = bottle.request.json
    snake, grid, astar_grid = init(data)

    json_data_board = data['board']

    snake_head = (int(snake['body'][0]['x']), int(snake['body'][0]['y']))  # Coordinates for own snake's head
    path = None
    source = astar_grid.node(snake_head[0], snake_head[1])

    foods = []  # Tuple list of food coordinates
    for food in data['board']['food']:
        x = food['x']
        y = food['y']
        foods.append((x, y))

    # middle = [data['width'] / 2, data['height'] / 2]
    # foods = sorted(data['food'], key=lambda p: distance(p, middle))
    foods = sorted(foods, key=lambda p: distance(p, snake_head))  # Sorts food list by distance to snake's head

    for food in foods:
        target = astar_grid.node(food[0], food[1])
        finder = AStarFinder()  # Initialize AStarFinder
        path, runs = finder.find_path(source, target, astar_grid)  # get A* shortest path
        if not path:
            # print "no path to food"
            continue

        path_length = len(path)
        # snek_length = len(snake_coords) + 1

        in_trouble = False
        for enemy in json_data_board['snakes']:
            if enemy['name'] == NAME:
                continue
            if path_length > distance((enemy['body'][0]['x'], enemy['body'][0]['y']), food):
                in_trouble = True
        if in_trouble:
            continue
    print(path)

    print(json.dumps(data))
    print(path)

    return move_response(direction(path))


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
