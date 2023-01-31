import math
import time
import os
os.chdir(r'C:\Users\Jed\Desktop\Programming\Genius\Monorail')
from MonorailGame import MonorailGame
from TileSet import TileSet
from SquareSet import SquareSet
from Square import Square
from Tile import Tile
from PIL import Image, ImageDraw, ImageFont
import cfg
#from importlib import reload

start_time = time.perf_counter()
to_process = set([1,2,3])
seen_paths = set([1,2,3])
POOL_SIZE = 16
max_length = POOL_SIZE

# Generate every path of length up to 16, without regard for physical possibility
# I'm sure there are better ways, but it gets it done.
while(to_process):
    path_to_continue = to_process.pop()
    if (path_to_continue < 2**(2*(max_length - 1))):
        last_dir = path_to_continue % 4
        path_shifted = path_to_continue << 2
        for next_dir in range(4):
            if next_dir != 3 - last_dir:
                path_new = path_shifted + next_dir
                to_process.add(path_new)
                seen_paths.add(path_new)    
del(to_process)

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
station_paths = [(path << 6) + 2**6 - 1 for path in seen_paths]
del(seen_paths)
returning_paths = set()

# Paths that return to the station (i.e. create a loop)
for i in range(len(station_paths)):
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

# Filter out self-intersecting paths
loop_paths = {path for path in returning_paths if one_loop(path)}
loop_paths_list = [path for path in loop_paths]

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

tile_dict = dict() # map from tiles to possible paths
path_dict = dict() # map from paths to contained tiles

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

fixed_tiles = TileSet({Tile(1, 0, (0, 3)), Tile(2, 0, (0, 3))})

game = MonorailGame(fixed_tiles, tile_dict, path_dict)
game.play_game()
end_time = time.perf_counter()

def get_tile_coordinates(x, y, x_offset = cfg.x_offset, y_offset = cfg.y_offset, height = cfg.height):
    x_coord = (x + x_offset) * (cfg.square_length + cfg.square_gap) + cfg.square_gap
    y_coord = (-(y + y_offset) + height - 1) * (cfg.square_length + cfg.square_gap) + cfg.square_gap
    return((x_coord, y_coord))

def add_tile(x, y, dirs, draw, color = cfg.color, x_offset = cfg.x_offset, y_offset = cfg.y_offset, height = cfg.height):
    minx, miny = get_tile_coordinates(x, y, x_offset, y_offset, height)
    short_gap = cfg.square_length * 0.4
    long_gap = cfg.square_length * 0.6
    square_length = cfg.square_length
    draw.rectangle([minx + short_gap, miny + short_gap, minx + long_gap, miny + long_gap], outline = (255, 100, 100, 100), fill = color)
    if 1 in dirs:
        draw.rectangle([minx + short_gap, miny, minx + long_gap, miny + short_gap], outline = (255, 100, 100, 100), fill = color)
    if 0 in dirs:
        draw.rectangle([minx + long_gap, miny + short_gap, minx + square_length, miny + long_gap], outline = (255, 100, 100, 100), fill = color)
    if 2 in dirs:
        draw.rectangle([minx + short_gap, miny + long_gap, minx + long_gap, miny + square_length], outline = (255, 100, 100, 100), fill = color)
    if 3 in dirs:
        draw.rectangle([minx, miny + short_gap, minx + short_gap, miny + long_gap], outline = (255, 100, 100, 100), fill = color)

def draw_clean_board(width = cfg.width, height = cfg.height):
    square_length = cfg.square_length
    square_gap = cfg.square_gap
    x_squares = width
    y_squares = height
    x_length = x_squares * square_length + (x_squares + 1) * square_gap
    y_length = y_squares * square_length + (y_squares + 1) * square_gap
    image = Image.new("RGB", (x_length, y_length))
    draw = ImageDraw.Draw(image)
    pixels = image.load()
    for i in range(x_squares):
        minx = (square_length + square_gap)*i + square_gap
        for j in range(y_squares):
            miny = (square_length + square_gap)*j + square_gap
            draw.rectangle([minx, miny, minx + square_length, miny + square_length], outline = (255, 100, 100, 100), fill = (255, 255, 255, 150))
    return((image, draw))

