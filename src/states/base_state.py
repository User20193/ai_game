import pygame

class State:
    """Базовый класс для всех игровых состояний (экранов)."""
    def __init__(self, game):
        self.game = game
        self.prev_state = None

    def update(self, dt, events):
        """Обновление логики состояния."""
        pass

    def render(self, surface):
        """Отрисовка состояния."""
        pass

    def enter_state(self):
        """Вызывается при переходе в это состояние. Сохраняем предыдущее состояние в стек."""
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    def exit_state(self):
        """Вызывается при выходе из состояния. Убираем себя из стека."""
        self.game.state_stack.pop()
