from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

snake = {
    "id": "gs_3D4KXWHKWVcjHdw6wbv7Rg3T",
    "name": "ACHultman / Fer-de-lance",
    "body": [
        {
            "x": 1,
            "y": 5

        },
        {
            "x": 1,
            "y": 5
        },
        {
            "x": 1,
            "y": 5
        }
    ],
    "health": 100
}

snake_head = (snake['body'][0]['x'], snake['body'][0]['y'])

matrix = [[1 for col in xrange(12)] for row in xrange(11)]
grid = Grid(matrix=matrix)

start = grid.node(snake_head[0], snake_head[1])
end = grid.node(2, 6)

finder = AStarFinder()
path, runs = finder.find_path(start, end, grid)

print('operations:', runs, 'path length:', len(path))
print(grid.grid_str(path=path, start=start, end=end))
print(path)
