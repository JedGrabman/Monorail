class TileSet(set):
    def __init__(self, tiles = None):
        self.hash = None
        if tiles is None:
            super().__init__()
        else:
            super().__init__(tiles)
    
    def __hash__(self):
        if self.hash is None:
            tile_hashes = sorted([hash(tile) for tile in self]) #5.109
            self.hash = hash(tuple(tile_hashes))
        return(self.hash)

    def union(self, other):
        return(TileSet(super().union(other)))