import math
import random
import timeit
start_time = timeit.time()

to_process = set([1,2,3])
seen_paths = set([1,2,3])
POOL_SIZE = 16
max_length = POOL_SIZE

while(to_process):
    if len(to_process) % 1000 == 0:
        print(len(to_process))
    path_to_continue = to_process.pop()
    if (path_to_continue < 2**(2*(max_length - 1))):
        last_dir = path_to_continue % 4
        path_shifted = path_to_continue << 2
        for next_dir in range(4):
            if next_dir != 3 - last_dir:
                path_new = path_shifted + next_dir
                to_process.add(path_new)
                seen_paths.add(path_new)    

station_paths = [path for path in seen_paths]

def return_to_origin(path):
    x_offset = 0
    y_offset = 0
    while(path):
        dir = path % 4
        if (dir == 0):
            x_offset = x_offset + 1 # right
        if (dir == 1):
            y_offset = y_offset + 1 # up
        if (dir == 2):
            y_offset = y_offset - 1 # down
        if (dir == 3):
            x_offset = x_offset - 1 # left
        path = path // 4
    return(x_offset == 0 and y_offset == 0)

# The starting bit can't be a 0, so we must exit the station with 1, 2 or 3 (up, down or left)

# We need to travel through the station, taking three steps to the left (3,3,3 or 111111 in bits)
station_paths = [(path << 6) + 2**6 - 1 for path in station_paths]

returning_paths = set()
for i in range(len(station_paths)):
    if i % 100000 == 0:
        print(i)
    if return_to_origin(station_paths[i]):
        returning_paths.add(station_paths[i])


def one_loop(path):
    seen_points = set()
    x_offset = 0
    y_offset = 0
    while(path):
        dir = path % 4
        if (dir == 0):
            x_offset = x_offset + 1
        if (dir == 1):
            y_offset = y_offset + 1
        if (dir == 2):
            y_offset = y_offset - 1
        if (dir == 3):
            x_offset = x_offset - 1
        path = path // 4
        current_point = (x_offset, y_offset)
        if current_point in seen_points:
            return False
        seen_points.add(current_point)
    return True

loop_paths = {path for path in returning_paths if one_loop(path)}
loop_paths_list = [path for path in loop_paths]

def find_max_rep(path):
    tiles = math.floor(math.log(path, 4))
    max_path = path
    new_path = (path >> 2) + (path % 4) * 4**tiles
    while new_path != path:
        if new_path > max_path:
            max_path = new_path
        new_path = (new_path >> 2) + (new_path % 4) * 4**tiles
    return(max_path)

#max_paths = {find_max_rep(path) for path in loop_paths}

#max_paths_list = [path for path in max_paths]


def get_tiles(path):
    x_offset = 0
    y_offset = 0
    num_tiles = math.ceil(math.log(path, 4))
    tiles = [0] * num_tiles
    prev_dir = 3
    for tiles_remaining in range(num_tiles, 0, -1):
        dir = ((path >> (2 * (tiles_remaining - 1))) % 4)
        dir_info = (min(dir, 3 - prev_dir), max(dir, 3 - prev_dir))
        tile = Tile(x_offset, y_offset, dir_info)
        tiles[num_tiles - tiles_remaining] = tile
        if (dir == 0):
            x_offset = x_offset + 1
        if (dir == 1):
            y_offset = y_offset + 1
        if (dir == 2):
            y_offset = y_offset - 1
        if (dir == 3):
            x_offset = x_offset - 1
        prev_dir = dir
    return(tiles)

tile_dict = dict()
path_dict = dict()

for i in range(len(loop_paths_list)):
    path = loop_paths_list[i]
    path_dict[path] = dict()
    path_tiles = get_tiles(path)
    for tile in path_tiles:
        square = tile.get_square()
        path_dict[path][square] = tile
        directions = tile.directions
        if square in tile_dict:
            if directions in tile_dict[square]:
                tile_dict[square][directions].add(path)
            else:
                tile_dict[square][directions] = set([path])
        else:
            tile_dict[square] = dict()
            tile_dict[square][directions] = set([path])

fixed_tiles = TileSet({Tile(1, 0, set([0, 3])), Tile(2, 0, set([0, 3]))})

import cProfile

def squareset_test(num_trials):
    for i in range(num_trials):
        bar = SquareSet(0, 0, 1, 1)

def square_test(num_trials):
    for i in range(num_trials):
        bar = Square(0, 2)

def state_test(state, num_trials):
    for i in range(num_trials):
        state.find_moves()


foo = MonorailGame(fixed_tiles, tile_dict, path_dict)
#cProfile.run("state_test(foo.base_state, 100)") # 7.380 vs 0.8
#cProfile.run("squareset_test(1000000)") #3.845

#cProfile.run("square_test(10000000)") #3.354
#bar = cProfile.run("foo.play_game()") #27.7

foo.play_game()
end_time = timeit.time()


foo.base_state.evaluation

bar = foo.base_state.find_moves()
for move in bar:
    move_fixed_tiles = TileSet(foo.base_state.fixed_tiles.union(move))
    if move_fixed_tiles in foo.state_dict:
        print("move:", move)
        print("eval:", foo.state_dict[TileSet(foo.base_state.fixed_tiles.union(move))].evaluation)


winning_move = TileSet({Tile(4, -1, (0, 1)), Tile(2, -1, (0, 2)), Tile(3, -1, (1, 3))})
losing_state = foo.state_dict[foo.base_state.fixed_tiles.union(winning_move)]
losing_responses = losing_state.find_moves()
for response in losing_responses:
    response_tiles = TileSet(losing_state.fixed_tiles.union(response))
    w_turn_2 = foo.state_dict[response_tiles]
    w_turn_2_moves = w_turn_2.find_moves()
    for move in w_turn_2_moves:
        l_turn_3_tiles = TileSet(w_turn_2.fixed_tiles.union(move))
        if l_turn_3_tiles in foo.state_dict:
            if foo.state_dict[l_turn_3_tiles].evaluation == 0:
                winning_response = move
                break
    print("losing attempt:", response, ", win with:", winning_response)



