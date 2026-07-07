import pygame
import sys
import os

class Game:
    def __init__(self):
        pygame.init()
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Лисеу-Сити")

        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0

        # Стек состояний (например: Game -> PauseMenu). Текущее состояние - последнее в списке.
        self.state_stack = []

        # Загрузка глобальных ресурсов
        self.load_assets()

    def load_assets(self):
        # Базовый шрифт, если есть. Иначе - дефолтный.
        font_path = os.path.join("assets", "fonts", "pixel_font.ttf")
        try:
            self.title_font = pygame.font.Font(font_path, 48)
            self.menu_font = pygame.font.Font(font_path, 24)
        except:
            print("Warning: Couldn't load custom font, using default.")
            self.title_font = pygame.font.Font(None, 48)
            self.menu_font = pygame.font.Font(None, 24)

    def get_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        return events

    def update(self, events):
        # Обновляем только текущее (верхнее) состояние
        if self.state_stack:
            self.state_stack[-1].update(self.dt, events)

    def render(self):
        # Отрисовываем текущее (верхнее) состояние
        if self.state_stack:
            self.state_stack[-1].render(self.screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000.0
            events = self.get_events()
            self.update(events)
            self.render()

        pygame.quit()
        sys.exit()
