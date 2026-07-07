class Prefab:
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        # Слои префаба
        self.ground_layer = [[None for _ in range(width)] for _ in range(height)]
        self.roof_layer = [[None for _ in range(width)] for _ in range(height)]

    def set_tile(self, x, y, tile_id, layer="ground"):
        if 0 <= x < self.width and 0 <= y < self.height:
            if layer == "ground":
                self.ground_layer[y][x] = tile_id
            elif layer == "roof":
                self.roof_layer[y][x] = tile_id

    def fill_rect(self, start_x, start_y, w, h, tile_id, layer="ground"):
        for y in range(start_y, start_y + h):
            for x in range(start_x, start_x + w):
                self.set_tile(x, y, tile_id, layer)

    def draw_perimeter(self, start_x, start_y, w, h, tile_id, layer="ground"):
        for x in range(start_x, start_x + w):
            self.set_tile(x, start_y, tile_id, layer)
            self.set_tile(x, start_y + h - 1, tile_id, layer)
        for y in range(start_y + 1, start_y + h - 1):
            self.set_tile(start_x, y, tile_id, layer)
            self.set_tile(start_x + w - 1, y, tile_id, layer)

def apply_prefab(world, start_x, start_y, prefab):
    """Накладывает префаб на мир по мировым координатам тайлов."""
    for y in range(prefab.height):
        for x in range(prefab.width):
            world_x = start_x + x
            world_y = start_y + y

            ground_tile = prefab.ground_layer[y][x]
            if ground_tile is not None:
                world.set_tile_by_index(world_x, world_y, ground_tile, layer="ground")

            roof_tile = prefab.roof_layer[y][x]
            if roof_tile is not None:
                world.set_tile_by_index(world_x, world_y, roof_tile, layer="roof")

def get_mayor_house_prefab():
    p = Prefab("MayorHouse", 8, 6)

    # Пол и стены
    p.fill_rect(0, 0, 8, 6, 8, "ground") # Пол везде внутри
    p.draw_perimeter(0, 0, 8, 6, 5, "ground") # Стены по периметру

    # Крыша
    p.fill_rect(0, 0, 8, 6, 6, "roof")

    # Интерьер
    p.set_tile(1, 1, 10, "ground") # Кровать
    p.set_tile(1, 2, 10, "ground")
    p.set_tile(6, 2, 11, "ground") # Стул

    # Двери
    door_x = 4
    door_y = 5
    p.set_tile(door_x, door_y, 8, "ground") # Пол на пороге
    p.set_tile(door_x, door_y, None, "roof") # Убрать крышу над дверью

    return p

def get_city_hall_prefab():
    p = Prefab("CityHall", 14, 10)

    # Пол и Стены
    p.fill_rect(0, 0, 14, 10, 8, "ground")
    p.draw_perimeter(0, 0, 14, 10, 5, "ground")

    # Крыша (северная стена-козырек тоже выглядит как крыша)
    p.fill_rect(0, 0, 14, 2, 6, "ground")
    p.fill_rect(0, 0, 14, 10, 6, "roof")

    # Стойка Reception
    p.fill_rect(3, 4, 8, 1, 9, "ground")

    # Двери
    door_x = 7
    door_y = 9
    p.fill_rect(door_x - 1, door_y - 1, 2, 2, 8, "ground") # Пол у дверей

    p.set_tile(door_x, door_y, None, "roof") # Убираем крышу над входом
    p.set_tile(door_x - 1, door_y, None, "roof")

    return p
