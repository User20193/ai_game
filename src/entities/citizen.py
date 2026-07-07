import pygame
import random
import math
import os
from .entity import Entity

class Citizen(Entity):
    def __init__(self, x, y, language_system, world):
        # Размеры жителя (8 ширина, 18 высота)
        super().__init__(x, y, 8, 18)

        self.language = language_system
        self.world = world

        # Процедурная генерация внешности
        self.skin_color = (255, 224, 189) # Телесный
        # Случайный цвет рубашки (не слишком темный)
        self.shirt_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.pants_color = (40, 40, 60) # Темно-синие джинсы/брюки

        # FSM (Конечный автомат)
        self.state = "IDLE"
        self.state_timer = 0
        self.target_x = self.x
        self.target_y = self.y
        self.speed = 15 # Пикселей в секунду

        # Облачко мыслей
        self.thought = ""
        self.thought_timer = 0
        font_path = os.path.join("assets", "fonts", "pixel_font.ttf")
        try:
            self.font = pygame.font.Font(font_path, 12)
        except:
            self.font = pygame.font.Font(None, 16)

        # Сразу сгенерируем мысль при появлении
        self.generate_thought()

    def generate_thought(self):
        """Создает новую мысль и запускает таймер ее отображения."""
        if self.language:
            self.thought = self.language.generate_thought()
            self.thought_timer = random.uniform(7.0, 10.0) # Мысль висит от 7 до 10 секунд

    def update(self, dt):
        # Обновление таймера мысли
        if self.thought_timer > 0:
            self.thought_timer -= dt
            if self.thought_timer <= 0:
                self.thought = ""
                # Следующая мысль появится через случайное время
                self.thought_timer = -random.uniform(5.0, 15.0)
        elif self.thought_timer < 0:
            self.thought_timer += dt
            if self.thought_timer >= 0:
                self.generate_thought()

        # FSM Логика
        if self.state == "IDLE":
            self.state_timer -= dt
            if self.state_timer <= 0:
                # Переход в состояние блуждания
                self.state = "WANDER"
                # Выбираем случайную точку в радиусе 50 пикселей
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(10, 50)
                self.target_x = self.x + math.cos(angle) * distance
                self.target_y = self.y + math.sin(angle) * distance

                # Ограничение по границам карты (20 чанков * 16 тайлов * 8 пикселей = 2560)
                # Поскольку Citizen не знает напрямую о World, хардкодим/передаем пределы,
                # либо берем их с запасом, чтобы не уйти в пустошь (на будущее лучше прокидывать world reference).
                max_world_x = 20 * 16 * 8
                max_world_y = 20 * 16 * 8

                self.target_x = max(0, min(self.target_x, max_world_x - self.width))
                self.target_y = max(0, min(self.target_y, max_world_y - self.height))

        elif self.state == "WANDER":
            # Вычисляем вектор к цели
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.hypot(dx, dy)

            if dist < 1.0: # Достигли цели
                self.state = "IDLE"
                self.state_timer = random.uniform(1.0, 4.0) # Стоим от 1 до 4 секунд
            else:
                # Двигаемся к цели
                step_x = (dx / dist) * self.speed * dt
                step_y = (dy / dist) * self.speed * dt

                future_x = self.x + step_x
                future_y = self.y + step_y

                # Проверка коллизий по центру низа ног (самая "твердая" часть жителя)
                check_x = future_x + self.width / 2
                check_y = future_y + self.height

                tile_idx = self.world.get_tile_index(check_x, check_y)
                tile = self.world.tile_registry.get_tile(tile_idx)

                # Если тайл непроходимый (is_solid), прерываем движение
                if tile.is_solid:
                    self.state = "IDLE"
                    self.state_timer = random.uniform(1.0, 2.0)
                    self.target_x = self.x
                    self.target_y = self.y
                else:
                    self.x = future_x
                    self.y = future_y

    def render(self, surface, camera):
        # Получаем координаты на экране с учетом зума
        screen_rect = camera.apply(self.get_rect())

        # Чтобы не было дрожания из-за float, округляем до целых
        sx = int(screen_rect.x)
        sy = int(screen_rect.y)

        # Пропорции для частей тела (при масштабировании)
        # Оригинал: Голова 6, Тело 7, Ноги 5. Общая высота 18.
        # Масштаб по высоте
        head_h = int((6 / 18) * screen_rect.height)
        body_h = int((7 / 18) * screen_rect.height)
        legs_h = screen_rect.height - head_h - body_h

        # Масштаб по ширине (Голова уже туловища на 2 пикселя)
        body_w = int(screen_rect.width)
        head_w = int((6 / 8) * screen_rect.width)
        head_offset_x = (body_w - head_w) // 2

        # Рисуем ноги
        pygame.draw.rect(surface, self.pants_color, (sx, sy + head_h + body_h, body_w, legs_h))
        # Рисуем тело
        pygame.draw.rect(surface, self.shirt_color, (sx, sy + head_h, body_w, body_h))
        # Рисуем голову
        pygame.draw.rect(surface, self.skin_color, (sx + head_offset_x, sy, head_w, head_h))

        # Рисуем мысль, если она есть
        if self.thought_timer > 0 and self.thought:
            text_surf = self.font.render(self.thought, True, (0, 0, 0))
            text_rect = text_surf.get_rect()

            # Подложка (пузырь)
            padding = 4
            bubble_rect = pygame.Rect(
                0, 0,
                text_rect.width + padding * 2,
                text_rect.height + padding * 2
            )
            # Размещаем над головой
            bubble_rect.midbottom = (sx + body_w // 2, sy - 5)

            # Рисуем пузырь (белый с черной рамкой)
            pygame.draw.rect(surface, (255, 255, 255), bubble_rect, border_radius=4)
            pygame.draw.rect(surface, (0, 0, 0), bubble_rect, width=1, border_radius=4)

            # Рисуем текст
            text_rect.center = bubble_rect.center
            surface.blit(text_surf, text_rect)
