import pygame
from .base_state import State
from src.camera import Camera
from src.world import World

class PlayState(State):
    def __init__(self, game):
        super().__init__(game)

        # Инициализируем мир и камеру
        self.world = World(self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT)
        self.camera = Camera(self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT)

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # По нажатию ESC возвращаемся в предыдущее состояние (меню)
                    self.exit_state()

        # Обновляем логику камеры (передаем нажатые клавиши и события для зума)
        keys = pygame.key.get_pressed()
        self.camera.update(dt, keys, events)

        # Обновляем размеры мира в камере, на случай если был переключен полноэкранный режим
        self.camera.update_screen_size(self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT)

        # Логика строительства
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_x, world_y = self.camera.screen_to_world(mouse_x, mouse_y)

        self.hovered_tile_x = int(world_x // self.world.TILE_SIZE)
        self.hovered_tile_y = int(world_y // self.world.TILE_SIZE)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Левый клик (ЛКМ)
                    # Строим "дорогу" (индекс 4 в массиве цветов мира)
                    self.world.set_tile(world_x, world_y, 4)

    def render(self, surface):
        # Заливаем фон базовым цветом (например, цвет пустоты вокруг карты)
        surface.fill((30, 30, 30))

        # Отрисовываем мир с учетом позиции и зума камеры
        self.world.render(surface, self.camera)

        # Отрисовка курсора строителя
        # Проверяем, что курсор находится в пределах мира
        max_tile_x = self.world.WORLD_WIDTH * self.world.CHUNK_SIZE
        max_tile_y = self.world.WORLD_HEIGHT * self.world.CHUNK_SIZE

        if 0 <= self.hovered_tile_x < max_tile_x and 0 <= self.hovered_tile_y < max_tile_y:
            hover_rect_world = pygame.Rect(
                self.hovered_tile_x * self.world.TILE_SIZE,
                self.hovered_tile_y * self.world.TILE_SIZE,
                self.world.TILE_SIZE,
                self.world.TILE_SIZE
            )
            hover_rect_screen = self.camera.apply(hover_rect_world)

            # Рисуем полупрозрачный белый квадрат поверх тайла
            cursor_surf = pygame.Surface((hover_rect_screen.width, hover_rect_screen.height), pygame.SRCALPHA)
            cursor_surf.fill((255, 255, 255, 100))
            surface.blit(cursor_surf, (hover_rect_screen.x, hover_rect_screen.y))

        # Отрисовываем отладочную информацию (Координаты камеры и зум)
        debug_text = f"Cam: ({int(self.camera.x)}, {int(self.camera.y)}) | Zoom: {self.camera.zoom:.2f}"
        try:
            debug_surf = self.game.menu_font.render(debug_text, True, (255, 255, 255))
            surface.blit(debug_surf, (10, 10))
        except:
            pass # Если шрифт вдруг не прогрузился
