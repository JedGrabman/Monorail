class Tile(Square):
    def __init__(self, x_pos, y_pos, directions):
        if len(directions) != 2:
            raise ValueError("Expected two values for directions")
        self.directions = directions
        super(Tile, self).__init__(x_pos, y_pos)

    def get_square(self):
        return Square(self.x_pos, self.y_pos)

    def __hash__(self):
        return(hash((self.x_pos, self.y_pos, min(self.directions), max(self.directions))))

    def __repr__(self):
        return("Tile(" + str(self.x_pos) + ", " + str(self.y_pos) + ", " + str(self.directions) + ")")

    def __str__(self):
        return(repr(self))


