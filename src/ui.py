import pygame

class Button:
    def __init__(self, x, y, text, font, base_color, hover_color):
        self.x = x
        self.y = y
        self.text_str = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.is_hovered = False

        # Создаем текстовую поверхность один раз для оптимизации
        self.text_surf = self.font.render(self.text_str, True, self.base_color)
        self.rect = self.text_surf.get_rect(center=(self.x, self.y))

        # Размеры для рамки (подложки)
        self.padding = 10
        self.bg_rect = pygame.Rect(
            self.rect.left - self.padding,
            self.rect.top - self.padding,
            self.rect.width + self.padding * 2,
            self.rect.height + self.padding * 2
        )

    def update(self, mouse_pos):
        # Проверяем, наведен ли курсор на кнопку
        self.is_hovered = self.bg_rect.collidepoint(mouse_pos)

        # Обновляем цвет текста в зависимости от наведения
        current_color = self.hover_color if self.is_hovered else self.base_color
        self.text_surf = self.font.render(self.text_str, True, current_color)

    def draw(self, surface):
        # Рисуем подложку (рамку)
        border_color = self.hover_color if self.is_hovered else self.base_color
        pygame.draw.rect(surface, border_color, self.bg_rect, width=2, border_radius=5)

        # Рисуем сам текст
        surface.blit(self.text_surf, self.rect)

    def check_click(self, mouse_pos, event):
        """Возвращает True, если на кнопку кликнули."""
        if self.is_hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return True
        return False
