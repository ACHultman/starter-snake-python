import json
import os

import bottle
from astar import *
from api import ping_response, start_response, end_response, move_response

SNEK_BUFFER = 3
NAME = "ACHultman / Fer-de-lance"
SNAKE = 1
FOOD = 3
SAFETY = 5


def distance(p, q):
    """
    Helper function for finding Manhattan distance between two cartesian points.
    """
    dx = abs(p[0] - q[0])
    dy = abs(p[1] - q[1])
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


def init(data):
    """
    Function for initializing the board.
    """
    json_data_board = data['board']
    height = json_data_board['height']

    grid = [[0 for col in xrange(height + 1)] for row in xrange(height)]
    for snake in json_data_board['snakes']:

        for coord in snake['body']:
            grid[coord['x']][coord['y']] = SNAKE

    for f in json_data_board['food']:
        grid[f['x']][f['y']] = FOOD

    my_snake = data['you']

    avoid = []
    for rownum, row in enumerate(grid):
        for colnum, value in enumerate(row):
            if value is SNAKE:
                avoid.append((rownum, colnum))

    return my_snake, grid, avoid


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
    snake, grid, avoid = init(data)

    json_data_board = data['board']

    snake_head = (int(snake['body'][0]['x']), int(snake['body'][0]['y']))
    # snake_coords = snake['body']
    path = None
    tentative_path = AStarGraph(avoid)
    # middle = [data['width'] / 2, data['height'] / 2]
    # foods = sorted(data['food'], key=lambda p: distance(p, middle))
    foods = sorted(json_data_board['food'], key=lambda p: closest(p, snake_head))

    for food in foods:
        food_coords = (int(food['x']), int(food['y']))
        # print food
        path = tentative_path.AStarSearch(snake_head, food_coords, grid)
        if not path:
            # print "no path to food"
            continue

        path_length = len(path)
        # snek_length = len(snake_coords) + 1

        in_trouble = False
        for enemy in json_data_board['snakes']:
            if enemy['name'] == NAME:
                continue
            if path_length > distance((enemy['body'][0]['x'], enemy['body'][0]['y']), food_coords):
                in_trouble = True
        if in_trouble:
            continue
    print(path)

    for element in path:
        if element is (1, 0):
            path[element] = "right"
        elif element is (-1, 0):
            path[element] = "left"
        elif element is (0, 1):
            path[element] = "up"
        elif element is (0, -1):
            path[element] = "down"
        else:
            break

    print(json.dumps(data))
    print(path)

    return move_response(path[0])


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
