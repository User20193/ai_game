import pygame

class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.speed = 300  # Пикселей в секунду

        # Настройки зума
        self.zoom = 1.0
        self.zoom_speed = 0.5
        self.min_zoom = 0.5
        self.max_zoom = 5.0

    def update_screen_size(self, width, height):
        self.width = width
        self.height = height

    def update(self, dt, keys, events):
        # Обработка перемещения (WASD)
        # Приближенная камера движется медленнее относительно экрана,
        # поэтому делим скорость на зум для равномерного ощущения движения
        current_speed = self.speed * dt / self.zoom

        if keys[pygame.K_w]:
            self.y -= current_speed
        if keys[pygame.K_s]:
            self.y += current_speed
        if keys[pygame.K_a]:
            self.x -= current_speed
        if keys[pygame.K_d]:
            self.x += current_speed

        # Обработка зума (Q и E)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.zoom -= self.zoom_speed
                elif event.key == pygame.K_e:
                    self.zoom += self.zoom_speed

        # Ограничение зума
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

    def apply(self, entity_rect):
        """
        Преобразует координаты объекта в мире в координаты на экране,
        учитывая смещение камеры и зум.
        """
        # Сдвиг относительно камеры
        shifted_x = entity_rect.x - self.x
        shifted_y = entity_rect.y - self.y

        # Применяем зум, масштабируя относительно центра экрана
        # 1. Центрируем координаты
        center_x = self.width / 2
        center_y = self.height / 2

        dist_x = shifted_x - center_x
        dist_y = shifted_y - center_y

        # 2. Умножаем на зум
        zoomed_x = (dist_x * self.zoom) + center_x
        zoomed_y = (dist_y * self.zoom) + center_y

        # Масштабируем размер
        zoomed_w = entity_rect.width * self.zoom
        zoomed_h = entity_rect.height * self.zoom

        return pygame.Rect(zoomed_x, zoomed_y, zoomed_w, zoomed_h)

    def screen_to_world(self, screen_x, screen_y):
        """
        Переводит координаты курсора на экране в координаты игрового мира,
        выполняя обратные преобразования зума и сдвига камеры.
        """
        center_x = self.width / 2
        center_y = self.height / 2

        # 1. Отменяем зум
        dist_x = (screen_x - center_x) / self.zoom
        dist_y = (screen_y - center_y) / self.zoom

        # 2. Отменяем сдвиг камеры
        world_x = dist_x + center_x + self.x
        world_y = dist_y + center_y + self.y

        return world_x, world_y
