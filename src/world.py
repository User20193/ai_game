import pygame
import random

class World:
    def __init__(self, screen_width, screen_height):
        self.TILE_SIZE = 8 # 8x8 пикселей

        # Для начала создадим простую сетку чанков.
        # В будущем здесь можно прикрутить шум Перлина для генерации биомов по сиду.
        # Пока мы сгенерируем словарь чанков "на лету" (ленивая генерация)
        self.chunks = {}
        self.CHUNK_SIZE = 16 # 16x16 тайлов в одном чанке

        # Цвета для тестов (трава разных оттенков)
        self.colors = [
            (34, 139, 34),   # Forest Green
            (50, 205, 50),   # Lime Green
            (154, 205, 50),  # Yellow Green
            (107, 142, 35)   # Olive Drab
        ]

    def get_chunk(self, chunk_x, chunk_y):
        """Возвращает чанк по его координатам. Если его нет - генерирует."""
        chunk_pos = (chunk_x, chunk_y)
        if chunk_pos not in self.chunks:
            self.chunks[chunk_pos] = self.generate_chunk(chunk_x, chunk_y)
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

    def render(self, surface, camera):
        """
        Отрисовывает только те тайлы, которые попадают в область видимости камеры.
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

                # Отрисовываем тайлы внутри чанка
                for ty in range(self.CHUNK_SIZE):
                    for tx in range(self.CHUNK_SIZE):
                        world_tile_x = cx * self.CHUNK_SIZE + tx
                        world_tile_y = cy * self.CHUNK_SIZE + ty

                        # Проверяем, попадает ли тайл в видимую область (для оптимизации краев чанков)
                        if (start_tile_x <= world_tile_x <= end_tile_x and
                            start_tile_y <= world_tile_y <= end_tile_y):

                            # Получаем цвет тайла
                            color_idx = chunk[ty][tx]
                            color = self.colors[color_idx]

                            # Реальные координаты тайла в мире
                            world_rect = pygame.Rect(
                                world_tile_x * self.TILE_SIZE,
                                world_tile_y * self.TILE_SIZE,
                                self.TILE_SIZE,
                                self.TILE_SIZE
                            )

                            # Преобразуем через камеру для отрисовки на экране
                            screen_rect = camera.apply(world_rect)

                            # Чтобы избежать зазоров между тайлами из-за округления Float при зуме,
                            # мы можем округлить (ceil) размеры
                            screen_rect.width = int(screen_rect.width) + 1
                            screen_rect.height = int(screen_rect.height) + 1

                            pygame.draw.rect(surface, color, screen_rect)
