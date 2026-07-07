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

    def render(self, surface):
        # Заливаем фон базовым цветом (например, цвет пустоты вокруг карты)
        surface.fill((30, 30, 30))

        # Отрисовываем мир с учетом позиции и зума камеры
        self.world.render(surface, self.camera)

        # Отрисовываем отладочную информацию (Координаты камеры и зум)
        debug_text = f"Cam: ({int(self.camera.x)}, {int(self.camera.y)}) | Zoom: {self.camera.zoom:.2f}"
        try:
            debug_surf = self.game.menu_font.render(debug_text, True, (255, 255, 255))
            surface.blit(debug_surf, (10, 10))
        except:
            pass # Если шрифт вдруг не прогрузился
