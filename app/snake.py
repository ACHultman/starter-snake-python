def get_body(data):
    """
    Turns snake's body data into a coordinate list
    :param data:
    :return: list of all snake body coordinates
    """
    body = []
    for coord in data['you']['body']:
        body.append((coord['x'], coord['y']))
    return body


class Snake:
    def __init__(self, data):
        self.name = data['you']['name']
        self.id = data['you']['id']
        self.health = data['you']['health']
        self.body = get_body(data)
        self.head = (self.body[0][0], self.body[0][1])
        self.tail = (self.body[-1][0], self.body[-1][1])
        self.size = len(self.body)
