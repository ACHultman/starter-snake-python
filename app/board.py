from app.utils import *
from app.algs import *

NAME = "ACHultman / Fer-de-lance"
FOOD = 2
WALKABLE = 1
SNAKE = -1
HEAD = -2
ADJ_HEAD = -3
TAIL = 0



def in_bounds(x, y, data):
    """
    Checks if given x,y coordinate is in the grid.
    :param data: Data received
    :param x: x coordinate on graph
    :param y: y coordinate on graph
    :return: True if coordinate is in the bounds
    """
    limit = data['board']['height'] - 1
    if x > limit or x < 0 or y > limit or y < 0:
        return False
    else:
        return True


def close_to_border(pos, height):
    points = []
    result = False
    dy_up = pos[1] - 1
    dy_down = pos[1] + 1
    dx_left = pos[0] - 1
    dx_right = pos[0] + 1

    if dy_up == 0:
        points.append((pos[0], dy_up))
        result = True
    if dy_down == height - 1:
        points.append((pos[0], dy_down))
        result = True
    if dx_left == 0:
        points.append((dx_left, pos[1]))
        result = True
    if dx_right == height - 1:
        points.append((dx_right, pos[1]))
        result = True
    print('Close to border returning ', points, result)
    return points, result


def danger_near_head(data, height, enemy):
    if len(enemy['body']) >= len(data['you']['body']):  # If enemy equal size or larger
        print('danger_near_head return TRUE')
        return None, True
    else:
        enemy_head = (enemy['body'][0]['x'], enemy['body'][0]['y'])
        points, result = close_to_border(enemy_head, height)
        # Else if smaller enemy close to border
        if result:
            print('danger_near_head return TRUE')
            return points, True
        else:
            print('danger_near_head return FALSE')
            return None, False


def is_threat_beside(pos, data, grid, enemies):
    if not is_adj(pos, data, grid, HEAD):
        return False
    enemy = enemies.find_adj_enemy(pos, data, grid)
    if len(enemy['body']) <= len(data['you']['body']):
        return False
    print('Threat beside ', pos)
    return True


def create_grid(data, height, enemies):
    """
    Initializes the grid as a 2D list based on given data.
    :param enemies: enemies object
    :param data: data received
    :param height: height of board
    :return: A grid in the form of a 2D list
    """
    you = data['you']  # Dictionary for own snake
    grid = [[1 for col in range(height)] for row in range(height)]  # initialize 2d grid, assumes square

    for food in data['board']['food']:  # For loop for marking all food on grid.
        grid[food['y']][food['x']] = FOOD

    for snake in data['board']['snakes']:  # For every snake
        snake_head = (snake['body'][0]['x'], snake['body'][0]['y'])
        snake_tail = snake['body'][-1]['x'], snake['body'][-1]['y']
        if snake['name'] != you['name']:  # If snake is not me

            for coord in snake['body']:  # For every coordinate in the snake's body
                coord = (coord['x'], coord['y'])

                if coord == snake_tail:  # If coord is tail
                    if data['turn'] < 2 or enemies.just_ate(coord) or distance(snake_head, coord) < 2:  # If turn<2 or
                        # enemy just ate/grew
                        grid[coord[1]][coord[0]] = SNAKE  # Consider the tail a snake body
                    else:
                        grid[coord[1]][coord[0]] = TAIL  # Else mark it as a snake tail
                    continue
                elif coord == snake_head:  # If coord is head
                    grid[coord[1]][coord[0]] = HEAD
                    points, border_result = danger_near_head(data, height, snake)
                    if border_result and not points:
                        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            x2 = coord[0] + dx
                            y2 = coord[1] + dy
                            if not in_bounds(x2, y2, data):
                                continue
                            grid[y2][x2] = ADJ_HEAD
                    elif border_result and points:
                        for point in points:  # For all marked coordinates
                            grid[point[1]][point[0]] = ADJ_HEAD  # Mark coordinate as head
                        continue
                else:
                    grid[coord[1]][coord[0]] = SNAKE  # Documents other snake's bodies for later evasion.

        else:  # Snake is me
            for coord in snake['body']:
                coord = (coord['x'], coord['y'])
                if coord != snake_tail:
                    grid[coord[1]][coord[0]] = SNAKE
                    continue
                # If bigger enemy beside tail, or I just ate and beside tail, or I just ate and have food close
                threat_beside = is_threat_beside(coord, data, grid, enemies)
                eating_tail_close = (
                        enemies.just_ate(coord) and is_adj(snake_head, data, grid, FOOD) and distance(coord,
                                                                                                      snake_head) < 3)
                tail_threat = data['turn'] < 2 or (enemies.just_ate(coord) and distance(coord,
                                                                                        snake_head) < 2) or eating_tail_close or threat_beside
                if tail_threat:
                    grid[coord[1]][coord[0]] = SNAKE
                else:
                    grid[coord[1]][coord[0]] = TAIL

    #for x in grid:
    #    print(*x, sep='  ')

    return grid


class Board:
    """
    A class for the board itself.
    """

    def __init__(self, data, enemies):
        self.height = data['board']['height']
        self.width = data['board']['width']
        self.board = data['board']
        self.turn = data['turn']
        self.grid = create_grid(data, self.height, enemies)

    def in_centre(self, pos):
        '''
        Determines if position is in centre of grid
        :param pos:
        :return:
        '''
        x = pos[0]
        y = pos[1]
        x_mid = False
        y_mid = False
        if 2 < x < self.height-3:
            x_mid = True
        if 2 < y < self.height-3:
            y_mid = True
        if x_mid and y_mid:
            return True
        else:
            return False