def fill_squares(draw, squares_to_fill):
    for square in squares_to_fill:
        min_x = (cfg.square_length + cfg.square_gap) * square[0] + cfg.square_gap
        min_y = (cfg.square_length + cfg.square_gap) * square[1] + cfg.square_gap
        draw.rectangle([min_x, min_y, min_x + cfg.square_length, min_y + cfg.square_length], outline = (255, 255, 255, 255), fill = (0, 0, 0, 0))
    return(draw)

def draw_start_board(width = cfg.width, height = cfg.height, x_offset = cfg.x_offset, y_offset = cfg.y_offset, color = cfg.start_color):
    image, draw = draw_clean_board(width, height)
    add_tiles(TileSet([Tile(1, 0, (0, 3)), Tile(2, 0, (0, 3))]), draw, x_offset = x_offset, y_offset = y_offset, height = height, color = color)
    return ((image, draw))

def add_tiles(tiles, draw, color = cfg.color, x_offset = cfg.x_offset, y_offset = cfg.y_offset, height = cfg.height):
    for tile in tiles:
        add_tile(tile.x_pos, tile.y_pos, tile.directions, draw, color, x_offset, y_offset, height)

def add_state_tiles(state, draw, color = cfg.color, x_offset = cfg.x_offset, y_offset = cfg.y_offset):
    fixed_tiles = state.fixed_tiles
    remaining_tiles = state.fixed_tiles.difference(TileSet([Tile(1, 0, (0, 3)), Tile(2, 0, (0, 3))]))
    add_tiles(remaining_tiles, draw, color, x_offset, y_offset)

winning_move = TileSet({Tile(4, -1, (0, 1)), Tile(2, -1, (0, 2)), Tile(3, -1, (1, 3))})
losing_state = game.state_dict[game.base_state.fixed_tiles.union(winning_move)]

def get_adjacency_sets(state):
    path_squares = SquareSet(0, 4, 0, 1).union(SquareSet(2, 5, -2, -1))
    remaining_squares = path_squares.difference(state.exhausted_squares)
    adjacency_sets = set()
    while remaining_squares:
        start_square = remaining_squares.pop()
        squares_to_process = SquareSet([start_square])
        group_squares = SquareSet([start_square])
        while squares_to_process:
            square_processing = squares_to_process.pop()
            adjacent_squares = SquareSet([square for square in remaining_squares if (abs(square_processing.x_pos - square.x_pos) + abs(square_processing.y_pos - square.y_pos)) == 1])
            squares_to_process.update(adjacent_squares)
            group_squares.update(adjacent_squares)
            remaining_squares.difference_update(adjacent_squares)
        adjacency_sets.add(group_squares)
    return(adjacency_sets)

def get_all_substates(state, game):
    states_to_process = set([state])
    states_seen = set([state])
    while states_to_process:
        state_processing = states_to_process.pop()
        moves = state_processing.find_moves()
        state_tiles = state_processing.fixed_tiles
        for move in moves:
            substate_tiles = state_tiles.union(move)
            if substate_tiles not in game.state_dict:
                substate = game.create_state(substate_tiles)
                if substate.evaluation is not None:
                    game.state_dict[substate_tiles] = substate
                game.play_game(substate)
                if substate_tiles not in game.state_dict:
                    raise AssertionError('Oops')
            substate = game.state_dict[substate_tiles]
            if substate not in states_seen:
                states_seen.add(substate)
                states_to_process.add(substate)
    return(states_seen)

all_substates = get_all_substates(losing_state, game)
done_state = [state for state in all_substates if len(state.fixed_tiles) == 18][0]

def draw_winning_board(highlight_state = done_state, width = cfg.width, height = cfg.height, x_offset = cfg.x_offset, y_offset = cfg.y_offset):
    image, draw = draw_start_board(width, height, x_offset, y_offset)
    add_state_tiles(highlight_state, draw, color = (255, 255, 255, 255))
    draw = fill_squares(draw, [(0, 2), (0, 3), (1, 2), (1, 3), (5, 0), (5, 1)])
    return((image, draw))

