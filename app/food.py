def list_foods(data):
    """
    Takes food data and lists the coordinates
    :param data:
    :return: List of all food coordinates
    """
    foods = []  # Tuple list of food coordinates
    for food in data['board']['food']:
        x = food['x']
        y = food['y']
        foods.append((x, y))
    return foods


class Food:
    """
    A class for food on the board.
    """
    def __init__(self, data):
        self.coords = list_foods(data)
        self.food_count = len(self.coords)
