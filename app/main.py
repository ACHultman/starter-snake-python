import copy
import json
import os

import bottle

from a_star import *
from api import ping_response, start_response, end_response, move_response

SNEK_BUFFER = 3
ID = 'de508402-17c8-4ac7-ab0b-f96cb53fbee8'
SNAKE = 1
FOOD = 3
SAFETY = 5


def direction(from_cell, to_cell):
    """
    Helper function for final move response.
    """
    dx = to_cell[0] - from_cell[0]
    dy = to_cell[1] - from_cell[1]

    if dx == 1:
        return 'left'
    elif dx == -1:
        return 'right'
    elif dy == -1:
        return 'up'
    elif dy == 1:
        return 'down'


def distance(p, q):
    """
    Helper function for finding absolute distance between two cartesian points.
    """
    dx = abs(p[0] - q[0])
    dy = abs(p[1] - q[1])
    return dx + dy


def closest(items, ref):
    """
    Helper function for finding closest item from reference point.
    """
    closest_item = None
    closest_distance = 10000  # type: int

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
        if snek['id'] == ID:  # finds own snake
            mysnake = snek  # copies data
        for coord in snek['coords']:
            grid[coord[0]][coord[1]] = SNAKE

    for f in data['food']:
        grid[f[0]][f[1]] = FOOD

    return mysnake, grid


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

    for enemy in data['snakes']:
        if enemy['id'] == ID:
            continue
        if len(enemy['coords']) > len(snek['coords']) - 1:
            if enemy['coords'][0][1] < data['height'] - 1:
                grid[enemy['coords'][0][0]][enemy['coords'][0][1] + 1] = SAFETY
            if enemy['coords'][0][1] > 0:
                grid[enemy['coords'][0][0]][enemy['coords'][0][1] - 1] = SAFETY

            if enemy['coords'][0][0] < data['width'] - 1:
                grid[enemy['coords'][0][0] + 1][enemy['coords'][0][1]] = SAFETY
            if enemy['coords'][0][0] > 0:
                grid[enemy['coords'][0][0] - 1][enemy['coords'][0][1]] = SAFETY

    snek_head = snek['coords'][0]
    snek_coords = snek['coords']
    path = None
    middle = [data['width'] / 2, data['height'] / 2]
    foods = sorted(data['food'], key=lambda p: distance(p, middle))
    if data['mode'] == 'advanced':
        foods = data['gold'] + foods
    for food in foods:
        # print food
        tentative_path = a_star(snek_head, food, grid, snek_coords)
        if not tentative_path:
            # print "no path to food"
            continue

        path_length = len(tentative_path)
        snek_length = len(snek_coords) + 1

        dead = False
        for enemy in data['snakes']:
            if enemy['id'] == ID:
                continue
            if path_length > distance(enemy['coords'][0], food):
                dead = True
        if dead:
            continue

        # Update snek
        if path_length < snek_length:
            remainder = snek_length - path_length
            new_snek_coords = list(reversed(tentative_path)) + snek_coords[:remainder]
        else:
            new_snek_coords = list(reversed(tentative_path))[:snek_length]

        if grid[new_snek_coords[0][0]][new_snek_coords[0][1]] == FOOD:
            # we ate food so we grow
            new_snek_coords.append(new_snek_coords[-1])

        # Create a new grid with the updates snek positions
        new_grid = copy.deepcopy(grid)

        for coord in snek_coords:
            new_grid[coord[0]][coord[1]] = 0
        for coord in new_snek_coords:
            new_grid[coord[0]][coord[1]] = SNAKE

        # printg(grid, 'orig')
        # printg(new_grid, 'new')

        # print snek['coords'][-1]
        foodtotail = a_star(food, new_snek_coords[-1], new_grid, new_snek_coords)
        if foodtotail:
            path = tentative_path
            break
        # print "no path to tail from food"

    if not path:
        path = a_star(snek_head, snek['coords'][-1], grid, snek_coords)

    despair = not (path and len(path) > 1)

    if despair:
        for neighbour in neighbours(snek_head, grid, 0, snek_coords, [1, 2, 5]):
            path = a_star(snek_head, neighbour, grid, snek_coords)
            # print 'i\'m scared'
            break

    despair = not (path and len(path) > 1)

    if despair:
        for neighbour in neighbours(snek_head, grid, 0, snek_coords, [1, 2]):
            path = a_star(snek_head, neighbour, grid, snek_coords)
            # print 'lik so scared'
            break

    if path:
        assert path[0] == tuple(snek_head)
        assert len(path) > 1

    return move_response('down')


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
