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

        # Управление слоями (Z-Index)
        self.show_roofs = True

        # Менеджер сущностей
        self.entities = []

        # Спавним первого жителя (Мэра) прямо в центре Мэрии
        mayor_x = world_pixel_width / 2
        mayor_y = world_pixel_height / 2
        mayor = Citizen(mayor_x, mayor_y, self.game.language, self.world)
        self.entities.append(mayor)

        # Система времени
        self.game_time = 12.0 # Начинаем в полдень (12:00)
        self.time_speed = 1.0 # 1 игровой час проходит за 1 реальную минуту (1 / 60 часов в секунду)

    def update(self, dt, events):
        # Обновление времени
        self.game_time += dt * (self.time_speed / 60.0)
        if self.game_time >= 24.0:
            self.game_time -= 24.0

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # По нажатию ESC возвращаемся в предыдущее состояние (меню)
                    self.exit_state()
                elif event.key == pygame.K_r:
                    # Переключение видимости крыш
                    self.show_roofs = not self.show_roofs

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

        # 1. Отрисовываем землю (пол, трава, вода)
        self.world.render_ground(surface, self.camera)

        # 2. Отрисовываем сущности
        for entity in self.entities:
            entity.render(surface, self.camera)

        # 3. Отрисовываем крыши (если включены)
        if self.show_roofs:
            self.world.render_roof(surface, self.camera)

        # 4. Отрисовка ночного фильтра
        self.render_day_night_cycle(surface)

        # Отрисовываем отладочную информацию (Координаты камеры и зум)
        debug_text = f"Cam: ({int(self.camera.x)}, {int(self.camera.y)}) | Zoom: {self.camera.zoom:.2f}"
        try:
            debug_surf = self.game.menu_font.render(debug_text, True, (255, 255, 255))
            surface.blit(debug_surf, (10, 10))
        except:
            pass # Если шрифт вдруг не прогрузился

        # Отрисовка UI Времени
        self.render_ui(surface)

    def render_day_night_cycle(self, surface):
        """Отрисовывает полупрозрачный слой в зависимости от времени суток."""
        # Время от 0 до 24
        # Темнота: 0.0 (день) до 0.7 (ночь)
        alpha = 0

        if self.game_time < 5.0 or self.game_time > 20.0:
            alpha = 180 # Ночь
        elif 5.0 <= self.game_time < 8.0:
            # Рассвет (светлеет)
            progress = (self.game_time - 5.0) / 3.0
            alpha = int(180 * (1.0 - progress))
        elif 17.0 <= self.game_time <= 20.0:
            # Закат (темнеет)
            progress = (self.game_time - 17.0) / 3.0
            alpha = int(180 * progress)

        if alpha > 0:
            dark_surface = pygame.Surface((self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT), pygame.SRCALPHA)
            # Темно-синий ночной цвет
            dark_surface.fill((10, 10, 30, alpha))
            surface.blit(dark_surface, (0, 0))

    def render_ui(self, surface):
        """Отрисовывает интерфейс (время)."""
        hours = int(self.game_time)
        minutes = int((self.game_time - hours) * 60)
        time_str = f"{hours:02d}:{minutes:02d}"

        status = "День"
        if self.game_time < 6.0 or self.game_time > 20.0:
            status = "Ночь"
        elif 6.0 <= self.game_time < 9.0:
            status = "Утро"
        elif 18.0 <= self.game_time <= 20.0:
            status = "Вечер"

        text = f"{status} | {time_str}"
        try:
            # Тень
            shadow = self.game.menu_font.render(text, True, (0, 0, 0))
            surface.blit(shadow, (self.game.WINDOW_WIDTH - 250 + 2, 12))

            # Текст
            ui_surf = self.game.menu_font.render(text, True, (255, 255, 255))
            surface.blit(ui_surf, (self.game.WINDOW_WIDTH - 250, 10))
        except:
            pass