all_adjacency_sets = set()
for state in all_substates:
    adjacency_sets = get_adjacency_sets(state)
    all_adjacency_sets.update(adjacency_sets)

def get_adjacency_set_type(adjacency_set):
    single_x = len({sq.x_pos for sq in adjacency_set}) == 1
    single_y = len({sq.y_pos for sq in adjacency_set}) == 1
    if single_x or single_y:
        return(str(len(adjacency_set)))
    if adjacency_set in {SquareSet({Square(3,0), Square(4,1), Square(4,0)}),
                         SquareSet({Square(3,0), Square(3,1), Square(4,1)}),
                         SquareSet({Square(3,0), Square(3,1), Square(2,1)})}:
        return("L")
    if adjacency_set in {SquareSet({Square(3,1), Square(4,1), Square(4,0)}), 
                         SquareSet({Square(5,-2), Square(4,-2), Square(5,-1)}), 
                         SquareSet({Square(0,1), Square(0,0), Square(1,1)})}:
        return("Lx")
    if adjacency_set in {SquareSet({Square(3,0), Square(3,1), Square(1,1), Square(2,1)})}:
        return("L3")
    if adjacency_set in {SquareSet({Square(5,-1), Square(4,-2), Square(3,-2), Square(5,-2)}), 
                         SquareSet({Square(3,1), Square(4,1), Square(2,1), Square(4,0)}),
                         SquareSet({Square(0,1), Square(0,0), Square(1,1), Square(2,1)})}:
        return("L3x")
    if adjacency_set in {SquareSet({Square(0,1), Square(3,0), Square(3,1), Square(1,1), Square(2,1)})}:
        return("L4")
    if adjacency_set in {SquareSet({Square(0,1), Square(0,0), Square(3,1), Square(1,1), Square(2,1)}),
                         SquareSet({Square(3,1), Square(4,1), Square(1,1), Square(2,1), Square(4,0)}),
                         SquareSet({Square(5,-1), Square(5,-2), Square(2,-2), Square(4,-2), Square(3,-2)})}:
        return("L4x")
    if adjacency_set in {SquareSet({Square(0,1), Square(0,0), Square(3,1), Square(4,1), Square(1,1), Square(2,1)}), 
                         SquareSet({Square(0,1), Square(3,1), Square(4,1), Square(1,1), Square(2,1), Square(4,0)})}:
        return("L5x")
    if adjacency_set in {SquareSet({Square(3,0), Square(3,1), Square(4,1), Square(4,0)})}:
        return("S")
    if adjacency_set in {SquareSet({Square(3,0), Square(3,1), Square(4,1), Square(2,1), Square(4,0)})}:
        return("S+1")
    if adjacency_set in {SquareSet({Square(3,0), Square(3,1), Square(4,1), Square(1,1), Square(2,1), Square(4,0)})}:
        return("S+2")
    if adjacency_set in {SquareSet({Square(0,1), Square(3,0), Square(3,1), Square(4,1), Square(1,1), Square(2,1), Square(4,0)})}:
        return("S+3")
    if adjacency_set in {SquareSet({Square(0,1), Square(0,0), Square(3,0), Square(3,1), Square(4,1), Square(1,1), Square(2,1), Square(4,0)})}:
        return("S+L3x")
    if adjacency_set in {SquareSet({Square(0,1), Square(0,0), Square(3,0), Square(3,1), Square(1,1), Square(2,1)})}:
        return("C4")
    if adjacency_set in {SquareSet({Square(0,1), Square(0,0), Square(3,0), Square(3,1), Square(4,1), Square(1,1), Square(2,1)})}:
        return("C4+1")
    if adjacency_set in {SquareSet({Square(0,1), Square(0,0), Square(3,1), Square(4,1), Square(1,1), Square(2,1), Square(4,0)})}:
        return("C5")
    if adjacency_set in {SquareSet({Square(3,0), Square(3,1), Square(4,1), Square(2,1)})}:
        return("T")
    if adjacency_set in {SquareSet({Square(3,0), Square(3,1), Square(4,1), Square(1,1), Square(2,1)})}:
        return("T4")
    if adjacency_set in {SquareSet({Square(0,1), Square(3,0), Square(3,1), Square(4,1), Square(1,1), Square(2,1)})}:
        return("T5")
    raise ValueError(adjacency_set)

