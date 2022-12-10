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
        return((tile_dict, path_dict))

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
                    self.state_dict[substate.fixed_tiles] = substate
                if substate.evaluation == 0:
                    state.evaluation = 1
                    return(1)
        state.evaluation = 0
        return(0)