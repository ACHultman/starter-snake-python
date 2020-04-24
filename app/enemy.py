from app.algs import *
from app.utils import *


def init_enemy_size(data):
    """
    Initializes enemy size dictionary
    :param data:
    :return: Enemy size dictionary
    """
    snakes = data['board']['snakes']
    size_dict = {snake['id']: len(snake['body']) for snake in snakes}
    #print('Initialized size_dict')
    return size_dict


def find_heads(own_snake, data):
    """
    Finds coordinates of all the heads of enemy snakes
    :param own_snake:
    :param data:
    :return: list of coordinates of heads
    """
    enemy_heads = [(snake['body'][0]['x'], snake['body'][0]['y']) for snake in data['board']['snakes'] if
                   snake['id'] != own_snake.id]
    return enemy_heads


class Enemy:
    """
    A class for enemy snakes
    """

    def __init__(self, own_snake, data):
        self.size_dict = init_enemy_size(data)
        self.heads = find_heads(own_snake, data)
        self.snake_data = data['board']['snakes']

    def update_enemy_size(self):
        """
        Updates the dictionary of enemy sizes
        :return:
        """
        for snake in self.snake_data:
            snake_size = len(snake['body'])
            if self.size_dict[snake['id']] != snake_size:
                self.size_dict[snake['id']] = snake_size
                print(snake['name'] + 'is now ' + str(snake_size))

    def just_ate(self, pos):
        """
        Finds if given snake has just eaten this turn.
        :param pos:
        :return: True if size has changed (snake has eaten)
        """
        ate = False
        snake = self.get_enemy(pos)
        if not snake:
            #print('just_ate no snake found')
            return False
        snake_length = len(snake["body"])
        if snake_length >= 3:
            tail = snake["body"][-1]
            tail_body = snake["body"][-2]
            if tail != tail_body:
                #print("Snake didn't eat")
                ate = False
            else:
                #print("Snake ate")
                ate = True
        return ate

    def get_enemy(self, pos):
        """
        Finds snake data of snake at given position, if any
        :param pos:
        :return: Snake data
        """
        for snake in self.snake_data:
            for coord in snake['body']:
                if pos == (coord['x'], coord['y']):
                    return snake
        print('No snake found there')
        return None

    def enemy_size(self, pos):
        """
        Finds enemy snake at given position and returns its size.
        :param pos: position of enemy snake
        :return: size of snake at the position
        """
        snake = self.get_enemy(pos)
        if snake:
            return len(snake['body'])
        else:
            raise RuntimeError('No snake found in enemy_size')

    def largest_size(self, snake):
        """
        Finds largest size
        :return: size (int)
        """
        largest = 0
        for s_id in self.size_dict.keys():
            if s_id == snake.id:
                print('Passing own snake id in largest_size')
                continue
            size = self.size_dict[s_id]
            if size > largest:
                largest = size
        return largest

    def next_to_food(self, pos, data, grid):
        snake = self.get_enemy(pos)
        if not snake:
            return False
        snake_head = (snake['body'][0]['x'], snake['body'][0]['y'])
        if is_adj(snake_head, data, grid, FOOD):
            return True
        else:
            return False

    def find_adj_enemy(self, pos, data, grid):
        neighbours = get_vertex_neighbours(pos, data, grid, all_types=True)
        for neighbour in neighbours:
            snake = self.get_enemy(neighbour)
            if snake:
                return snake
        print('No adj enemy found')
        return None