# Validate all adjacency sets are assigned a name
for adj_set in all_adjacency_sets:
    try:
        _ = get_adjacency_set_type(adj_set)
    except ValueError as e:
        raise e

def get_state_category(state):
    adjacency_sets = get_adjacency_sets(state)
    if len(adjacency_sets) == 0:
        return("Done")
    else:
        return("-".join(sorted([get_adjacency_set_type(adj_set) for adj_set in adjacency_sets])))

all_substate_cats = {get_state_category(state) for state in all_substates}

# Validate that states with identical adjacency set names map moves to states
# with identical adjacency set names
state_move_dict = dict()
for state in all_substates:
    state_cat = get_state_category(state)
    state_fixed = state.fixed_tiles
    state_moves = state.find_moves()
    substate_cats = []
    for move in state_moves:
        move_fixed_tiles = state_fixed.union(move)
        substate = game.state_dict[move_fixed_tiles]
        substate_cat = get_state_category(substate)
        substate_cats.append(substate_cat)
    substate_cats = sorted(substate_cats)
    substate_string = ";".join(substate_cats)
    if state_cat in state_move_dict:
        if state_move_dict[state_cat] != substate_string:
            raise ValueError('substate strings are not consistent!')
    else:
        state_move_dict[state_cat] = substate_string

seen_cats = set()
for state in all_substates:
    state_cat = get_state_category(state)
    if state_cat not in seen_cats:
        seen_cats.add(state_cat)
        image, draw = draw_winning_board()
        add_state_tiles(state, draw)
        image.save("Images/" + state_cat + ".png")

def tile_to_alphanum(tile):
    col_char = ""
    if tile.y_pos == 1:
        col_char = "A"
    elif tile.y_pos == 0:
        col_char = "B"
    elif tile.y_pos == -1:
        col_char = "C"
    elif tile.y_pos == -2:
        col_char = "D"
    row_char = str(tile.x_pos + 1)
    if len(col_char) == 0:
        raise ValueError("Cannot find column for " + str(tile))
    return(col_char + row_char)

# Create image with squares labeled alphanumerically for the appendix
image, draw = draw_start_board()
add_state_tiles(losing_state, draw)
draw = fill_squares(draw, [(0, 2), (0, 3), (1, 2), (1, 3), (5, 0), (5, 1)])
times_font = ImageFont.truetype(r"C:\Windows\Fonts\Times.ttf", size = 40)
letters = ["A", "B", "C", "D"]

for i in range(6):
    for j in range(4):
        alphanum_text = letters[j] + str(i + 1)
        if alphanum_text not in ["A6", "B2", "B3", "B6", "C1", "C2", "C3", "C4", "C5", "D1", "D2"]:
            draw.text((38 + 110 * i, 38 + 110 * j), alphanum_text, fill=(0, 0, 0), font = times_font)
image.show()
image.save("images/alphanum.png")

# create_tables
seen_cats = set()
summary_dict = {}
tiles_remaining_dict = {}
for state in all_substates:
    state_cat = get_state_category(state)
    if state_cat not in seen_cats:
        move_dict = {}
        tiles_remaining_dict[state_cat] = 18 - len(state.fixed_tiles)
        summary_dict[state_cat] = move_dict
        state_fixed = state.fixed_tiles
        seen_cats.add(state_cat)
        moves = state.find_moves()
        for move in moves:
            move_fixed_tiles = state_fixed.union(move)
            substate = game.state_dict[move_fixed_tiles]
            substate_cat = get_state_category(substate)
            eval_string = "Loss" if substate.evaluation else "Win"
            move_alpha = ",".join(sorted([tile_to_alphanum(tile) for tile in move]))
            move_summary = " & ".join([move_alpha, "\\hyperref[" + substate_cat + "]{" + substate_cat + "}", eval_string + " \\\\"])  + "\n"
            move_dict[move_alpha] = move_summary

