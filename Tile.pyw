from Square import Square
class Tile(Square):
    _registry = dict()

    def __new__(cls, x_pos, y_pos, directions):
        if type(directions) != tuple:
            raise TypeError('directions must be a tuple!')
        if len(directions) != 2:
            raise ValueError('directions must have 2 values')
        if not (directions[0] < directions[1]):
            raise ValueError('smaller direction must be listed first!')
        if (x_pos, y_pos, directions) in Tile._registry:
            return Tile._registry[x_pos, y_pos, directions]
        instance = object.__new__(Tile)  # don't pass extra *args and **kwargs to obj.__new__
        Tile._registry[x_pos, y_pos, directions] = instance
        return instance

    def __init__(self, x_pos, y_pos, directions):
        if len(directions) != 2:
            raise ValueError("Expected two values for directions")
        if type(directions) != tuple:
            raise ValueError("directions must be a tuple!")
        self.directions = directions
        super(Tile, self).__init__(x_pos, y_pos)
        self.hash = None

    def get_square(self):
        return Square(self.x_pos, self.y_pos)

    def __hash__(self):
        if self.hash is None:
            self.hash = hash((self.x_pos, self.y_pos, min(self.directions), max(self.directions)))
        return(self.hash)

    def __repr__(self):
        return("Tile(" + str(self.x_pos) + ", " + str(self.y_pos) + ", " + str(self.directions) + ")")

    def __str__(self):
        return(repr(self))


