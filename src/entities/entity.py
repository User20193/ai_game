import pygame

class Entity:
    """Базовый класс для всех объектов в мире (сущностей)."""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_rect(self):
        """Возвращает Pygame Rect для этой сущности в мировых координатах."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt):
        """Обновление логики сущности. Переопределяется в наследниках."""
        pass

    def render(self, surface, camera):
        """
        Отрисовка сущности.
        Должна использовать camera.apply(self.get_rect()) для правильного позиционирования на экране.
        """
        pass
