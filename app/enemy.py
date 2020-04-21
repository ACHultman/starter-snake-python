def init_enemy_size(data):
    """
    Initializes enemy size dictionary
    :param data:
    :return: Enemy size dictionary
    """
    snakes = data['board']['snakes']
    size_dict = {snake['id']: len(snake['body']) for snake in snakes}
    print('Initialized size_dict')
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
        snake = self.get_enemy(pos)
        cur_size = len(snake['body'])
        prev_size = self.size_dict[snake['id']]
        print('just_ate: ' + str(cur_size) + ' ' + str(prev_size))
        return cur_size != prev_size

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

    def largest_size(self):
        """
        Finds largest size
        :return: size (int)
        """
        largest = 0
        for size in self.size_dict.values():
            if size > largest:
                largest = size
        return largest
