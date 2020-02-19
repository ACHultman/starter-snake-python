import json
import os

import bottle
from api import ping_response, start_response, end_response, move_response

import astarsearch

NAME = "ACHultman / Fer-de-lance"
WALKABLE = 1
SNAKE = -1
FOOD = 2
TAIL = 3


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
    print('p: ', p)
    print('q: ', q)
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
        print('item: ', item)
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
                print('enemy_size is ', len(snake['body']))
                return len(snake['body'])
    raise RuntimeError('No snake found in enemy_size')


def is_threat(pos, grid, snake, data):
    """
    Returns true if other >= snakes (threat) near target
    """
    snake_body = []
    for coord in snake['body']:
        snake_body.append((coord['x'], coord['y']))
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        x2 = pos[0] + dx
        y2 = pos[1] + dy
        if not in_bounds(x2, y2, data):
            continue
        current_pos = grid[y2][x2]
        print('current_pos: ', current_pos)
        print('snake_body: ', snake_body)
        if current_pos == -1 and (x2, y2) not in snake_body:
            print('oh no')
            if enemy_size((x2, y2), data) < len(snake['body']):
                print('snake_size: ', len(snake['body']))
                return False  # Nearby enemy is smaller
            else:
                return True  # Nearby enemy is bigger
    return False  # No enemies found


def last_check(path, grid, snake, data):
    """

    :param path:
    :param snake:
    :param grid:
    :param data:
    :return:
    """
    snake_body = []
    for coord in snake['body']:
        snake_body.append((coord['x'], coord['y']))

    snake_head = (snake['body'][0]['x'], snake['body'][0]['y'])
    if is_threat(path[1], grid, snake, data):  # If plotted path is still dangerous
        print('Last check is threat!')
        new_move = None
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x2 = snake_head[0] + dx
            y2 = snake_head[1] + dy
            new_move = (x2, y2)
            print('new_move: ', new_move)
            if not in_bounds(x2, y2, data):  # If not in bounds, try another move
                print('new_move is not in bounds!')
                continue
            elif is_threat(new_move, grid, snake, data):  # If still dangerous, try another move
                print('new_move is still dangerous!')
                continue
            elif new_move in snake_body:  # If new_move is self-collision, try another move
                continue
            else:  # Suitable move
                print('new_move is suitable')
                return new_move, True
        print('no suitable new_move found')
    return path[1], False


def grid_init(data):
    """
    Function for initializing the board.
    """
    json_data_board = data['board']
    height = json_data_board['height']
    you = data['you']  # Dictionary for own snake
    barriers = []

    grid = [[1 for col in range(height)] for row in range(height)]  # initialize 2d grid
    for snake in json_data_board['snakes']:
        if snake['name'] != you['name']:
            for coord in snake['body']:
                '''
                if coord is snake['body'][0]:
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        x2 = coord['x'] + dx
                        y2 = coord['y'] + dy
                        if x2 < 0 or x2 > 14 or y2 < 0 or y2 > 14:  # TODO make bounds run-time variable
                            continue
                        barriers.append((x2, y2))
                '''
                grid[coord['y']][coord['x']] = SNAKE  # Documents other snake's bodies for later evasion.
                barriers.append((coord['x'], coord['y']))
        else:
            for coord in snake['body']:  # Skip adding own tail to barriers in this loop
                if coord is not snake['body'][-1]:
                    grid[coord['y']][coord['x']] = SNAKE
                    barriers.append((coord['x'], coord['y']))
    for food in json_data_board['food']:  # For loop for marking all food on grid.
        grid[food['y']][food['x']] = FOOD

    return you, grid, barriers


def food_path(foods, data, snake, snake_head, astargrid, grid, enemies):
    foods = sorted(foods, key=lambda p: distance(p, snake_head))  # Sorts food list by distance to snake's head
    path = None
    # print(foods)
    for food in foods:
        food_coords = (food[0], food[1])
        enemy_distance = closest(enemies, food_coords)[1]
        my_distance = distance(snake_head, food_coords)
        if enemy_distance < my_distance:
            continue
        target = food_coords
        path, f = astarsearch.AStarSearch(snake_head, target, astargrid, data)  # get A* shortest path
        if len(path) <= 1:
            continue
        elif len(path) == 2:
            print('food is close')
            if is_threat(target, grid, snake, data):
                continue
            else:
                break
        else:
            print("Path to food: " + str(path))
            break
    return path


def kill_path(enemies, snake, snake_head, data, astargrid):
    enemies = sorted(enemies, key=lambda p: distance(p, snake_head))  # Sort enemy list by distance to snake's head
    path = None
    # print(foods)
    for enemy in enemies:
        if enemy_size(enemy, data) >= len(snake['body']):
            continue
        else:
            target = (enemy[0], enemy[1])
            path, f = astarsearch.AStarSearch(snake_head, target, astargrid, data)  # get A* shortest path
            if len(path) <= 1:
                continue
            elif f > 100:
                continue
            else:
                print("Path to enemy: " + str(path))
                return path, True
    return path, False


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
    # print(json.dumps(data))

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
    # print(data)
    own_snake, grid, barriers = grid_init(data)
    astargrid = astarsearch.AStarGraph()
    astargrid.barriers = barriers
    turn = data['turn']
    # print("Snake head x: " + str(snake['body'][0]['x']) + " snake head y: " + str(snake['body'][0]['y']))
    # print(barriers)

    snake_tail = (own_snake['body'][-1]['x'], own_snake['body'][-1]['y'])
    snake_head = (own_snake['body'][0]['x'], own_snake['body'][0]['y'])  # Coordinates for own snake's head

    enemies = [(snake['body'][0]['x'], snake['body'][0]['y']) for snake in data['board']['snakes']]
    if own_snake['health'] > 60 and turn > 5:  # Kill logic
        print('HUNTING...')
        path, result_1 = kill_path(enemies, own_snake, snake_head, data, astargrid)
        if result_1:
            print('KILL PATH FOUND')
            new_move, result_2 = last_check(path, grid, own_snake, data)
            if result_2:
                path[1] = new_move
            return move_response(direction(path))

    foods = []  # Tuple list of food coordinates
    for food in data['board']['food']:
        x = food['x']
        y = food['y']
        foods.append((x, y))

    # middle = (data['board']['width'] / 2, data['board']['height'] / 2)
    # foods = sorted(data['food'], key=lambda p: distance(p, middle))
    path = food_path(foods, data, own_snake, snake_head, astargrid, grid, enemies)  # Food logic

    if path is None or len(path) <= 1 or is_threat(path[1], grid, own_snake, data):
        # print("Snake Tail x: " + str(snake_tail[0]) + " y: " + str(snake_tail[1]))
        target = (snake_tail[0], snake_tail[1])  # Make target snake's own tail
        path, f = astarsearch.AStarSearch(snake_head, target, astargrid, data)  # get A* shortest path to tail
        # print("Path to tail:" + str(path))

    new_move, result = last_check(path, grid, own_snake, data)
    if result:
        path[1] = new_move

    response = direction(path)

    return move_response(response)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    # print(json.dumps(data))

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