doc_summary = open("summary.txt", "w")
state_order = [val[0] for val in sorted(tiles_remaining_dict.items(), key = lambda k: (-k[1], k[0]))]
for state_cat in state_order:
    _ = doc_summary.write('\\subsection{' + state_cat + '}\n')
    _ = doc_summary.write('\\label{' + state_cat + '}\n')
    _ = doc_summary.write("![" + state_cat + "](images/" + state_cat + ".png){width=70%}\n\n")
    if state_cat != 'Done':
        _ = doc_summary.write('\\begin{center}\n')
        _ = doc_summary.write('\\begin{tabular}{ |r c c| }\n')
        _ = doc_summary.write('\\hline\n')
        _ = doc_summary.write(" & ".join(["Move", "New State", "Result"]) + "\\\\\n")
        _ = doc_summary.write('\\hline\n')
        move_dict = summary_dict[state_cat]
        for move in sorted(move_dict.keys()):
            _ = doc_summary.write(move_dict[move])
        _ = doc_summary.write('\\hline\n')
        _ = doc_summary.write('\\end{tabular}\n')
        _ = doc_summary.write('\\end{center}\n')
        _ = doc_summary.write('\\pagebreak\n\n')
doc_summary.close()

######
image, draw = draw_start_board(width = 2, height = 1, y_offset = 0, x_offset = -1)
image.save("images/station.png")

image, draw = draw_clean_board(width = 1, height = 1)
add_tile(0, 0, (0, 3), draw, y_offset = 0, height = 1)
image.save("images/straight.png")

image, draw = draw_clean_board(width = 1, height = 1)
add_tile(0, 0, (1, 3), draw, y_offset = 0, height = 1)
image.save("images/bend.png")

image, draw = draw_start_board(y_offset = 0, x_offset = 1, height = 3, width = 5)
add_tiles(TileSet([Tile(0, 0, (0, 1)), Tile(0, 1, (2, 3)), Tile(-1, 1, (0, 1)), Tile(-1, 2, (0, 2)),
                   Tile(0, 2, (0, 3)), Tile(1, 2, (0, 3)), Tile(2, 2, (0, 3)), Tile(3, 2, (2, 3)),
                   Tile(3, 1, (1, 2)), Tile(3, 0, (1, 3))]), draw, y_offset = 0, x_offset = 1, height = 3)
image.save("images/example_finish.png")

image, draw = draw_start_board(y_offset = 3)
add_tiles(TileSet([Tile(0, 3, (0, 2)), Tile(0, 1, (1, 2)), Tile(0, 2, (1, 2)), Tile(0, 0, (0, 1)),
                   Tile(1, 0, (0, 3)), Tile(2, 0, (0, 3)), Tile(3, 0, (0, 3)), Tile(4, 0, (0, 3)),
                   Tile(1, 1, (0, 1)), Tile(2, 1, (0, 3)), Tile(3, 1, (0, 3)), Tile(4, 1, (0, 3)),
                   Tile(1, 2, (0, 2)), Tile(2, 2, (0, 3))]), draw, y_offset = 0)
image.save("images/not_enough_tiles.png")

image, draw = draw_start_board(y_offset = 1, height = 2, x_offset = -1, width = 4)
add_tiles(TileSet([Tile(0, 0, (0, 3)), Tile(1, 0, (0, 3)), Tile(2, 0, (1, 3)), Tile(3, 0, (0, 1)),
                   Tile(3, 1, (2, 3))]), draw, y_offset = 0, height = 2)
image.save("images/impossible_junction.png")

image, draw = draw_start_board(height = 2, width = 3, y_offset = 0, x_offset = -1)
add_tiles(TileSet([Tile(0, 1, (0, 1)), Tile(1, 1, (1, 3)), Tile(2, 1, (1, 2))]), draw, y_offset = 0, height = 2)
image.save("images/start_move_ex.png")


counter = 0
for state in all_substates:
    substate_cat = get_state_category(state)
    if substate_cat == "3-L5x":
        print(counter)
        counter = counter + 1
        filename = "images/3-L5x_ex" + str(counter) + ".png"
        image, draw = draw_winning_board()
        add_state_tiles(state, draw)
        image.save(filename)