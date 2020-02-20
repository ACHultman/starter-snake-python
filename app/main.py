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


def is_threat(pos, grid, snake, data, enemies):
    """
    Returns true if other >= snakes (threat) near target
    """
    snake_body = []
    own_snake_count = 0
    for coord in snake['body']:
        snake_body.append((coord['x'], coord['y']))
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]:
        x2 = pos[0] + dx
        y2 = pos[1] + dy
        if not in_bounds(x2, y2, data):
            continue
        current_pos = grid.graph[y2][x2]
        # print('current_pos: ', current_pos)
        # print('snake_body: ', snake_body)
        if current_pos == -1 and (x2, y2) not in snake_body:  # If position is snake and is not mine
            print('oh no')
            print('x2, y2: ', (x2, y2))
            print('enemies: ', enemies)
            if (x2, y2) in enemies:
                if enemy_size((x2, y2), data) < len(snake['body']):
                    # print('snake_size: ', len(snake['body']))
                    print('Nearby enemy is smaller at ', (x2, y2))
                    continue
                else:
                    print(' Nearby enemy is bigger at ', (x2, y2))
                    return True  # Nearby enemy is bigger
            elif (dx, dy) == (0, 0):
                return True  # Space occupied by snake
            else:
                print('Nearby enemy is not its head at ', (x2, y2))
                continue  # Nearby enemy is not its head so is threat
        elif current_pos == -1:
            if (dx, dy) == (0, 0):
                return True
            '''
            elif own_snake_count > 1:
                return True
            '''
        elif is_dead_end((x2, y2), grid, data, snake):
            print('Dead end threat detected')
            return True

    print('No threats found at ', (x2, y2))
    return False  # No enemies found


def last_check(path, grid, snake, data, enemies):
    """

    :param enemies:
    :param path:
    :param snake:
    :param grid:
    :param data:
    :return:
    """
    new_moves = []
    snake_body = []

    for coord in snake['body']:
        snake_body.append((coord['x'], coord['y']))
    if snake['health'] < 100 and data['turn'] > 5:  # If food has not just been eaten
        del snake_body[-1]
    snake_head = snake_body[0]

    if len(path) <= 1 or is_threat(path[1], grid, snake, data, enemies) or path[1] in snake_body:
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x2 = snake_head[0] + dx
            y2 = snake_head[1] + dy
            new_move = (x2, y2)
            print('new_move: ', new_move)
            if not in_bounds(x2, y2, data):  # If not in bounds, try another move
                print('new_move is not in bounds!')
                continue
            elif is_threat(new_move, grid, snake, data, enemies):  # If still dangerous, try another move
                print('new_move is still dangerous!')
                continue
            elif new_move in snake_body:  # If new_move is self-collision, try another move
                continue
            else:  # Suitable move
                print('new_move is suitable', new_move)
                new_moves.append(new_move)

    if len(new_moves) > 0:
        largest = 0
        best_move = None
        '''
        if len(path) >= 2:
            best_move = path[1]
            largest = astarsearch.bfs(grid, data, path[1])
        '''
        for new_move in new_moves:
            count = astarsearch.bfs(grid, data, new_move)
            print('count: ', count)
            print('new_move: ', new_move)
            if count > largest:
                largest = count
                best_move = new_move

        return best_move, True

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


def food_path(foods, data, snake, snake_head, astargrid, enemies):
    foods = sorted(foods, key=lambda p: distance(p, snake_head))  # Sorts food list by distance to snake's head
    path = None
    f = 0
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
        elif f > 100:
            continue
        elif len(path) == 2:
            print('food is close')
            if is_threat(target, astargrid, snake, data, enemies):
                continue
            else:
                break
        else:
            print("Path to food: " + str(path))
            print('Path to food COST: ', f)
            break
    return path, f


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
            elif f > 3:
                print('f too large: ', f)
                continue
            else:
                print("Path to enemy: " + str(path))
                print('Path to enemy COST: ', f)
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
    astargrid.graph = grid
    turn = data['turn']

    print('********** MOVE ' + str(turn) + ' *************')
    # print("Snake head x: " + str(snake['body'][0]['x']) + " snake head y: " + str(snake['body'][0]['y']))
    # print(barriers)

    snake_tail = (own_snake['body'][-1]['x'], own_snake['body'][-1]['y'])
    snake_head = (own_snake['body'][0]['x'], own_snake['body'][0]['y'])  # Coordinates for own snake's head

    enemies = [(snake['body'][0]['x'], snake['body'][0]['y']) for snake in data['board']['snakes']]
    if own_snake['health'] > 60 and turn > 10:  # Kill logic
        print('HUNTING...')
        path, result_1 = kill_path(enemies, own_snake, snake_head, data, astargrid)
        if result_1:
            print('KILL PATH FOUND')
            new_move, result_2 = last_check(path, astargrid, own_snake, data, enemies)
            if result_2:
                path[1] = new_move
            print('MOVING TO KILL')
            return move_response(direction(path))

    foods = []  # Tuple list of food coordinates
    for food in data['board']['food']:
        x = food['x']
        y = food['y']
        foods.append((x, y))

    # middle = (data['board']['width'] / 2, data['board']['height'] / 2)
    # foods = sorted(data['food'], key=lambda p: distance(p, middle))
    path, f = food_path(foods, data, own_snake, snake_head, astargrid, enemies)  # Food logic
    print('Path to food: ', path)
    if path is None or len(path) <= 1 or f > 100:
        # print("Snake Tail x: " + str(snake_tail[0]) + " y: " + str(snake_tail[1]))
        target = (snake_tail[0], snake_tail[1])  # Make target snake's own tail
        path, f = astarsearch.AStarSearch(snake_head, target, astargrid, data)  # get A* shortest path to tail
        print("PATH TO TAIL:" + str(path))

    if own_snake['health'] > 65 and turn > 30:
        # print("Snake Tail x: " + str(snake_tail[0]) + " y: " + str(snake_tail[1]))
        target = (snake_tail[0], snake_tail[1])  # Make target snake's own tail
        path, f = astarsearch.AStarSearch(snake_head, target, astargrid, data)  # get A* shortest path to tail
        print("PATH TO TAIL:" + str(path))

    new_move, result = last_check(path, astargrid, own_snake, data, enemies)
    if result:
        print('LAST_CHECK CORRECTION: ', new_move)
        if len(path) <= 1:
            path.append(new_move)
        else:
            path[1] = new_move

    if len(path) <= 1:
        #survive()
        print('Survive...')

    response = direction(path)
    print('moving: ', response)
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
