from SquareSet import SquareSet
from TileSet import TileSet
from Square import Square

class MonorailState:
    def __init__(self, fixed_tiles, tiles_dict, path_dict):
        POOL_SIZE = 16
      #  print(POOL_SIZE)
        self.fixed_tiles = fixed_tiles
        self.tiles_dict = tiles_dict
        self.path_dict = path_dict
        self.exhausted_squares = {tile.get_square() for tile in fixed_tiles}
        self.evaluation = None
        if len(path_dict) == 0:
            self.evaluation = 1
        if len(path_dict) == 1:
            if len(fixed_tiles) == POOL_SIZE + 2:
                self.evaluation = 0
        if len(fixed_tiles) > POOL_SIZE + 2:
            raise ValueError('too many fixed tiles!')
    
    def get_orientations(self, squareset):
        results = set()
        possible_paths = set(self.path_dict)
        for square in squareset:
            square_paths = set()
            for orientation in self.tiles_dict[square]:
                square_paths.update(self.tiles_dict[square][orientation])
            possible_paths.intersection_update(square_paths)
        
        while possible_paths:
            path = possible_paths.pop()
            tiles = TileSet()
            move_paths = possible_paths.copy()
            for square in squareset:
                tile = self.path_dict[path][square]
                orientation = tile.directions
                tiles.add(tile)
                move_paths.intersection_update(self.tiles_dict[square][orientation])
            possible_paths.difference_update(move_paths)
            results.add(tiles)

    #    for path in possible_paths:
     #       tiles = TileSet()
    #        for square in squareset:
    #            tiles.add(self.path_dict[path][square])
    #        results.add(tiles)
        return(results)


    def find_moves(self):
        squaresets = self.get_possible_squaresets()
        moves = set()
        for squareset in squaresets:
            squareset_moves = self.get_orientations(squareset)
            moves.update(squareset_moves)
        return(moves)

    def get_squaresets_by_square(self, square, possible_squares):
        results = set()
        results.add(SquareSet([square]))
        x_pos = square.x_pos
        y_pos = square.y_pos
        square_1_left = Square(x_pos - 1, y_pos)
        square_1_left_possible = False
        if square_1_left in possible_squares:
            square_1_left_possible = True
            results.add(SquareSet([square, square_1_left]))
            square_2_left = Square(x_pos - 2, y_pos)
            if square_2_left in possible_squares:
                results.add(SquareSet([square, square_1_left, square_2_left]))

        square_1_right = Square(x_pos + 1, y_pos)
        if square_1_right in possible_squares:
            results.add(SquareSet([square, square_1_right]))
            square_2_right = Square(x_pos + 2, y_pos)
            if square_2_right in possible_squares:
                results.add(SquareSet([square, square_1_right, square_2_right]))
            if square_1_left_possible:
                results.add(SquareSet([square_1_left, square, square_1_right]))

        square_1_up = Square(x_pos, y_pos + 1)
        square_1_up_possible = False
        if square_1_up in possible_squares:
            square_1_up_possible = True
            results.add(SquareSet([square, square_1_up]))
            square_2_up = Square(x_pos, y_pos + 2)
            if square_2_up in possible_squares:
                results.add(SquareSet([square, square_1_up, square_2_up]))

        square_1_down = Square(x_pos, y_pos - 1)
        if square_1_down in possible_squares:
            results.add(SquareSet([square, square_1_down]))
            square_2_down = Square(x_pos, y_pos - 2)
            if square_2_down in possible_squares:
                results.add(SquareSet([square, square_1_down, square_2_down]))
            if square_1_up_possible:
                results.add(SquareSet([square_1_up, square, square_1_down]))

   #     results.update({SquareSet(x_pos, x_pos + x_offset, y_pos, y_pos) for x_offset in range(-2, 3)})
   #     results.update({SquareSet(x_pos, x_pos, y_pos, y_pos + y_offset) for y_offset in range(-2, 3)})
   #     results.add(SquareSet(x_pos - 1, x_pos + 1, y_pos, y_pos))
   #     results.add(SquareSet(x_pos, x_pos, y_pos - 1, y_pos + 1))
   #     results = [squareset for squareset in results if 
   #                all([(square in self.tiles_dict) and (square not in self.exhausted_squares) for square in squareset])]
        return(results)

    def get_possible_squaresets(self):
        adjacent_squares = self.get_adjacent_squares()
        possible_squares = self.get_possible_squares()
        placeable_squares = adjacent_squares.intersection(possible_squares)
        results = set()
        for square in placeable_squares:
            square_squaresets = self.get_squaresets_by_square(square, possible_squares)
            results.update(square_squaresets)
        return(results)

    def get_adjacent_squares(self):
        results = SquareSet()
        for tile in self.fixed_tiles:
            for adj_square in tile.get_adjacencies():
                results.add(adj_square)
        return(results)

    def get_possible_squares(self):
        possible_squares = SquareSet([square for square in self.tiles_dict])
        possible_squares.difference_update(self.exhausted_squares)
        return(possible_squares)

    def __hash__(self):
        return(hash(self.fixed_tiles))