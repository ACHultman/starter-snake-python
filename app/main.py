"""
Main server and snake logic.
"""
import os

import bottle

from app.api import ping_response, start_response, end_response, move_response
from app.enemy import *
from app.food import *
from app.snake import *
from app.board import *
from app.utils import *


def is_threat(pos, grid, snake, data, enemies):
    """
    Returns true if other >= snakes (threat) near target
    """

    neighbours = get_vertex_neighbours(pos, data, grid, False)
    neighbours.append(pos)
    for neighbour in neighbours:
        y2 = neighbour[1]
        x2 = neighbour[0]
        current_pos = grid[y2][x2]

        if current_pos in (HEAD, ADJ_HEAD, SNAKE) and neighbour not in snake.body:  # If position is snake and is not mine
            print('pos near enemy snake')
            print('current neighbour x2, y2: ', (x2, y2))

            if neighbour in enemies.heads:  # If neighbour is enemy head
                if enemies.enemy_size(neighbour) < snake.size:
                    #print('Nearby enemy is smaller at ', neighbour)
                    continue
                else:
                    #print(' Nearby enemy is bigger at ', neighbour)
                    return True  # Nearby enemy is bigger
            elif neighbour == pos:  # If neighbour is suggested path (and is snake)
                return True  # Space occupied by snake

    if pos == TAIL:  # Is snake tail
        enemy_head = enemies.get_enemy(pos)['body'][0]
        enemy_head = (enemy_head['x'], enemy_head['y'])
        if is_adj(enemy_head, data, grid, FOOD):  # If enemy head near food, is threat
            return True

    elif grid[pos[1]][pos[0]] == ADJ_HEAD:
        #print('Pos is adj_head at ', pos)
        return True

    if is_dead_end(pos, grid, data, snake):
        #print('Dead end threat detected')
        return True

    else:
        #print('No threats found at ', pos)
        return False  # No enemies found


def survive(snake, data, grid):
    """
    Last effort to survive.
    :param snake:
    :param data:
    :param grid:
    :return: optimal path.
    """
    path = []
    new_moves = []

    path.append(snake.head)

    count, tails, bodies = bfs(grid, data, snake.head)  # use heads

    if len(tails) > 0:
        tails = sorted(tails, key=lambda p: distance(p, snake.head))
        for tail in tails:
            path, f = astarsearch(snake.head, tail, grid, data)
            if len(path) >= 2:
                return path
        del path
        path = [snake.head]

    neighbours = get_vertex_neighbours(snake.head, data, grid, False)
    for neighbour in neighbours:
        y2 = neighbour[1]
        x2 = neighbour[0]
        if grid[y2][x2] in [SNAKE, HEAD]:  # If neighbour is snake body
            continue
        elif neighbour in snake.body:  # If neighbour means self-collision, try another move
            continue
        else:  # Suitable move
            #print('new_move is suitable', neighbour)
            new_moves.append(neighbour)
    if len(new_moves) > 0:
        largest = 0
        best_move = None
        for new_move in new_moves:
            count = bfs(grid, data, new_move)[0]
            #print('count: ', count)
            #print('new_move: ', new_move)
            if is_adj(new_move, data, grid, TAIL):
                path.append(new_move)
                break
            if count > largest:
                largest = count
                best_move = new_move
        path.append(best_move)
        return path
    print('Survive failing...')
    return path


