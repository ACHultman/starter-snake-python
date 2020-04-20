"""
Main server and snake logic.
"""
import os

import bottle
from app.api import ping_response, start_response, end_response, move_response

from app.algs import *
from app.utils import *


def is_threat(pos, grid, snake, data, enemies):
    """
    Returns true if other >= snakes (threat) near target
    """
    snake_body = []
    own_snake_count = 0
    for coord in snake['body']:
        snake_body.append((coord['x'], coord['y']))

    neighbours = get_vertex_neighbours(pos, data, grid)
    neighbours.append(pos)
    for neighbour in neighbours:
        y2 = neighbour[1]
        x2 = neighbour[0]
        current_pos = grid[y2][x2]
        # print('current_pos: ', current_pos)
        # print('snake_body: ', snake_body)
        if current_pos < 0 and neighbour not in snake_body:  # If position is snake and is not mine
            print('oh no')
            print('x2, y2: ', (x2, y2))
            print('enemies: ', enemies)
            if neighbour in enemies:  # If neighbour is enemy head
                if enemy_size(neighbour, data) < len(snake['body']):
                    # print('snake_size: ', len(snake['body']))
                    print('Nearby enemy is smaller at ', neighbour)
                    continue
                else:
                    print(' Nearby enemy is bigger at ', neighbour)
                    return True  # Nearby enemy is bigger
            elif neighbour == pos:  # If neighbour is suggested path (and is snake)
                return True  # Space occupied by snake
            else:
                print('Nearby enemy is not its head at ', neighbour)
                continue  # Nearby enemy is not its head so is not threat
        elif current_pos < 0 and neighbour == pos:
            return True

        elif current_pos == 0 and neighbour == pos:  # Is snake tail
            enemy_head = get_enemy(pos, data)['body'][0]
            enemy_head = (enemy_head['x'], enemy_head['y'])
            if adj_food(enemy_head, data, grid):  # If enemy head near food, is threat
                return True

    if is_dead_end(pos, grid, data, snake):
        print('Dead end threat detected')
        return True

    print('No threats found at ', pos)
    return False  # No enemies found


def survive(snake, data, grid):
    snake_body = []
    path = []
    new_moves = []

    for coord in snake['body']:
        snake_body.append((coord['x'], coord['y']))
    if snake['health'] < 100 and data['turn'] > 5:  # If food has not just been eaten then disregard tail
        del snake_body[-1]
    snake_head = snake_body[0]
    path.append(snake_head)

    count, tails, heads = bfs(grid, data, snake_head)  # use heads

    if len(tails) > 0:
        tails = sorted(tails, key=lambda p: distance(p, snake_head))
        for tail in tails:
            path, f = astarsearch(snake_head, tail, grid, data)
            if len(path) >= 2:
                return path
        path = []

    neighbours = get_vertex_neighbours(snake_head, data, grid)
    for neighbour in neighbours:
        y2 = neighbour[1]
        x2 = neighbour[0]
        if grid[y2][x2] < 0:  # If neighbour is snake body
            continue
        elif neighbour in snake_body:  # If neighbour means self-collision, try another move
            continue
        else:  # Suitable move
            print('new_move is suitable', neighbour)
            new_moves.append(neighbour)
    if len(new_moves) > 0:
        largest = 0
        best_move = None
        for new_move in new_moves:
            count = bfs(grid, data, new_move)[0]
            print('count: ', count)
            print('new_move: ', new_move)
            if count > largest:
                largest = count
                best_move = new_move
        path.append(best_move)
        return path
    print('Survive failed...')
    return path


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
        neighbours = get_vertex_neighbours(snake_head, data, grid)
        for neighbour in neighbours:
            print('neighbour: ', neighbour)
            if is_threat(neighbour, grid, snake, data, enemies):  # If still dangerous, try another move
                print('neighbour is still dangerous!')
                continue
            elif neighbour in snake_body:  # If neighbour is self-collision, try another move
                continue
            else:  # Suitable move
                print('neighbour is suitable', neighbour)
                new_moves.append(neighbour)

    if len(path) <= 1:
        path = survive(snake, data, grid)

    if len(new_moves) > 0:
        largest = 0
        best_move = None
        for neighbour in new_moves:
            count = bfs(grid, data, neighbour)[0]
            print('count: ', count)
            print('neighbour: ', neighbour)
            if count > largest:
                largest = count
                best_move = neighbour
        return best_move, True

    return path[1], False


