import pygame
import sys

# Настройки экрана и игры
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

def main():
    # Инициализация Pygame
    pygame.init()

    # Настройка экрана
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Симуляция Города (AI Game)")

    # Часы для управления FPS и вычисления delta time
    clock = pygame.time.Clock()

    running = True

    # Игровой цикл
    while running:
        # 1. Вычисление delta time (в секундах)
        dt = clock.tick(FPS) / 1000.0

        # 2. Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # 3. Обновление логики (update)
        # Здесь будет логика ECS, систем, камеры и т.д.

        # 4. Отрисовка (render)
        # Очистка экрана черным цветом
        screen.fill((0, 0, 0))

        # Здесь будет отрисовка карты, сущностей, интерфейса

        # Обновление экрана
        pygame.display.flip()

    # Корректный выход
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