def last_check(path, grid, snake, data, enemies):
    """
    Performs a last check of proposed path, edits if necessary
    :param enemies:
    :param path:
    :param snake:
    :param grid:
    :param data:
    :return: True and new move, or false and old move
    """
    new_moves = []
    trouble = False

    if len(path) <= 1 or is_threat(path[1], grid, snake, data, enemies) or path[1] in snake.body:
        if len(path) > 1 and grid[path[1][1]][path[1][0]] == TAIL:
            return path[1], False
        trouble = True
        neighbours = get_vertex_neighbours(snake.head, data, grid, False)
        for neighbour in neighbours:
            #print('neighbour: ', neighbour)
            if is_threat(neighbour, grid, snake, data, enemies):  # If still dangerous, try another move
                #print('neighbour is still dangerous!')
                continue
            elif neighbour in snake.body:  # If neighbour is self-collision, try another move
                continue
            else:  # Suitable move
                #print('neighbour is suitable', neighbour)
                trouble = False
                new_moves.append(neighbour)

    if len(new_moves) > 0:
        largest = 0
        best_move = None
        for neighbour in new_moves:
            count, tails, bodies = bfs(grid, data, neighbour)
            print('count: ', count)
            print('neighbour: ', neighbour)
            if neighbour in tails:  # If move can be onto enemy tail
                return neighbour, True  # Do it
            if count > largest:
                largest = count
                best_move = neighbour
            # if tails:  # Probably stuck with enemy tail nearby
            #    tails = sorted(tails, key=lambda p: distance(p, snake.head))
            #    path, f = astarsearch(snake.head, tails[0], grid, data)
            #    if not path:
            #        continue
            #    return path[1], True

        return best_move, True

    elif len(path) <= 1 or trouble:
        path = survive(snake, data, grid)
        return path[1], True

    enemies.heads = sorted(enemies.heads, key=lambda p: distance(p, snake.head))
    enemy_head = enemies.heads[0]
    is_duel = len(path) > 1 and (len(enemies.heads) == 1 or distance(snake.head, enemy_head) < 5) and \
              enemies.enemy_size(enemies.heads[0]) > snake.size > 3 and snake.health > 30
    pos_moves = check_neighbours(data, grid, snake)

    if is_duel and len(pos_moves) > 1:  # If one
        print('Duelling...')
        # last bigger enemy
        duel_move, duel_res = duel_danger(enemies, path, pos_moves)
        if duel_res:
            if not is_dead_end(duel_move, grid, data, snake):
                #print('Duel correction: ', duel_move)
                return duel_move, True

    # elif new_moves == 0 and trouble and len(path) <= 1:
    #    #print('last_check trouble, path to tail')
    #    path, f = astarsearch(snake.head, snake.tail, grid, data)
    #    if path and 30 > f > 1:
    #        return path[1], True

    return path[1], False  # TODO Fix bug that ends here without a path


def check_neighbours(data, grid, snake):
    neighbours = get_vertex_neighbours(snake.head, data, grid, False)
    pos_moves = []
    for neighbour in neighbours:
        coord = (neighbour[0], neighbour[1])
        if grid[coord[1]][coord[0]] == 1:
            pos_moves.append(coord)
    return pos_moves


def duel_danger(enemies, path, pos_moves):
    for duel_move in pos_moves:
        if distance(duel_move, enemies.heads[0]) >= distance(path[0],
                                                             enemies.heads[0]):  # If next move is closer to enemy
            #print('Evading in duel')
            return duel_move, True
    else:
        return path[1], False


def food_path(foods, data, snake, grid, enemies):
    """
    Find best path to food
    :param foods:
    :param data:
    :param snake:
    :param grid:
    :param enemies:
    :return: Path, if any
    """
    foods.coords = sorted(foods.coords, key=lambda p: distance(p, snake.head))  # Sorts food list by distance to
    # snake's head
    path = None
    f = 0
    for food in foods.coords:
        #print('Looking at food: ', food)
        enemy_head, enemy_distance = closest(enemies.heads, food)
        my_distance = distance(snake.head, food)
        enemy_bigger = enemies.enemy_size(enemy_head) >= snake.size
        enemy_foods = sorted(foods.coords, key=lambda p: distance(p, enemy_head))
        if enemy_distance < 2 < my_distance:  # If enemy is next to food and I am not
            continue
        if enemy_distance < my_distance:  # If enemy is closer to food
            if food == enemy_foods[0]:  # If targeted food is closest to enemy
                #print('Looks like enemy is closer', enemy_head)
                continue
        if enemy_distance == my_distance and enemy_bigger:  # If we are equidistant but enemy is bigger
            if food == enemy_foods[0] and (data['turn'] < 15 or len(enemies.heads) < 2) and snake.health > 40:  # If
                # targeted food is closest to enemy
                continue
        target = food
        path, f = astarsearch(snake.head, target, grid, data)  # get A* shortest path
        if len(path) <= 1:
            continue
        elif f > 100:
            continue
        elif len(path) == 2:
            #print('food is close')
            if is_threat(target, grid, snake, data, enemies):
                continue
            else:
                break
        else:
            #print("Path to food: " + str(path))
            #print('Path to food COST: ', f)
            break
    return path, f


