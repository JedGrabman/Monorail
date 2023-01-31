from MonorailState import MonorailState
from TileSet import TileSet
from Tile import Tile
import math

class MonorailGame():
    def __init__(self, start_tiles, tile_dict, paths_dict):
        self.start_tiles = start_tiles
        self.tile_dict = tile_dict
        self.paths_dict = paths_dict
        self.state_dict = dict()
        self.base_state = MonorailState(self.start_tiles, tile_dict, paths_dict)
        self.state_dict[self.base_state.fixed_tiles] = self.base_state
        self.counter = 0

    def get_tile_hash(self, tiles):
        tiles = [tile for tile in tiles]
        return(tuple(sorted([hash(tile) for tile in tiles])))

    def find_moves(self):
        return self.base_game.find_moves()

    def generate_dicts(self, paths):
        path_dict = dict()
        tile_dict = dict()
        for path in paths:
            path_dict[path] = dict()
            path_tiles = self.get_tiles(path)
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
        return((tile_dict, path_dict))

    def get_tiles(self, path):
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

    def create_state(self, fixed_tiles, tile_dict = None, paths_dict = None):
        fixed_tiles = TileSet(fixed_tiles.union({Tile(1, 0, (0, 3)), Tile(2, 0, (0, 3))}))
        if fixed_tiles in self.state_dict:
            return self.state_dict[fixed_tiles]
        if tile_dict is None:
            tile_dict = self.tile_dict
        if paths_dict is None:
            paths_dict = self.paths_dict
        move_paths = set(paths_dict)
        for tile in fixed_tiles:
            square = tile.get_square()
            directions = tile.directions
            tile_paths = self.tile_dict[square][tile.directions]
            move_paths.intersection_update(tile_paths)
        state_dicts = self.generate_dicts(move_paths)
        state_tile_dict = state_dicts[0]
        state_path_dict = state_dicts[1]
        substate = MonorailState(fixed_tiles, state_tile_dict, state_path_dict)
        return(substate)



    def play_game(self, state = None):
       # if state is not None:
       #     print("Testing state:", state.fixed_tiles)
        if state is None:
            state = self.base_state
        if state.evaluation is not None:
            return state.evaluation
        if state.fixed_tiles in self.state_dict and state is not self.base_state:
            evaluation = self.state_dict[state.fixed_tiles].evaluation
            state.evaluation = evaluation
            return evaluation
        else:
            self.state_dict[state.fixed_tiles] = state
        if(self.counter % 1000 == 0):
            print("test number:", self.counter)
        self.counter = self.counter + 1
       # print("Tiles remaining:", POOL_SIZE + 2 - len(state.fixed_tiles))
       # print("\n")
        moves = state.find_moves()
        for move in moves:
            fixed_tiles = state.fixed_tiles.copy()
            fixed_tiles.update(move)
            tile_hash = self.get_tile_hash(fixed_tiles)
            if tile_hash in self.state_dict:
                substate = self.state_dict[tile_hash]
                substate_evaluation = substate.evaluation
                if substate_evaluation == 0:
                    return 1
            else:
                move_paths = set(state.path_dict)
                tile_paths = set()
                # a.union(b) and b.union(a) are returning different types, so cast it.
                substate_fixed_tiles = TileSet(state.fixed_tiles.union(move))
                if (substate_fixed_tiles in self.state_dict):
                    substate = self.state_dict[substate_fixed_tiles]
                else:
                    for tile in move:
                        square = tile.get_square()
                        directions = tile.directions
                        tile_paths = state.tiles_dict[square][tile.directions]
                        move_paths.intersection_update(tile_paths)
                    substate_dicts = self.generate_dicts(move_paths)
                    substate_tile_dict = substate_dicts[0]
                    substate_path_dict = substate_dicts[1]
                    substate = MonorailState(substate_fixed_tiles, substate_tile_dict, substate_path_dict)
                    self.play_game(substate)
                if substate.evaluation == 0:
                    state.evaluation = 1
                    return(1)
        state.evaluation = 0
        return(0)