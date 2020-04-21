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
        if snake['name'] != you['name']:  # If snake is not me

            for coord in snake['body']:  # For every coordinate in the snake's body
                coord = (coord['x'], coord['y'])

                if coord == (snake['body'][-1]['x'], snake['body'][-1]['y']):  # If coord is tail
                    if data['turn'] < 2 or enemies.just_ate(coord):  # If turn<2 or enemy just ate/grew
                        grid[coord[1]][coord[0]] = SNAKE  # Consider the tail a snake body
                    else:
                        grid[coord[1]][coord[0]] = TAIL  # Else mark it as a snake tail
                    continue
                elif coord == (snake['body'][0]['x'], snake['body'][0]['y']):  # If coord is head
                    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:  # For all adjacent coordinates
                        x2 = coord[0] + dx
                        y2 = coord[1] + dy
                        if not in_bounds(x2, y2, data):  # Check if in bounds
                            continue
                        grid[y2][x2] = ADJ_HEAD  # Mark coordinate as head
                    continue
                else:
                    grid[coord[1]][coord[0]] = SNAKE  # Documents other snake's bodies for later evasion.

        else:  # Snake is me
            for coord in snake['body']:
                if coord is not snake['body'][-1]:
                    grid[coord['y']][coord['x']] = SNAKE
                elif enemies.just_ate(coord):
                    grid[coord['y']][coord['x']] = SNAKE
                else:
                    grid[coord['y']][coord['x']] = TAIL

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
