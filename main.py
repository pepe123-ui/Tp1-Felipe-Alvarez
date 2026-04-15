import pygame
import sys

from scripts import (
    draw_mapa, draw_borde, draw_minimapa, draw_hud, draw_lose, agregar_comida,
    Camara, Snake, Food,
    Negro, Blanco, Ancho, Alto, Comida_minimo,
    Verde, Verde_Oscuro, Rojo, Amarillo,
    BG_COLOR,
)

SCREEN_W = 1280
SCREEN_H = 720
FPS      = 60


def make_player():
    return Snake(
        x          = Ancho // 2,
        y          = Alto  // 2,
        color      = Verde,
        head_color = Verde_Oscuro,
    )


def main():
    pygame.init()
    pygame.display.set_caption("Snake  •  move with mouse  •  hold SPACE to boost")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    camara    = Camara(SCREEN_W, SCREEN_H)
    player    = make_player()
    food_list = []
    agregar_comida(food_list)

    game_over = False
    running   = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and game_over:
                    player    = make_player()
                    food_list = []
                    agregar_comida(food_list)
                    game_over = False

        if not game_over:
            keys = pygame.key.get_pressed()
            player.boost = keys[pygame.K_SPACE]

            mx, my = pygame.mouse.get_pos()
            player.direccion(mx, my, camara)
            player.mover()
            player.colision_pared()
            player.comer(food_list)
            agregar_comida(food_list)

            for food in food_list:
                food.update()

            camara.seguir(int(player.head[0]), int(player.head[1]))

            if not player.alive:
                game_over = True

        draw_mapa(screen, camara)

        for food in food_list:
            food.draw(screen, camara)

        if not game_over:
            player.draw(screen, camara)

        draw_borde(camara, screen)
        draw_hud(screen, player, camara)
        draw_minimapa(screen, player, camara)

        if game_over:
            draw_lose(player, screen, camara)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()