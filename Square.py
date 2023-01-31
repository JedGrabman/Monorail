class Square(object):
    _registry = dict()

    def __new__(cls, x_pos, y_pos):
        if (x_pos, y_pos) in Square._registry:
            return Square._registry[x_pos, y_pos]
        instance = super().__new__(cls)  # don't pass extra *args and **kwargs to obj.__new__
        Square._registry[x_pos,y_pos] = instance
        return instance

    def __init__(self, x_pos, y_pos):
        if hasattr(self, "x_pos"):  # avoid running init twice if the attribute is already set
            return
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.adjacencies = None
        self.hash = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return(self.x_pos == other.x_pos and self.y_pos == other.y_pos)
        else:
            return False

    def __hash__(self):
        if self.hash is None:
            self.hash = hash((self.x_pos, self.y_pos))
        return(self.hash)

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


