import pygame
import random

class World:
    def __init__(self, screen_width, screen_height):
        self.TILE_SIZE = 8 # 8x8 пикселей

        # Словари чанков для двух слоев
        self.chunks_ground = {}
        self.chunks_roof = {}

        # Кэш поверхностей для двух слоев
        self.chunk_surfaces_ground = {}
        self.chunk_surfaces_roof = {}

        self.CHUNK_SIZE = 16 # 16x16 тайлов в одном чанке

        # Ограничения карты (в чанках)
        self.WORLD_WIDTH = 20  # От 0 до 19
        self.WORLD_HEIGHT = 20 # От 0 до 19

        # Цвета для тестов (трава разных оттенков)
        self.colors = [
            (34, 139, 34),   # 0: Forest Green
            (50, 205, 50),   # 1: Lime Green
            (154, 205, 50),  # 2: Yellow Green
            (107, 142, 35),  # 3: Olive Drab
            (100, 100, 100), # 4: Дорога (Серый)
            (240, 230, 210), # 5: Стена Мэрии (Бежевый)
            (178, 34, 34),   # 6: Крыша Мэрии (Темно-красный)
            (139, 69, 19),   # 7: Дверь (Коричневый)
            (205, 170, 125), # 8: Пол внутри (Светлое дерево)
            (101, 67, 33),   # 9: Стойка (Темное дерево)
            (65, 105, 225),  # 10: Вода (Синий)
            (0, 100, 0),     # 11: Дерево Крона (Темно-зеленый)
            (139, 69, 19)    # 12: Ствол дерева (Коричневый)
        ]

        # Генерируем центр города при старте
        self.build_city_center()

    def get_chunk(self, chunk_x, chunk_y):
        """Возвращает словари слоев чанка по его координатам. Если их нет - генерирует."""
        if chunk_x < 0 or chunk_x >= self.WORLD_WIDTH or chunk_y < 0 or chunk_y >= self.WORLD_HEIGHT:
            return None, None

        chunk_pos = (chunk_x, chunk_y)
        if chunk_pos not in self.chunks_ground:
            # Инициализируем пустые матрицы
            ground_data = [[None for _ in range(self.CHUNK_SIZE)] for _ in range(self.CHUNK_SIZE)]
            roof_data = [[None for _ in range(self.CHUNK_SIZE)] for _ in range(self.CHUNK_SIZE)]

            import math
            for ty in range(self.CHUNK_SIZE):
                for tx in range(self.CHUNK_SIZE):
                    world_tx = chunk_x * self.CHUNK_SIZE + tx
                    world_ty = chunk_y * self.CHUNK_SIZE + ty

                    # Псевдо-шум на основе синусов для генерации биомов
                    noise_val = math.sin(world_tx * 0.1) + math.cos(world_ty * 0.1) + math.sin((world_tx + world_ty) * 0.05)

                    if noise_val > 1.2:
                        # Вода
                        ground_data[ty][tx] = 10
                    elif noise_val < -1.0:
                        # Лес
                        ground_data[ty][tx] = random.choice([0, 1]) # Темная трава
                        # Добавляем дерево на слое крыши (каждый второй тайл, чтобы не было сплошной массы)
                        if (tx + ty) % 2 == 0:
                            roof_data[ty][tx] = 11 # Крона
                            ground_data[ty][tx] = 12 # Ствол
                    else:
                        # Обычная трава
                        if random.random() > 0.9:
                            ground_data[ty][tx] = random.choice([2, 3]) # Редкие вкрапления
                        else:
                            ground_data[ty][tx] = random.choice([0, 1]) # Базовая трава

            self.chunks_ground[chunk_pos] = ground_data
            self.chunks_roof[chunk_pos] = roof_data
            self.render_chunk_surface(chunk_x, chunk_y)

        return self.chunks_ground[chunk_pos], self.chunks_roof[chunk_pos]

    def render_chunk_surface(self, chunk_x, chunk_y):
        """Создает Pygame Surface для земли и крыши чанка, отрисовывая все тайлы."""
        ground_chunk = self.chunks_ground.get((chunk_x, chunk_y))
        roof_chunk = self.chunks_roof.get((chunk_x, chunk_y))
        if not ground_chunk or not roof_chunk: return

        pixel_size = self.CHUNK_SIZE * self.TILE_SIZE

        # Ground Layer
        surf_ground = pygame.Surface((pixel_size, pixel_size))
        for ty in range(self.CHUNK_SIZE):
            for tx in range(self.CHUNK_SIZE):
                color_idx = ground_chunk[ty][tx]
                if color_idx is not None:
                    rect = pygame.Rect(tx * self.TILE_SIZE, ty * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
                    pygame.draw.rect(surf_ground, self.colors[color_idx], rect)
        self.chunk_surfaces_ground[(chunk_x, chunk_y)] = surf_ground

        # Roof Layer (с альфа-каналом, так как он прозрачный)
        surf_roof = pygame.Surface((pixel_size, pixel_size), pygame.SRCALPHA)
        for ty in range(self.CHUNK_SIZE):
            for tx in range(self.CHUNK_SIZE):
                color_idx = roof_chunk[ty][tx]
                if color_idx is not None:
                    rect = pygame.Rect(tx * self.TILE_SIZE, ty * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
                    pygame.draw.rect(surf_roof, self.colors[color_idx], rect)
        self.chunk_surfaces_roof[(chunk_x, chunk_y)] = surf_roof

    def set_tile_by_index(self, tile_x, tile_y, color_idx, layer="ground"):
        """Изменяет тайл по его индексным координатам в определенном слое."""
        chunk_x = tile_x // self.CHUNK_SIZE
        chunk_y = tile_y // self.CHUNK_SIZE

        ground_chunk, roof_chunk = self.get_chunk(chunk_x, chunk_y)
        if ground_chunk and roof_chunk:
            local_x = tile_x % self.CHUNK_SIZE
            local_y = tile_y % self.CHUNK_SIZE
            if layer == "ground":
                ground_chunk[local_y][local_x] = color_idx
            elif layer == "roof":
                roof_chunk[local_y][local_x] = color_idx
            self.render_chunk_surface(chunk_x, chunk_y)

    def build_city_center(self):
        """Генерирует все чанки и строит Мэрию с дорогой в центре карты."""
        # Сначала генерируем все чанки
        for cy in range(self.WORLD_HEIGHT):
            for cx in range(self.WORLD_WIDTH):
                self.get_chunk(cx, cy)

        # Центр мира в тайлах
        center_tx = (self.WORLD_WIDTH * self.CHUNK_SIZE) // 2
        center_ty = (self.WORLD_HEIGHT * self.CHUNK_SIZE) // 2

        # Размеры мэрии (в тайлах)
        b_width = 14
        b_height = 10

        start_x = center_tx - b_width // 2
        start_y = center_ty - b_height // 2

        # Очищаем площадь под Мэрию (убираем деревья и воду)
        for y in range(start_y - 2, start_y + b_height + 4):
            for x in range(start_x - 8, start_x + b_width + 8):
                self.set_tile_by_index(x, y, 0, layer="ground") # Трава
                self.set_tile_by_index(x, y, None, layer="roof") # Очищаем крышу (убираем деревья)

        # Рисуем здание (интерьер и стены) на слое ground
        for y in range(start_y, start_y + b_height):
            for x in range(start_x, start_x + b_width):
                # Периметр (западная, восточная, южная, северная стены)
                if x == start_x or x == start_x + b_width - 1 or y == start_y + b_height - 1 or y == start_y or y == start_y + 1:
                    self.set_tile_by_index(x, y, 5, layer="ground") # Стена
                # Внутреннее пространство
                else:
                    self.set_tile_by_index(x, y, 8, layer="ground") # Пол

                # Всю площадь мэрии покрываем крышей на слое roof
                self.set_tile_by_index(x, y, 6, layer="roof") # Крыша

        # Рисуем стойку внутри (reception)
        reception_y = start_y + 4
        for x in range(start_x + 3, start_x + b_width - 3):
            self.set_tile_by_index(x, reception_y, 9, layer="ground")

        # Рисуем дверь
        door_x = center_tx
        door_y = start_y + b_height - 1
        # Делаем проход шире (2 тайла)
        self.set_tile_by_index(door_x, door_y, 8, layer="ground") # Пол на входе
        self.set_tile_by_index(door_x - 1, door_y, 8, layer="ground")
        self.set_tile_by_index(door_x, door_y - 1, 8, layer="ground")
        self.set_tile_by_index(door_x - 1, door_y - 1, 8, layer="ground")

        # Сами двери чуть выдвинуты (или открыты)
        self.set_tile_by_index(door_x + 1, door_y, 7, layer="ground")
        self.set_tile_by_index(door_x - 2, door_y, 7, layer="ground")

        # Убираем крышу над входом, чтобы было видно дверь
        self.set_tile_by_index(door_x, door_y, None, layer="roof")
        self.set_tile_by_index(door_x - 1, door_y, None, layer="roof")

        # Рисуем дорогу перед мэрией
        road_y = start_y + b_height
        for x in range(start_x - 6, start_x + b_width + 6):
            self.set_tile_by_index(x, road_y, 4, layer="ground")
            self.set_tile_by_index(x, road_y + 1, 4, layer="ground")
            self.set_tile_by_index(x, road_y + 2, 4, layer="ground")

    def _render_layer(self, surface, camera, chunk_surfaces_dict):
        """Вспомогательный метод для рендера конкретного слоя."""
        visible_width = camera.width / camera.zoom
        visible_height = camera.height / camera.zoom

        center_world_x = camera.x + camera.width / 2
        center_world_y = camera.y + camera.height / 2

        start_world_x = center_world_x - visible_width / 2
        start_world_y = center_world_y - visible_height / 2
        end_world_x = center_world_x + visible_width / 2
        end_world_y = center_world_y + visible_height / 2

        start_tile_x = int(start_world_x // self.TILE_SIZE)
        start_tile_y = int(start_world_y // self.TILE_SIZE)
        end_tile_x = int(end_world_x // self.TILE_SIZE) + 1
        end_tile_y = int(end_world_y // self.TILE_SIZE) + 1

        start_chunk_x = start_tile_x // self.CHUNK_SIZE
        start_chunk_y = start_tile_y // self.CHUNK_SIZE
        end_chunk_x = end_tile_x // self.CHUNK_SIZE
        end_chunk_y = end_tile_y // self.CHUNK_SIZE

        for cy in range(start_chunk_y, end_chunk_y + 1):
            for cx in range(start_chunk_x, end_chunk_x + 1):
                # Убеждаемся, что чанк сгенерирован (если мы на краю карты)
                self.get_chunk(cx, cy)

                chunk_surf = chunk_surfaces_dict.get((cx, cy))
                if chunk_surf:
                    world_rect = pygame.Rect(
                        cx * self.CHUNK_SIZE * self.TILE_SIZE,
                        cy * self.CHUNK_SIZE * self.TILE_SIZE,
                        self.CHUNK_SIZE * self.TILE_SIZE,
                        self.CHUNK_SIZE * self.TILE_SIZE
                    )

                    screen_rect = camera.apply(world_rect)
                    target_size = (int(screen_rect.width) + 1, int(screen_rect.height) + 1)
                    scaled_surf = pygame.transform.scale(chunk_surf, target_size)
                    surface.blit(scaled_surf, (screen_rect.x, screen_rect.y))

    def render_ground(self, surface, camera):
        self._render_layer(surface, camera, self.chunk_surfaces_ground)

    def render_roof(self, surface, camera):
        self._render_layer(surface, camera, self.chunk_surfaces_roof)
