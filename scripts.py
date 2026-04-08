import os
import random
import pygame
import math

#Pool de Colores
Negro = (0,   0,   0  )
Blanco= (255, 255, 255)
Verde= (50,  200, 50 )
Verde_Oscuro= (30,  140, 30 )
Rojo= (220, 60,  60 )
Amarillo= (255, 220, 0  )
Gris= (40,  40,  40 )
Gris_Claro= (80,  80,  80 )

#Mapa
Ancho= 3000
Alto= 3000
Bloque= 20
Comida_minimo= 80

# Colores para mapa y serpiente
BG_COLOR     = (15, 15, 15)
GRID_COLOR   = (35, 35, 35)
HIGHLIGHT    = (50, 50, 50)
BORDER_COLOR = (80, 80, 80)

HEX_SIZE = 40
HEX_WIDTH = HEX_SIZE * 2
HEX_HEIGHT = int(HEX_SIZE * 1.732)
HEX_H_SPACING = int(HEX_WIDTH * 0.75)
HEX_V_SPACING = HEX_HEIGHT

BACKGROUND_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'mapa1.png')
_background_cache = {}

SNAKE_COLORS = [Verde, Verde_Oscuro, Rojo, Amarillo, Gris, Gris_Claro]
SNAKE_BASE_COLOR = random.choice(SNAKE_COLORS)
SNAKE_BORDER_COLOR = (max(0, SNAKE_BASE_COLOR[0] - 90), max(0, SNAKE_BASE_COLOR[1] - 90), max(0, SNAKE_BASE_COLOR[2] - 90))

snake_segments = []
base_x = 1280 // 2 + 140
base_y = 720 // 2
segment_radius = 18
segment_spacing = segment_radius * 0.55
for i in range(12):
    x = base_x - i * segment_spacing
    y = base_y
    snake_segments.append((int(x), int(y)))


class camara:
    def __init__(self):
        pass
    def seguir():
        pass
    def aplicar():
        pass

class Food:
    #Pool de Colores
    Negro = (0,   0,   0  )
    Blanco= (255, 255, 255)
    Verde= (50,  200, 50 )
    Verde_Oscuro= (30,  140, 30 )
    Rojo= (220, 60,  60 )
    Amarillo= (255, 220, 0  )
    Gris= (40,  40,  40 )
    Gris_Claro= (80,  80,  80 )

    def __init__(self):
        pass

    def draw(self):
        pass

class snake:
    largo_inicial= 10
    velocidad= 3.5
    velocidad_con_boost= 6.5

    def __init__(self, x, y, color=(50, 200, 50), head_color=(30, 140, 30)):
        self.color      = color
        self.head_color = head_color
        self.alive      = True
        self.score      = 0
        self.boost      = False
        self.angle      = 0.0   
        self.segments = [
            (float(x - i * Bloque), float(y))
            for i in range(self.largo_inicial)
        ]

    @property
    def head(self):
        return self.segments[0]
 
    @property
    def radius(self):
        return 8 + min(len(self.segments) // 20, 6)
    
    def direccion():
        pass
    def mover(self):
        pass
    def crecer():
        pass
    def colision_pared():
        pass
    def comer():
        pass
    def draw(self):
        pass
def _get_background_image():
    if 'original' not in _background_cache:
        image = pygame.image.load(BACKGROUND_IMAGE_PATH).convert()
        _background_cache['original'] = image
    return _background_cache['original']


def draw_mapa(surface):
    width, height = surface.get_size()
    image = _get_background_image()
    small_w = int(width * 0.4)
    small_h = int(height * 0.4)
    small_bg = pygame.transform.smoothscale(image, (small_w, small_h))

    surface.fill((8, 8, 10))
    for x in range(0, width, small_w):
        for y in range(0, height, small_h):
            surface.blit(small_bg, (x, y))


def draw_snake(surface):
    radius = 18
    for pos in snake_segments:
        pygame.draw.circle(surface, SNAKE_BORDER_COLOR, pos, radius + 1)
        pygame.draw.circle(surface, SNAKE_BASE_COLOR, pos, radius)

    head_pos = snake_segments[0]
    pygame.draw.circle(surface, SNAKE_BORDER_COLOR, head_pos, radius + 1)
    pygame.draw.circle(surface, SNAKE_BASE_COLOR, head_pos, radius)

    eye_y = head_pos[1] - 4
    eye_offset = 10
    pygame.draw.circle(surface, (255, 255, 255), (head_pos[0] - eye_offset, eye_y), 9)
    pygame.draw.circle(surface, (255, 255, 255), (head_pos[0] + eye_offset, eye_y), 9)
    pygame.draw.circle(surface, (20, 20, 20), (head_pos[0] - eye_offset, eye_y), 5)
    pygame.draw.circle(surface, (20, 20, 20), (head_pos[0] + eye_offset, eye_y), 5)
    pygame.draw.circle(surface, (255, 255, 255), (head_pos[0] - eye_offset + 2, eye_y - 2), 2)
    pygame.draw.circle(surface, (255, 255, 255), (head_pos[0] + eye_offset + 2, eye_y - 2), 2)


def draw_borde(camara,superfice):
    pass
def draw_minimapa(superficie,snake,camara):
    pass
def draw_hud(superficie,snake,camara):
    pass
def draw_lose(snake,superfice,camara):
    pass
def agregar_comida(superficie):
    pass