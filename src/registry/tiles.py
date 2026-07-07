class Tile:
    def __init__(self, id, name, color, is_solid=False):
        self.id = id
        self.name = name
        self.color = color
        self.is_solid = is_solid

class TileRegistry:
    def __init__(self):
        self.tiles = {}
        self._register_default_tiles()

    def register(self, tile):
        self.tiles[tile.id] = tile

    def get_tile(self, id):
        # Возвращаем Tile. Если ID нет или он None, возвращаем "Воздух"
        if id is None or id not in self.tiles:
            return Tile(-1, "Air", (0, 0, 0), is_solid=False)
        return self.tiles[id]

    def _register_default_tiles(self):
        # 0: Чистая трава (Светло-зеленый)
        self.register(Tile(0, "Grass", (124, 204, 31)))
        # 1-3 зарезервированы (ранее шум)

        # 4: Дорога/Тротуар (Светло-серый)
        self.register(Tile(4, "Sidewalk", (180, 180, 180)))

        # Здания (стены непроходимы)
        self.register(Tile(5, "Wall", (240, 230, 210), is_solid=True))
        # Крыша проходима для логики (она на другом слое)
        self.register(Tile(6, "Roof", (178, 34, 34)))

        # Двери, пол
        self.register(Tile(7, "Door", (139, 69, 19)))
        self.register(Tile(8, "WoodFloor", (205, 170, 125)))

        # Мебель (непроходимая)
        self.register(Tile(9, "Desk", (101, 67, 33), is_solid=True))
        self.register(Tile(10, "Bed", (65, 105, 225), is_solid=True))
        self.register(Tile(11, "Chair", (210, 105, 30), is_solid=True))
