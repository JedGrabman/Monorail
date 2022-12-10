class Square(object):
    def __init__(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.adjacencies = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return(self.x_pos == other.x_pos and self.y_pos == other.y_pos)
        else:
            return False

    def __hash__(self):
        return(hash((self.x_pos, self.y_pos)))

    def find_adjacencies(self):
        adjacencies = set()
        adjacencies.add(Square(self.x_pos + 1, self.y_pos))
        adjacencies.add(Square(self.x_pos - 1, self.y_pos))
        adjacencies.add(Square(self.x_pos, self.y_pos + 1))
        adjacencies.add(Square(self.x_pos, self.y_pos - 1))
        self.adjacencies = adjacencies
        return(self.adjacencies)

    def get_adjacencies(self):
        if self.adjacencies is None:
            self.find_adjacencies()
        return(self.adjacencies)

    def __str__(self):
        return("Square at (" + str(self.x_pos) + "," + str(self.y_pos) + ")")

    def __repr__(self):
        return("Square(" + str(self.x_pos) + "," + str(self.y_pos) + ")")


