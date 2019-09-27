from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import numpy as np

NAME = "ACHultman / Fer-de-lance"
WALKABLE = 1
SNAKE = -1
FOOD = 2


def distance(p, q):
    """
    Helper function for finding Manhattan distance between two cartesian points.
    """
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
        item_distance = distance(ref, item)
        if item_distance < closest_distance:
            closest_item = item
            closest_distance = item_distance

    return closest_item


def direction(path):
    """
    :param path:
    :return: "up", "down", "left", or "right"
    """
    try:
        x_delta = path[1][0] - path[0][0]  # Get delta of the first two path x coordinates.
        y_delta = path[1][1] - path[0][1]  # Get delta of the first two path y coordinates.
    except IndexError:
        print("It appears there is not path.")
        return "down"  # Implement smarter method

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


data = \
    {
        "turn": 31,
        "you": {
            "name": "ACHultman / Fer-de-lance",
            "body": [
                {
                    "x": 10,
                    "y": 2
                },
                {
                    "x": 9,
                    "y": 2
                },
                {
                    "x": 8,
                    "y": 2
                },
                {
                    "x": 7,
                    "y": 2
                },
                {
                    "x": 6,
                    "y": 2
                },
                {
                    "x": 6,
                    "y": 3
                },
                {
                    "x": 6,
                    "y": 4
                },
                {
                    "x": 6,
                    "y": 5
                },
                {
                    "x": 6,
                    "y": 6
                },
                {
                    "x": 6,
                    "y": 7
                },
                {
                    "x": 6,
                    "y": 8
                }
            ],
            "id": "gs_PJt8FHcR8hwrcvvMxwHHtmHV",
            "health": 97
        },
        "board": {
            "snakes": [
                {
                    "name": "sandeshakya / Snake Gyllenhaal",
                    "body": [
                        {
                            "x": 0,
                            "y": 3
                        },
                        {
                            "x": 0,
                            "y": 4
                        },
                        {
                            "x": 1,
                            "y": 4
                        },
                        {
                            "x": 1,
                            "y": 3
                        },
                        {
                            "x": 1,
                            "y": 2
                        }
                    ],
                    "id": "gs_x7CKfX9tvtVc8B8XTPQRbVB7",
                    "health": 96
                },
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

            "food": [

            ],
            "width": 11,
            "height": 11
        },
        "game": {
            "id": "cb1dcd78-663c-4074-80d5-9a84a9012a76"
        }
    }
'''
grid = Grid(matrix=matrix)

finder = AStarFinder()
path, runs = finder.find_path(start, end, grid)

print('operations:', runs, 'path length:', len(path))
print(grid.grid_str(path=path, start=start, end=end))
print(path)
'''


def init(datas):
    """
    Function for initializing the board.
    """
    json_data_board = datas['board']
    height = json_data_board['height']
    you = datas['you']  # Dictionary for own snake

    grid = [[1 for col in range(height)] for row in range(height)]
    print(np.array(grid))  # initialize 2d grid
    for snake in json_data_board['snakes']:
        if snake['name'] is not you['name']:
            for coord in snake['body']:
                grid[coord['y']][coord['x']] = SNAKE  # Documents other snake's bodies for later evasion.
        else:
            next(iter(snake['body']))  # Skips adding own snake's head to snake body grid.
            tail_coord = None
            print("Is there food? Answer: " + str(not not json_data_board['food']))

            for coord in you['body']:
                grid[coord['y']][coord['x']] = SNAKE
                tail_coord = (coord['y'], coord['x'])

            if not json_data_board['food']:
                grid[tail_coord[0]][tail_coord[1]] = WALKABLE
                print("Tail now walkable: y: " + str(tail_coord[0]) + " x: " + str(tail_coord[1]))

    for food in json_data_board['food']:  # For loop for marking all food on grid.
        grid[food['y']][food['x']] = FOOD

    astar_grid = Grid(matrix=grid)

    return you, grid, astar_grid


def move():
    snake, grid, astar_grid = init(data)
    print(np.array(grid))
    json_data_board = data['board']

    print("Snake head x: " + str(snake['body'][0]['x']) + " snake head y: " + str(snake['body'][0]['y']))
    print("nodes" + str(astar_grid.nodes))

    snake_tail = (snake['body'][-1]['x'], snake['body'][-1]['y'])
    snake_head = (snake['body'][0]['x'], snake['body'][0]['y'])  # Coordinates for own snake's head
    source = astar_grid.node(snake_head[0], snake_head[1])

    foods = []  # Tuple list of food coordinates
    for food in data['board']['food']:
        x = food['x']
        y = food['y']
        foods.append((x, y))

    # middle = [data['width'] / 2, data['height'] / 2]
    # foods = sorted(data['food'], key=lambda p: distance(p, middle))
    foods = sorted(foods, key=lambda p: distance(p, snake_head))  # Sorts food list by distance to snake's head
    target = None
    path = None
    finder = AStarFinder()  # Initialize AStarFinder
    for food in foods:
        target = astar_grid.node(food[0], food[1])
        path, runs = finder.find_path(source, target, astar_grid)  # get A* shortest path
        if not path:
            # print "no path to food"
            continue
        else:
            print("Path to food: " + str(path))
            break

    if not path:
        print("Snake Tail x: " + str(snake_tail[0]) + " y: " + str(snake_tail[1]))
        target = astar_grid.node(snake_tail[0], snake_tail[1])  # Make target snake's own tail
        path, runs = finder.find_path(source, target, astar_grid)  # get A* shortest path to tail
        print("Path to tail:" + str(path))

    path_length = len(path)
    # snek_length = len(snake_coords) + 1
    '''
        in_trouble = False
        for enemy in json_data_board['snakes']:
            if enemy['name'] == NAME:
                continue
            if path_length > distance((enemy['body'][0]['x'], enemy['body'][0]['y']), food):
                in_trouble = True
        if in_trouble:
            continue
    '''
    print(path)

    print('path length:', path_length)
    print(astar_grid.grid_str(path=path, start=source, end=target))
    print(path)
    print(direction(path))

    print("\n\nDEBUGGING\n\n")
    print("Path: ", path)
    print("Snake Head: ", snake_head)
    print("Snake Tail: ", snake_tail)
    print("Grid: \n\n")
    print(np.array(astar_grid.grid_str(path=path, start=source, end=target)))
    print("\n\n")


move()


'''
{
   u'game':{
      u'id':u'3b819e5b-d067-45b2-aba8-5e5fddbf7ab3'
   },
   u'you':{
      u'health':96,
      u'id':u'gs_tyKYS6wpDhQtTjFpj9fmXpRH',
      u'body':[
         {
            u'y':5,
            u'x':8
         },
         {
            u'y':4,
            u'x':8
         },
         {
            u'y':4,
            u'x':9
         },
         {
            u'y':4,
            u'x':10
         },
         {
            u'y':3,
            u'x':10
         },
         {
            u'y':3,
            u'x':9
         },
         {
            u'y':3,
            u'x':8
         }
      ],
      u'name':u'ACHultman / Fer-de-lance'
   },
   u'turn':17,
   u'board':{
      u'height':11,
      u'width':11,
      u'snakes':[
         {
            {
               u'health'u'game':96:,
               {
                  u'id'u'id'::u'gs_tyKYS6wpDhQtTjFpj9fmXpRH'u'3b819e5b-d067-45b2-aba8-5e5fddbf7ab3',

               }               u'body':,
               u'you'               [
:{
                     {
                        u'y'u'health'::599,
,
                        u'id'u'x'::u'gs_gRwc6tFjSJTxSRKxgqwWJDRR',
                        8                        u'body'
                     }:,
                     [
                        {
                           {
                              u'y'u'y'::43,
,
                              u'x'u'x'::82
                           }
                        },
                        {
,
                           u'y'                           {
:                              u'y'4:,
                              2                              u'x',
:                              u'x'9:
                           }                           2,

                        }                        {
,
                           u'y'                           {
:                              u'y'4:,
                              u'x'2:10,

                           }                           u'x',
:{
                              3                              u'y'
                           }:,
                           3                           {
,
                              u'y'u'x'::310,

                           }                           u'x',
:{
                              3                              u'y'
                           }:,
                           3                           {
,
                              u'y'u'x'::39,

                           }                           u'x',
                           {
:                              u'y'4:
                           }                           3,
,
                           {
                              u'x'u'y'::84
                           },

                        ]                        u'x',
:                        u'name'4:
                     }                     u'ACHultman / Fer-de-lance',

                  }                  {
,
                     u'y'                     {
:                        u'health'5:,
                        87                        u'x',
:                        u'id'4:
                     }                     u'gs_tpSyq8vx8JCRYRVpMjwWrkWK'
                  ],
,
                  u'body'u'name'::[
                     u'ACHultman / Fer-de-lance'                     {

                     }                     u'y',
:                     u'turn'7:,
                     17                     u'x',
:                     u'board'8:
                  }                  {
,
                     u'height'                     {
:                        u'y'11:,
                        6                        u'width',
:                        u'x'11:,
                        8                        u'snakes'
                     }:,
                     {
                        [
                           u'y'                           {
:                              u'health':696,
,
                              u'x'u'id'::9                              u'gs_tyKYS6wpDhQtTjFpj9fmXpRH'
                           },
,
                           u'body'                           {
:u'y'                              [
:{
                                    6                                    u'y',
:                                    u'x'5:,
                                    10                                    u'x'
                                 }:
                              ]                              8,

                           }                           u'name',
:{
                              u'j-delaney / Blue Bottle'u'y'
                           }:,
                           4                           {
,
                              u'health'u'x'::838,

                           }                           u'id',
:{
                              u'gs_7tBtgW4RcD9TRvWQtCThSBfb'u'y',
:                              u'body'4:,
                              [
                                 u'x'                                 {
:                                    u'y':10,
                                    u'x':7
                                 },
                                 {
                                    u'y':10,
                                    u'x'9:6
                                 }
                              },
,
                              {
                                 {
                                    u'y'u'y'::410,
,
                                    u'x'u'x'::105
                                 }
                              },

                           ]                           {
,
                              u'y'u'name'::3                              u'arielone / pollypython',

                           }                           u'x':,
                           10                           {

                           }                           u'health':,
                           {
                              99                              u'y',
:                              u'id'3:,
                              u'gs_gRwc6tFjSJTxSRKxgqwWJDRR'u'x',
:                              u'body'9:
                           }                           [
,
                              {
                                 {
                                    u'y'u'y'::33,
,
                                    u'x'u'x'::28
                                 }
                              },

                           ]                           {
,
                              u'y'u'name'::2                              u'ACHultman / Fer-de-lance',

                           }                           u'x',
:{
                              2                              u'health'
                           }:,
                           87                           {
,
                              u'y'u'id'::2                              u'gs_tpSyq8vx8JCRYRVpMjwWrkWK',
,
                              u'x'u'body'::3                              [

                              }                              {
,
                                 u'y'                                 {
:                                    u'y'7:,
                                    3                                    u'x',
:                                    u'x'8:
                                 }                                 3,

                              }                              {
,
                                 u'y'                                 {
:                                    u'y'6:,
                                    3                                    u'x',
:                                    u'x'8:
                                 }                                 4,

                              }                              {
,
                                 u'y'                                 {
:                                    u'y'6:,
                                    4                                    u'x',
:                                    u'x'9:
                                 }                                 4,

                              }                              {
,
                                 u'y'                                 {
:                                    u'y'6:,
                                    5                                    u'x',
:                                    u'x'10:
                                 }                                 4
                              ]
                           },

                        ]                        u'name',
:                        u'name'u'j-delaney / Blue Bottle':
                     }                     u'ACHultman / Fer-de-lance',

                  }                  {

                  ]                  u'health',
:                  u'food'83:[

                  ]
               }
            }            163           
            u'body':[
               {
                  u'y':Width11
               },
               {
                  u'y':10,
                  u'x':6
               },
               {
                  u'y':10,
                  u'x':5
               }
            ],
            u'name':u'arielone / pollypython'
         },
         {
            u'health':99,
            u'id':u'gs_gRwc6tFjSJTxSRKxgqwWJDRR',
            u'body':[
               {
                  u'y':3,
                  u'x':2
               },
               {
                  u'y':2,
                  u'x':2
               },
               {
                  u'y':2,
                  u'x':3
               },
               {
                  u'y':3,
                  u'x':3
               },
               {
                  u'y':3,
                  u'x':4
               },
               {
                  u'y':4,
                  u'x':4
               },
               {
                  u'y':5,
                  u'x':4
               }
            ],
            u'name':u'ACHultman / Fer-de-lance'
         }
      ],
      u'food':[

      ]
   }
}
'''