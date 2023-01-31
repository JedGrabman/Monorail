from Square import Square

class SquareSet(set):
    def __init__(self, x_min_or_squares = None, x_max = None, y_min = None, y_max = None):
        self.hash = None
        if x_min_or_squares is None:
            self.set_init(set())
        elif isinstance(x_min_or_squares, set) or isinstance(x_min_or_squares, list):
            self.set_init(x_min_or_squares)
        else:
            self.range_init(x_min_or_squares, x_max, y_min, y_max)

    def set_init(self, squares):
        super().__init__(squares)

    def range_init(self, x_lim1, x_lim2, y_lim1, y_lim2):
        x_min = min(x_lim1, x_lim2)
        x_max = max(x_lim1, x_lim2)
        y_min = min(y_lim1, y_lim2)
        y_max = max(y_lim1, y_lim2)
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                self.add(Square(x, y))

    def __hash__(self):
        if self.hash is None:
            square_hashes = sorted([hash(square) for square in self])
            self.hash = hash(tuple(square_hashes))
        return(self.hash)