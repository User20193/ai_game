import pygame
import random
from src.registry.tiles import TileRegistry
from src.world_gen.prefabs import get_city_hall_prefab, get_mayor_house_prefab, apply_prefab

class World:
    def __init__(self, screen_width, screen_height):
        self.TILE_SIZE = 8 # 8x8 пикселей

        # Словари чанков для двух слоев
        self.chunks_ground = {}
        self.chunks_roof = {}

        # Кэш поверхностей для двух слоев
        self.chunk_surfaces_ground = {}
        self.chunk_surfaces_roof = {}

        # Очередь для отложенной перерисовки чанков (оптимизация)
        self.dirty_ground = set()
        self.dirty_roof = set()

        self.CHUNK_SIZE = 16 # 16x16 тайлов в одном чанке

        # Ограничения карты (в чанках)
        self.WORLD_WIDTH = 20  # От 0 до 19
        self.WORLD_HEIGHT = 20 # От 0 до 19

        # Реестр тайлов
        self.tile_registry = TileRegistry()

        # Генерируем центр города при старте
        self.build_city_center()

    def get_tile_index(self, world_x, world_y, layer="ground"):
        """Возвращает индекс цвета тайла по пиксельным мировым координатам."""
        tile_x = int(world_x // self.TILE_SIZE)
        tile_y = int(world_y // self.TILE_SIZE)

        chunk_x = tile_x // self.CHUNK_SIZE
        chunk_y = tile_y // self.CHUNK_SIZE

        ground_chunk, roof_chunk = self.get_chunk(chunk_x, chunk_y)
        if ground_chunk and roof_chunk:
            local_x = tile_x % self.CHUNK_SIZE
            local_y = tile_y % self.CHUNK_SIZE
            if layer == "ground":
                return ground_chunk[local_y][local_x]
            elif layer == "roof":
                return roof_chunk[local_y][local_x]
        return None

    def get_chunk(self, chunk_x, chunk_y):
        """Возвращает словари слоев чанка по его координатам. Если их нет - генерирует."""
        if chunk_x < 0 or chunk_x >= self.WORLD_WIDTH or chunk_y < 0 or chunk_y >= self.WORLD_HEIGHT:
            return None, None

        chunk_pos = (chunk_x, chunk_y)
        if chunk_pos not in self.chunks_ground:
            # Инициализируем пустые матрицы
            ground_data = [[0 for _ in range(self.CHUNK_SIZE)] for _ in range(self.CHUNK_SIZE)] # 0 - чистая трава
            roof_data = [[None for _ in range(self.CHUNK_SIZE)] for _ in range(self.CHUNK_SIZE)]

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
                    tile = self.tile_registry.get_tile(color_idx)
                    rect = pygame.Rect(tx * self.TILE_SIZE, ty * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
                    pygame.draw.rect(surf_ground, tile.color, rect)
        self.chunk_surfaces_ground[(chunk_x, chunk_y)] = surf_ground

        # Roof Layer (с альфа-каналом, так как он прозрачный)
        surf_roof = pygame.Surface((pixel_size, pixel_size), pygame.SRCALPHA)
        for ty in range(self.CHUNK_SIZE):
            for tx in range(self.CHUNK_SIZE):
                color_idx = roof_chunk[ty][tx]
                if color_idx is not None:
                    tile = self.tile_registry.get_tile(color_idx)
                    rect = pygame.Rect(tx * self.TILE_SIZE, ty * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
                    pygame.draw.rect(surf_roof, tile.color, rect)
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
                self.dirty_ground.add((chunk_x, chunk_y))
            elif layer == "roof":
                roof_chunk[local_y][local_x] = color_idx
                self.dirty_roof.add((chunk_x, chunk_y))

    def update_dirty_chunks(self):
        """Перерисовывает только измененные чанки."""
        chunks_to_render = self.dirty_ground.union(self.dirty_roof)
        for chunk_x, chunk_y in chunks_to_render:
            self.render_chunk_surface(chunk_x, chunk_y)

        self.dirty_ground.clear()
        self.dirty_roof.clear()

    def build_city_center(self):
        """Генерирует все чанки и строит здания в центре карты через систему префабов."""
        # Сначала генерируем базовую траву для всех чанков
        for cy in range(self.WORLD_HEIGHT):
            for cx in range(self.WORLD_WIDTH):
                self.get_chunk(cx, cy)

        # Центр мира в тайлах
        center_tx = (self.WORLD_WIDTH * self.CHUNK_SIZE) // 2
        center_ty = (self.WORLD_HEIGHT * self.CHUNK_SIZE) // 2

        # Префаб Мэрии
        city_hall = get_city_hall_prefab()
        ch_x = center_tx - city_hall.width // 2
        ch_y = center_ty - city_hall.height // 2
        apply_prefab(self, ch_x, ch_y, city_hall)

        # Префаб Домика Мэра
        mayor_house = get_mayor_house_prefab()
        mh_x = ch_x + city_hall.width + 6
        mh_y = ch_y + 2
        apply_prefab(self, mh_x, mh_y, mayor_house)

        # Рисуем дорогу перед мэрией
        road_y = ch_y + city_hall.height
        for x in range(ch_x - 6, ch_x + city_hall.width + 20):
            for dy in range(3):
                self.set_tile_by_index(x, road_y + dy, 4, layer="ground")

        # Дорожка от дома мэра к основной дороге
        mh_door_x = mh_x + mayor_house.width // 2
        for y in range(mh_y + mayor_house.height, road_y):
            self.set_tile_by_index(mh_door_x, y, 4, layer="ground")
            self.set_tile_by_index(mh_door_x - 1, y, 4, layer="ground")

        # Открытые двери (выходят за рамки префаба, т.к. "открыты" на улицу)
        door_x = center_tx
        door_y = ch_y + city_hall.height - 1
        self.set_tile_by_index(door_x + 1, door_y, 7, layer="ground")
        self.set_tile_by_index(door_x - 2, door_y, 7, layer="ground")

        self.set_tile_by_index(mh_door_x, mh_y + mayor_house.height, 7, layer="ground")

        self.update_dirty_chunks()

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
