import pygame
from .base_state import State
from src.camera import Camera
from src.world import World
from src.entities.citizen import Citizen

class PlayState(State):
    def __init__(self, game):
        super().__init__(game)

        # Инициализируем мир и камеру
        self.world = World(self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT)
        self.camera = Camera(self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT)

        # Центрируем камеру на карте (чтобы центр мира был в центре экрана)
        # Размер мира в пикселях: (WORLD_WIDTH * CHUNK_SIZE * TILE_SIZE)
        world_pixel_width = self.world.WORLD_WIDTH * self.world.CHUNK_SIZE * self.world.TILE_SIZE
        world_pixel_height = self.world.WORLD_HEIGHT * self.world.CHUNK_SIZE * self.world.TILE_SIZE

        # Чтобы объект оказался в центре экрана, нужно из координаты объекта вычесть половину экрана
        self.camera.x = (world_pixel_width / 2) - (self.camera.width / 2)
        self.camera.y = (world_pixel_height / 2) - (self.camera.height / 2)

        # Менеджер сущностей
        self.entities = []

        # Спавним первого жителя (Мэра) прямо в центре Мэрии
        mayor_x = world_pixel_width / 2
        mayor_y = world_pixel_height / 2
        mayor = Citizen(mayor_x, mayor_y, self.game.language)
        self.entities.append(mayor)

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

        # Обновляем все сущности
        for entity in self.entities:
            entity.update(dt)

    def render(self, surface):
        # Заливаем фон базовым цветом (например, цвет пустоты вокруг карты)
        surface.fill((30, 30, 30))

        # Отрисовываем мир с учетом позиции и зума камеры
        self.world.render(surface, self.camera)

        # Отрисовываем сущности
        for entity in self.entities:
            entity.render(surface, self.camera)

        # Отрисовываем отладочную информацию (Координаты камеры и зум)
        debug_text = f"Cam: ({int(self.camera.x)}, {int(self.camera.y)}) | Zoom: {self.camera.zoom:.2f}"
        try:
            debug_surf = self.game.menu_font.render(debug_text, True, (255, 255, 255))
            surface.blit(debug_surf, (10, 10))
        except:
            pass # Если шрифт вдруг не прогрузился
