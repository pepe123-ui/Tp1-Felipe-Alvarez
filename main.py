import pygame
import sys

from scripts import (
    draw_mapa, draw_snake,
    Negro, Blanco, Ancho, Alto, Comida_minimo,
    BG_COLOR, GRID_COLOR, HIGHLIGHT, BORDER_COLOR,
    HEX_SIZE, HEX_WIDTH, HEX_HEIGHT, HEX_H_SPACING, HEX_V_SPACING,
    SNAKE_BASE_COLOR, SNAKE_BORDER_COLOR,
    snake_segments,
)

SCREEN_W = 1280
SCREEN_H = 720
FPS      = 60


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw_mapa(screen)
        draw_snake(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()