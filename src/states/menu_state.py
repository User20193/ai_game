import pygame
import random
from .base_state import State
from src.ui import Button

class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.mouse_pos = (0, 0)

        # Генерация "Procedural" фона (Звездное небо + силуэты зданий)
        self.bg_surface = pygame.Surface((self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT))
        self.generate_background()

        # Создание кнопок
        center_x = self.game.WINDOW_WIDTH // 2
        start_y = 300
        gap = 70
        base_color = (200, 200, 200) # Светло-серый
        hover_color = (255, 215, 0)  # Золотой

        self.buttons = {
            "new_game": Button(center_x, start_y, "Новая Игра", self.game.menu_font, base_color, hover_color),
            "settings": Button(center_x, start_y + gap, "Настройки", self.game.menu_font, base_color, hover_color),
            "credits": Button(center_x, start_y + gap * 2, "Авторы", self.game.menu_font, base_color, hover_color),
            "quit": Button(center_x, start_y + gap * 3, "Выйти", self.game.menu_font, base_color, hover_color)
        }

    def generate_background(self):
        # 1. Градиентное небо (от темно-синего к фиолетовому)
        for y in range(self.game.WINDOW_HEIGHT):
            r = int(10 + (30 * y / self.game.WINDOW_HEIGHT))
            g = int(10 + (20 * y / self.game.WINDOW_HEIGHT))
            b = int(40 + (50 * y / self.game.WINDOW_HEIGHT))
            pygame.draw.line(self.bg_surface, (r, g, b), (0, y), (self.game.WINDOW_WIDTH, y))

        # 2. Звезды
        for _ in range(150):
            x = random.randint(0, self.game.WINDOW_WIDTH)
            y = random.randint(0, self.game.WINDOW_HEIGHT // 2)
            alpha = random.randint(100, 255)
            # В Pygame не так просто нарисовать 1 пиксель с альфой, поэтому рисуем на временном Surface
            star = pygame.Surface((2, 2), pygame.SRCALPHA)
            star.fill((255, 255, 255, alpha))
            self.bg_surface.blit(star, (x, y))

        # 3. Силуэты зданий
        building_color = (15, 15, 25) # Почти черный
        x = 0
        while x < self.game.WINDOW_WIDTH:
            width = random.randint(40, 120)
            height = random.randint(100, 400)
            rect = pygame.Rect(x, self.game.WINDOW_HEIGHT - height, width, height)
            pygame.draw.rect(self.bg_surface, building_color, rect)

            # Окна в зданиях
            for win_x in range(x + 5, x + width - 10, 15):
                for win_y in range(self.game.WINDOW_HEIGHT - height + 10, self.game.WINDOW_HEIGHT - 10, 20):
                    if random.random() > 0.7: # 30% шанс, что окно горит
                        window_color = random.choice([(255, 255, 100), (200, 200, 255)])
                        pygame.draw.rect(self.bg_surface, window_color, (win_x, win_y, 8, 12))

            x += width + random.randint(2, 10)

    def update(self, dt, events):
        self.mouse_pos = pygame.mouse.get_pos()

        for btn in self.buttons.values():
            btn.update(self.mouse_pos)

        for event in events:
            # Проверка кнопок
            if self.buttons["quit"].check_click(self.mouse_pos, event):
                self.game.running = False
            elif self.buttons["new_game"].check_click(self.mouse_pos, event):
                print("Clicked: New Game (Not implemented yet)")
            elif self.buttons["settings"].check_click(self.mouse_pos, event):
                print("Clicked: Settings (Not implemented yet)")
            elif self.buttons["credits"].check_click(self.mouse_pos, event):
                print("Clicked: Credits (Not implemented yet)")

    def render(self, surface):
        # Отрисовка фона
        surface.blit(self.bg_surface, (0, 0))

        # Отрисовка заголовка с небольшой тенью для объема
        title_text = "Лисеу-Сити"

        # Тень
        title_shadow = self.game.title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = title_shadow.get_rect(center=(self.game.WINDOW_WIDTH // 2 + 4, 154))
        surface.blit(title_shadow, shadow_rect)

        # Основной текст
        title_surf = self.game.title_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.game.WINDOW_WIDTH // 2, 150))
        surface.blit(title_surf, title_rect)

        # Отрисовка кнопок
        for btn in self.buttons.values():
            btn.draw(surface)
