import json
import os

import bottle
from astar import *
from api import ping_response, start_response, end_response, move_response

SNEK_BUFFER = 3
NAME = "Fer-de-lance"
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

    grid = [[0 for col in xrange(data['height'])] for row in xrange(data['width'])]
    for snek in data['snakes']:
        if snek['name'] == NAME:  # finds own snake
            my_snake = snek  # copies data
        for coord in snek['coords']:
            grid[coord[0]][coord[1]] = SNAKE

    for f in data['food']:
        grid[f[0]][f[1]] = FOOD

    return my_snake, grid


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


# DATA OBJECT
# {
#     "game": "hairy-cheese",
#     "mode": "advanced",
#     "turn": 4,
#     "height": 20,
#     "width": 30,
#     "snakes": [
#         <Snake Object>, <Snake Object>, ...
#     ],
#     "food": [
#         [1, 2], [9, 3], ...
#     ],
#     "walls": [    // Advanced Only
#         [2, 2]
#     ],
#     "gold": [     // Advanced Only
#         [5, 5]
#     ]
# }

# SNAKE
# {
#     "id": "1234-567890-123456-7890",
#     "name": "Well Documented Snake",
#     "status": "alive",
#     "message": "Moved north",
#     "taunt": "Let's rock!",
#     "age": 56,
#     "health": 83,
#     "coords": [ [1, 1], [1, 2], [2, 2] ],
#     "kills": 4,
#     "food": 12,
#     "gold": 2
# }

@bottle.post('/move')
def move():
    data = bottle.request.json
    snek, grid = init(data)

    snake_head = snek['coords'][0]
    snake_coords = snek['coords']
    path = None
    tentative_path = AStarGraph(snake_coords)
    #middle = [data['width'] / 2, data['height'] / 2]
    # foods = sorted(data['food'], key=lambda p: distance(p, middle))
    foods = sorted(data['food'], key=lambda p: closest(p, snake_head))

    for food in foods:
        # print food
        path = AStarSearch(snake_head, food, grid)
        if not path:
            # print "no path to food"
            continue

        path_length = len(path)
        # snek_length = len(snake_coords) + 1

        in_trouble = False
        for enemy in data['snakes']:
            if enemy['name'] == NAME:
                continue
            if path_length > distance(enemy['coords'][0], food):
                in_trouble = True
        if in_trouble:
            continue

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