def kill_path(enemies, snake, data, grid):
    """
    Find best path to enemy
    :param enemies:
    :param snake:
    :param data:
    :param grid:
    :return: path, if any
    """

    # snake's head
    path = None
    for enemy in enemies.heads:
        enemy_size = enemies.enemy_size(enemy)
        if is_adj(enemy, data, grid, FOOD):
            #print('Target close to food')
            enemy_size = enemy_size + 1
        if enemy_size >= snake.size:
            #print('Enemy too big')
            continue
        else:
            target = (enemy[0], enemy[1])
            path, f = astarsearch(snake.head, target, grid, data)  # get A* shortest path
            if len(path) <= 1:
                #print('Invalid path')
                continue
            elif f > 15:
                #print('f too large: ', f)
                continue
            else:
                #print("Path to enemy: " + str(path))
                #print('Path to enemy COST: ', f)
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

    init_enemy_size(data)

    return start_response()


@bottle.post('/move')
def move():
    """
    Main logic for moving.
    :return: direction to move.
    """
    data = bottle.request.json
    game_foods = Food(data)
    own_snake = Snake(data)
    enemies = Enemy(own_snake, data)
    game_board = Board(data, enemies)
    enemies.heads = sorted(enemies.heads, key=lambda p: distance(p, own_snake.head))  # Sort enemy list by distance to
    print('********** MOVE ' + str(game_board.turn) + ' *************')

    should_hunt = own_snake.size > enemies.largest_size(own_snake) or distance(enemies.heads[0], own_snake.head) < 4
    can_hunt = should_hunt and own_snake.health > 30 and own_snake.size > 3
    if can_hunt:  # Kill logic
        #print('HUNTING...')
        path, result_1 = kill_path(enemies, own_snake, data, game_board.grid)
        if result_1:
            #print('KILL PATH FOUND')
            new_move, result_2 = last_check(path, game_board.grid, own_snake, data, enemies)
            if result_2:
                path[1] = new_move
            #print('MOVING TO KILL')
            enemies.update_enemy_size()
            return move_response(direction(path))

    cur_path, f = food_path(game_foods, data, own_snake, game_board.grid, enemies)  # Food logic
    #print('Path to food: ', cur_path)

    if cur_path is None or len(cur_path) <= 1 or f > 100:
        target = own_snake.tail  # Make target snake's own tail
        cur_path, f = astarsearch(own_snake.head, target, game_board.grid, data)  # get A* shortest path to tail
        print("PATH TO TAIL:" + str(cur_path))

    if own_snake.health > 70 and own_snake.size > enemies.largest_size(own_snake):
        target = own_snake.tail  # Make target snake's own tail
        cur_path, f = astarsearch(own_snake.head, target, game_board.grid, data)  # get A* shortest path to tail
        print("PATH TO TAIL:" + str(cur_path))

    new_move, result = last_check(cur_path, game_board.grid, own_snake, data, enemies)
    if result:
        #print('LAST_CHECK CORRECTION: ', new_move)
        if len(cur_path) <= 1:
            cur_path.append(new_move)
        else:
            cur_path[1] = new_move

    response = direction(cur_path)
    #print('moving: ', response)
    enemies.update_enemy_size()
    return move_response(response)


@bottle.post('/end')
def end():
    data = bottle.request.json

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
