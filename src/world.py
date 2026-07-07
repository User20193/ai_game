import pygame
import random

class World:
    def __init__(self, screen_width, screen_height):
        self.TILE_SIZE = 8 # 8x8 пикселей

        # Для начала создадим простую сетку чанков.
        # В будущем здесь можно прикрутить шум Перлина для генерации биомов по сиду.
        # Пока мы сгенерируем словарь чанков "на лету" (ленивая генерация)
        self.chunks = {}
        self.chunk_surfaces = {} # Кэш поверхностей чанков
        self.CHUNK_SIZE = 16 # 16x16 тайлов в одном чанке

        # Ограничения карты (в чанках)
        self.WORLD_WIDTH = 10  # От 0 до 9
        self.WORLD_HEIGHT = 10 # От 0 до 9

        # Цвета для тестов (трава разных оттенков)
        self.colors = [
            (34, 139, 34),   # 0: Forest Green
            (50, 205, 50),   # 1: Lime Green
            (154, 205, 50),  # 2: Yellow Green
            (107, 142, 35),  # 3: Olive Drab
            (100, 100, 100)  # 4: Дорога (Серый)
        ]

    def get_chunk(self, chunk_x, chunk_y):
        """Возвращает чанк по его координатам. Если его нет - генерирует."""
        # Проверка выхода за границы мира
        if chunk_x < 0 or chunk_x >= self.WORLD_WIDTH or chunk_y < 0 or chunk_y >= self.WORLD_HEIGHT:
            return None

        chunk_pos = (chunk_x, chunk_y)
        if chunk_pos not in self.chunks:
            self.chunks[chunk_pos] = self.generate_chunk(chunk_x, chunk_y)
            self.render_chunk_surface(chunk_x, chunk_y) # Сразу кэшируем поверхность
        return self.chunks[chunk_pos]

    def generate_chunk(self, chunk_x, chunk_y):
        """Генерирует данные для чанка."""
        # Для фундамента мы просто заполняем чанк случайными тайлами травы
        # В будущем здесь будет использоваться noise(x, y, seed)
        chunk_data = []
        for y in range(self.CHUNK_SIZE):
            row = []
            for x in range(self.CHUNK_SIZE):
                # 0, 1, 2, 3 - индексы цветов в self.colors
                row.append(random.randint(0, len(self.colors) - 1))
            chunk_data.append(row)
        return chunk_data

    def render_chunk_surface(self, chunk_x, chunk_y):
        """Создает Pygame Surface для чанка, отрисовывая на ней все тайлы один раз."""
        chunk = self.chunks.get((chunk_x, chunk_y))
        if not chunk: return

        # Размер поверхности чанка в пикселях
        pixel_size = self.CHUNK_SIZE * self.TILE_SIZE
        surf = pygame.Surface((pixel_size, pixel_size))

        for ty in range(self.CHUNK_SIZE):
            for tx in range(self.CHUNK_SIZE):
                color_idx = chunk[ty][tx]
                color = self.colors[color_idx]
                rect = pygame.Rect(tx * self.TILE_SIZE, ty * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
                pygame.draw.rect(surf, color, rect)

        self.chunk_surfaces[(chunk_x, chunk_y)] = surf

    def set_tile(self, world_x, world_y, color_idx):
        """Изменяет тайл по мировым пиксельным координатам и перерисовывает чанк."""
        tile_x = int(world_x // self.TILE_SIZE)
        tile_y = int(world_y // self.TILE_SIZE)

        chunk_x = tile_x // self.CHUNK_SIZE
        chunk_y = tile_y // self.CHUNK_SIZE

        chunk = self.get_chunk(chunk_x, chunk_y)
        if chunk:
            local_x = tile_x % self.CHUNK_SIZE
            local_y = tile_y % self.CHUNK_SIZE
            chunk[local_y][local_x] = color_idx
            # Обновляем кэш поверхности
            self.render_chunk_surface(chunk_x, chunk_y)

    def render(self, surface, camera):
        """
        Отрисовывает только те чанки, которые попадают в область видимости камеры,
        используя заранее отрендеренные поверхности.
        """
        # Определяем, какую область мира мы сейчас видим, с учетом зума
        # Если зум < 1 (отдаление), мы видим больше мира
        visible_width = camera.width / camera.zoom
        visible_height = camera.height / camera.zoom

        # Левый верхний угол видимой области в координатах мира (с учетом того, что зум идет от центра)
        # Центр экрана в координатах мира:
        center_world_x = camera.x + camera.width / 2
        center_world_y = camera.y + camera.height / 2

        start_world_x = center_world_x - visible_width / 2
        start_world_y = center_world_y - visible_height / 2
        end_world_x = center_world_x + visible_width / 2
        end_world_y = center_world_y + visible_height / 2

        # Переводим координаты мира в индексы тайлов
        start_tile_x = int(start_world_x // self.TILE_SIZE)
        start_tile_y = int(start_world_y // self.TILE_SIZE)
        end_tile_x = int(end_world_x // self.TILE_SIZE) + 1
        end_tile_y = int(end_world_y // self.TILE_SIZE) + 1

        # Определяем, какие чанки нам нужно отрисовать
        start_chunk_x = start_tile_x // self.CHUNK_SIZE
        start_chunk_y = start_tile_y // self.CHUNK_SIZE
        end_chunk_x = end_tile_x // self.CHUNK_SIZE
        end_chunk_y = end_tile_y // self.CHUNK_SIZE

        for cy in range(start_chunk_y, end_chunk_y + 1):
            for cx in range(start_chunk_x, end_chunk_x + 1):
                chunk = self.get_chunk(cx, cy)
                if not chunk: continue # Пропускаем, если вышли за границы мира

                chunk_surf = self.chunk_surfaces.get((cx, cy))
                if chunk_surf:
                    # Вычисляем позицию чанка в мире
                    world_rect = pygame.Rect(
                        cx * self.CHUNK_SIZE * self.TILE_SIZE,
                        cy * self.CHUNK_SIZE * self.TILE_SIZE,
                        self.CHUNK_SIZE * self.TILE_SIZE,
                        self.CHUNK_SIZE * self.TILE_SIZE
                    )

                    # Получаем позицию на экране с учетом зума камеры
                    screen_rect = camera.apply(world_rect)

                    # Масштабируем поверхность чанка
                    # Чтобы избежать искажений, преобразуем к целочисленным размерам
                    target_size = (int(screen_rect.width) + 1, int(screen_rect.height) + 1)
                    scaled_surf = pygame.transform.scale(chunk_surf, target_size)

                    surface.blit(scaled_surf, (screen_rect.x, screen_rect.y))
