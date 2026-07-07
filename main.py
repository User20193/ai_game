import os
import sys

# Добавляем корневую директорию в путь, чтобы импорты из src работали корректно
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.game import Game
from src.states.menu_state import MenuState

def main():
    # Создаем экземпляр игры
    game = Game()

    # Создаем и добавляем главное меню как первое состояние
    menu = MenuState(game)
    menu.enter_state()

    # Запускаем игровой цикл
    game.run()

if __name__ == "__main__":
    main()
