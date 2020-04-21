NAME = "ACHultman / Fer-de-lance"
FOOD = 2
WALKABLE = 1
SNAKE = -1
HEAD = -2
TAIL = 0


def in_bounds(x, y, data):
    """
    Checks if given x,y coordinate is in the grid.
    :param x:
    :param y:
    :return: True if coordinate is in the bounds
    """
    limit = data['board']['height'] - 1
    if x > limit or x < 0 or y > limit or y < 0:
        return False
    else:
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
    grid = [[1 for col in range(height)] for row in range(height)]  # initialize 2d grid
    for snake in data['board']['snakes']:

        if snake['name'] != you['name']:
            for coord in snake['body']:
                coord = (coord['x'], coord['y'])

                if coord == (snake['body'][-1]['x'], snake['body'][-1]['y']):
                    if data['turn'] < 2 or enemies.just_ate(coord):
                        grid[coord[1]][coord[0]] = SNAKE
                    else:
                        grid[coord[1]][coord[0]] = TAIL
                    continue
                elif coord == (snake['body'][0]['x'], snake['body'][0]['y']):
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                        x2 = coord[0] + dx
                        y2 = coord[1] + dy
                        if not in_bounds(x2, y2, data):
                            continue
                        grid[coord[1]][coord[0]] = HEAD
                    continue
                else:
                    grid[coord[1]][coord[0]] = SNAKE  # Documents other snake's bodies for later evasion.

        else:
            for coord in snake['body']:  # Skip adding own tail to barriers in this loop
                if coord is not snake['body'][-1]:
                    grid[coord['y']][coord['x']] = SNAKE
                    # barriers.append((coord['x'], coord['y']))
                else:
                    grid[coord['y']][coord['x']] = TAIL

    for food in data['board']['food']:  # For loop for marking all food on grid.
        grid[food['y']][food['x']] = FOOD

    return grid


class Board:
    def __init__(self, data, enemies):
        self.height = data['board']['height']
        self.width = data['board']['width']
        self.board = data['board']
        self.turn = data['turn']
        self.grid = create_grid(data, self.height, enemies)