def food_path(foods, data, snake, snake_head, grid, enemies):
    foods = sorted(foods, key=lambda p: distance(p, snake_head))  # Sorts food list by distance to snake's head
    path = None
    f = 0
    # print(foods)
    for food in foods:
        food_coords = (food[0], food[1])
        enemy, enemy_distance = closest(enemies, food_coords)
        my_distance = distance(snake_head, food_coords)
        if enemy_distance < my_distance and enemy_size(enemy, data) > len(snake['body']):
            continue
        if enemy_distance == my_distance and enemy_size(enemy, data) >= len(snake['body']) + 2:
            continue
        target = food_coords
        path, f = astarsearch(snake_head, target, grid, data)  # get A* shortest path
        if len(path) <= 1:
            continue
        elif f > 100:
            continue
        elif len(path) == 2:
            print('food is close')
            if is_threat(target, grid, snake, data, enemies):
                continue
            else:
                break
        else:
            print("Path to food: " + str(path))
            print('Path to food COST: ', f)
            break
    return path, f


def kill_path(enemies, snake, snake_head, data, grid):
    enemies = sorted(enemies, key=lambda p: distance(p, snake_head))  # Sort enemy list by distance to snake's head
    path = None
    # print(foods)
    for enemy in enemies:
        enemysize = enemy_size(enemy, data)
        if adj_food(enemy, data, grid):
            print('Target close to food')
            enemysize = enemysize + 1
        if enemysize >= len(snake['body']):
            print('Enemy too big')
            continue
        else:
            target = (enemy[0], enemy[1])
            path, f = astarsearch(snake_head, target, grid, data)  # get A* shortest path
            if len(path) <= 1:
                print('Invalid path')
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


en_size_dict = {}


@bottle.post('/start')
def start():
    data = bottle.request.json

    init_enemy_size(data)

    return start_response()


@bottle.post('/move')
def move():
    data = bottle.request.json
    # print(data)
    own_snake, grid, barriers = grid_init(data)

    turn = data['turn']

    print('********** MOVE ' + str(turn) + ' *************')
    # print("Snake head x: " + str(snake['body'][0]['x']) + " snake head y: " + str(snake['body'][0]['y']))
    # print(barriers)

    snake_tail = (own_snake['body'][-1]['x'], own_snake['body'][-1]['y'])
    snake_head = (own_snake['body'][0]['x'], own_snake['body'][0]['y'])  # Coordinates for own snake's head

    enemies = [(snake['body'][0]['x'], snake['body'][0]['y']) for snake in data['board']['snakes'] if
               snake['id'] != own_snake['id']]

    if (own_snake['health'] > 50 and turn > 15) or (
            len(data['board']['snakes']) == 2 and own_snake['health'] > 30):  # Kill logic
        print('HUNTING...')
        path, result_1 = kill_path(enemies, own_snake, snake_head, data, grid)
        if result_1:
            print('KILL PATH FOUND')
            new_move, result_2 = last_check(path, grid, own_snake, data, enemies)
            if result_2:
                path[1] = new_move
            print('MOVING TO KILL')
            update_enemy_size(data)
            return move_response(direction(path))

    foods = []  # Tuple list of food coordinates
    for food in data['board']['food']:
        x = food['x']
        y = food['y']
        foods.append((x, y))

    # middle = (data['board']['width'] / 2, data['board']['height'] / 2)
    # foods = sorted(data['food'], key=lambda p: distance(p, middle))
    path, f = food_path(foods, data, own_snake, snake_head, grid, enemies)  # Food logic
    print('Path to food: ', path)
    if path is None or len(path) <= 1 or f > 100:
        # print("Snake Tail x: " + str(snake_tail[0]) + " y: " + str(snake_tail[1]))
        target = (snake_tail[0], snake_tail[1])  # Make target snake's own tail
        path, f = astarsearch(snake_head, target, grid, data)  # get A* shortest path to tail
        print("PATH TO TAIL:" + str(path))

    if own_snake['health'] > 70 and len(own_snake['body']) > 35:
        # print("Snake Tail x: " + str(snake_tail[0]) + " y: " + str(snake_tail[1]))
        target = (snake_tail[0], snake_tail[1])  # Make target snake's own tail
        path, f = astarsearch(snake_head, target, grid, data)  # get A* shortest path to tail
        print("PATH TO TAIL:" + str(path))

    new_move, result = last_check(path, grid, own_snake, data, enemies)
    if result:
        print('LAST_CHECK CORRECTION: ', new_move)
        if len(path) <= 1:
            path.append(new_move)
        else:
            path[1] = new_move

    if len(path) <= 1:
        print('Survive...')
        path = survive(own_snake, data, grid)

    response = direction(path)
    print('moving: ', response)
    update_enemy_size(data)
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
