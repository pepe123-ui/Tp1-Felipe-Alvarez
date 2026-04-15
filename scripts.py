import os
import random
import pygame
import math

# ─── Pool de Colores ───────────────────────────────────────────────────────────
Negro        = (0,   0,   0  )
Blanco       = (255, 255, 255)
Verde        = (50,  200, 50 )
Verde_Oscuro = (30,  140, 30 )
Rojo         = (220, 60,  60 )
Amarillo     = (255, 220, 0  )
Gris         = (40,  40,  40 )
Gris_Claro   = (80,  80,  80 )

# ─── Mapa ──────────────────────────────────────────────────────────────────────
Ancho         = 3000
Alto          = 3000
Bloque        = 20
Comida_minimo = 80

# ─── Colores UI ────────────────────────────────────────────────────────────────
BG_COLOR     = (15, 15, 15)
GRID_COLOR   = (35, 35, 35)
HIGHLIGHT    = (50, 50, 50)
BORDER_COLOR = (80, 80, 80)

# ─── Hexágonos ─────────────────────────────────────────────────────────────────
HEX_SIZE      = 40
HEX_WIDTH     = HEX_SIZE * 2
HEX_HEIGHT    = int(HEX_SIZE * 1.732)
HEX_H_SPACING = int(HEX_WIDTH * 0.75)
HEX_V_SPACING = HEX_HEIGHT

# ─── Colores serpiente legacy ──────────────────────────────────────────────────
SNAKE_COLORS       = [Verde, Verde_Oscuro, Rojo, Amarillo, Gris, Gris_Claro]
SNAKE_BASE_COLOR   = random.choice(SNAKE_COLORS)
SNAKE_BORDER_COLOR = (
    max(0, SNAKE_BASE_COLOR[0] - 90),
    max(0, SNAKE_BASE_COLOR[1] - 90),
    max(0, SNAKE_BASE_COLOR[2] - 90),
)

snake_segments = []
base_x = 1280 // 2 + 140
base_y = 720  // 2
segment_radius  = 18
segment_spacing = segment_radius * 0.55
for i in range(12):
    snake_segments.append((int(base_x - i * segment_spacing), base_y))


# ══════════════════════════════════════════════════════════════════════════════
#  CÁMARA
# ══════════════════════════════════════════════════════════════════════════════
class Camara:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.x = 0.0
        self.y = 0.0

    def seguir(self, target_x, target_y):
        self.x = target_x - self.screen_w / 2
        self.y = target_y - self.screen_h / 2
        self.x = max(0, min(self.x, Ancho - self.screen_w))
        self.y = max(0, min(self.y, Alto  - self.screen_h))

    def aplicar(self, world_x, world_y):
        return world_x - self.x, world_y - self.y


# ══════════════════════════════════════════════════════════════════════════════
#  MAPA HEXAGONAL — tile tileable, sin stutter
# ══════════════════════════════════════════════════════════════════════════════
_hex_tile = None
_TILE_W   = 0
_TILE_H   = 0

_HEX_R    = 42
_HEX_GAP  = 3
_C_BG     = (10, 12, 16)
_C_FILL   = (22, 26, 32)
_C_INNER  = (16, 19, 24)
_C_BORDER = (44, 52, 62)


def _hex_pts(cx, cy, r):
    return [
        (cx + r * math.cos(math.radians(60 * i)),
         cy + r * math.sin(math.radians(60 * i)))
        for i in range(6)
    ]


def _build_hex_tile():
    """
    Construye un Surface que puede repetirse sin costuras.
    Usamos hexágonos pointy-top. El período exacto del patrón es:
        col_w  = sqrt(3) * r   (paso horizontal entre centros de la misma fila)
        row_h  = 1.5 * r       (paso vertical entre filas con offset)
    El tile contiene TILE_COLS × TILE_ROWS períodos enteros del patrón
    para que borde izquierdo == borde derecho y borde superior == borde inferior.
    """
    global _hex_tile, _TILE_W, _TILE_H

    r      = _HEX_R
    col_w  = math.sqrt(3) * r
    row_h  = 1.5 * r

    COLS = 5
    ROWS = 4
    tw   = int(col_w * COLS)
    th   = int(row_h * ROWS + r)   # +r para la mitad inferior del offset

    surf = pygame.Surface((tw, th))
    surf.fill(_C_BG)

    # dibujamos con margen para que los bordes queden bien
    margin_c = 2
    margin_r = 2
    for col in range(-margin_c, COLS + margin_c):
        for row in range(-margin_r, ROWS + margin_r):
            cx = col * col_w + (col_w / 2 if row % 2 else 0)
            cy = row * row_h + r
            if -r * 2 <= cx <= tw + r * 2 and -r * 2 <= cy <= th + r * 2:
                outer = _hex_pts(cx, cy, r - _HEX_GAP)
                inner = _hex_pts(cx, cy, r - _HEX_GAP - 9)
                pygame.draw.polygon(surf, _C_FILL,  outer)
                pygame.draw.polygon(surf, _C_BORDER, outer, 2)
                pygame.draw.polygon(surf, _C_INNER,  inner)

    _hex_tile = surf
    _TILE_W   = tw
    _TILE_H   = th


def draw_mapa(surface, camara=None):
    global _hex_tile, _TILE_W, _TILE_H
    if _hex_tile is None:
        _build_hex_tile()

    sw, sh = surface.get_size()
    ox = (camara.x % _TILE_W) if camara else 0
    oy = (camara.y % _TILE_H) if camara else 0

    # blit en grid, desplazado por el offset fraccionario de la cámara
    y = -int(oy)
    while y < sh:
        x = -int(ox)
        while x < sw:
            surface.blit(_hex_tile, (x, y))
            x += _TILE_W
        y += _TILE_H


# ══════════════════════════════════════════════════════════════════════════════
#  COMIDA
# ══════════════════════════════════════════════════════════════════════════════
FOOD_COLORS = [
    (255, 80,  80 ),
    (255, 200, 50 ),
    (80,  220, 80 ),
    (80,  180, 255),
    (255, 120, 200),
    (200, 100, 255),
]


class Food:
    def __init__(self):
        margin     = 100
        self.x     = random.randint(margin, Ancho - margin)
        self.y     = random.randint(margin, Alto  - margin)
        self.color = random.choice(FOOD_COLORS)
        self.radius = random.randint(6, 11)
        self.value  = max(1, self.radius - 4)
        self.pulse  = random.uniform(0, math.pi * 2)

    def update(self):
        self.pulse += 0.08

    def draw(self, surface, camara):
        sx, sy = camara.aplicar(self.x, self.y)
        sw, sh = surface.get_size()
        if -30 < sx < sw + 30 and -30 < sy < sh + 30:
            r = self.radius + int(math.sin(self.pulse) * 2)
            halo = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(halo, (*self.color, 55), (r * 2, r * 2), r * 2)
            surface.blit(halo, (int(sx) - r * 2, int(sy) - r * 2))
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), r)
            pygame.draw.circle(surface, Blanco,
                               (int(sx) - max(1, r // 3), int(sy) - max(1, r // 3)),
                               max(2, r // 3))


def agregar_comida(lista_comida):
    while len(lista_comida) < Comida_minimo:
        lista_comida.append(Food())


# ══════════════════════════════════════════════════════════════════════════════
#  SERPIENTE — estilo slither.io
# ══════════════════════════════════════════════════════════════════════════════

def _lerp_color(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def _darker(c, amount=60):
    return (max(0, c[0] - amount), max(0, c[1] - amount), max(0, c[2] - amount))


class Snake:
    largo_inicial   = 10
    velocidad       = 2.5
    velocidad_boost = 5.0
    # Distancia entre puntos internos: más pequeño = curvas más suaves
    SPACING         = 3.0

    def __init__(self, x, y, color=Verde, head_color=Verde_Oscuro):
        self.color      = color
        self.head_color = head_color
        self.alive      = True
        self.score      = 0
        self.boost      = False
        self.angle      = 0.0

        pts_iniciales = self.largo_inicial * int(Bloque / self.SPACING)
        self.segments = [
            [float(x - i * self.SPACING), float(y)]
            for i in range(pts_iniciales)
        ]
        self._grow_queue  = 0
        self._radii       = []
        self._rebuild_radii()

    # ── propiedades ──────────────────────────────────────────────────────────
    @property
    def head(self):
        return self.segments[0]

    @property
    def radius(self):
        n = len(self.segments)
        return 10 + min(n // 80, 7)

    # ── interno ───────────────────────────────────────────────────────────────
    def _rebuild_radii(self):
        n      = len(self.segments)
        r_head = self.radius
        r_tail = max(3, r_head - 6)
        self._radii = [
            r_head - (r_head - r_tail) * (i / max(1, n - 1))
            for i in range(n)
        ]

    # ── lógica ───────────────────────────────────────────────────────────────
    def direccion(self, mx, my, camara):
        hx, hy = camara.aplicar(self.head[0], self.head[1])
        dx, dy = mx - hx, my - hy
        if abs(dx) > 1 or abs(dy) > 1:
            target = math.atan2(dy, dx)
            # Interpolación angular suave (sin saltos al cruzar ±π)
            diff   = (target - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += diff * 0.18

    def mover(self):
        speed = self.velocidad_boost if self.boost else self.velocidad
        self.segments.insert(0, [
            self.head[0] + math.cos(self.angle) * speed,
            self.head[1] + math.sin(self.angle) * speed,
        ])
        if self._grow_queue > 0:
            self._grow_queue -= 1
        else:
            self.segments.pop()
        if len(self._radii) != len(self.segments):
            self._rebuild_radii()

    def crecer(self, amount=5):
        self._grow_queue += amount * int(Bloque / self.SPACING)
        self._rebuild_radii()

    def colision_pared(self):
        hx, hy = self.head
        if hx < 0 or hx > Ancho or hy < 0 or hy > Alto:
            self.alive = False

    def comer(self, lista_comida):
        hx, hy = self.head
        r      = self.radius + 10
        eaten  = [f for f in lista_comida if math.hypot(f.x - hx, f.y - hy) < r + f.radius]
        for f in eaten:
            self.score += f.value
            self.crecer(f.value * 3)
            lista_comida.remove(f)
        return bool(eaten)

    # ── dibujo ───────────────────────────────────────────────────────────────
    def draw(self, surface, camara):
        sw, sh  = surface.get_size()
        n       = len(self.segments)
        radii   = self._radii if len(self._radii) == n else [self.radius] * n

        body_c  = self.color
        tail_c  = _darker(self.color, 35)
        bord_c  = _darker(self.color, 80)

        # ── Cuerpo (de cola a cuello, saltando segmentos para rendimiento) ──
        step = max(1, n // 400)
        for i in range(n - 1, 0, -step):
            seg    = self.segments[i]
            sx, sy = camara.aplicar(seg[0], seg[1])
            if -40 < sx < sw + 40 and -40 < sy < sh + 40:
                r   = max(2, int(radii[i]))
                t   = i / max(1, n - 1)
                col = _lerp_color(body_c, tail_c, t)
                bor = _lerp_color(bord_c, _darker(tail_c, 20), t)
                pygame.draw.circle(surface, bor, (int(sx), int(sy)), r + 1)
                pygame.draw.circle(surface, col, (int(sx), int(sy)), r)

        # ── Cabeza ────────────────────────────────────────────────────────
        hx, hy = camara.aplicar(self.head[0], self.head[1])
        hr     = int(radii[0]) + 2

        # Sombra debajo de la cabeza
        shadow = pygame.Surface((hr * 4, hr * 4), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 55), (hr * 2 + 4, hr * 2 + 4), hr + 1)
        surface.blit(shadow, (int(hx) - hr * 2, int(hy) - hr * 2))

        pygame.draw.circle(surface, bord_c,          (int(hx), int(hy)), hr + 2)
        pygame.draw.circle(surface, self.head_color, (int(hx), int(hy)), hr)

        # Brillo tipo gloss
        gloss = pygame.Surface((hr * 2, hr * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(gloss, (255, 255, 255, 45),
                            (hr // 2, hr // 5, hr, hr // 2))
        surface.blit(gloss, (int(hx) - hr, int(hy) - hr))
        perp     = self.angle + math.pi / 2
        eye_dist = hr * 0.52
        fwd      = hr * 0.22

        for side in (-1, 1):
            ex = hx + math.cos(self.angle) * fwd + math.cos(perp) * eye_dist * side
            ey = hy + math.sin(self.angle) * fwd + math.sin(perp) * eye_dist * side
            er = max(4, hr // 2)

            pygame.draw.circle(surface, Blanco,       (int(ex), int(ey)), er)
            px = int(ex + math.cos(self.angle) * (er * 0.28))
            py = int(ey + math.sin(self.angle) * (er * 0.28))
            pygame.draw.circle(surface, (20, 20, 20), (px, py), max(2, er // 2))
            pygame.draw.circle(surface, Blanco,
                               (px + max(1, er // 4), py - max(1, er // 4)),
                               max(1, er // 4))


def draw_borde(camara, superficie):
    corners = [
        camara.aplicar(0,     0    ),
        camara.aplicar(Ancho, 0    ),
        camara.aplicar(Ancho, Alto ),
        camara.aplicar(0,     Alto ),
    ]
    pygame.draw.lines(superficie, (255, 80, 80), True, corners, 3)


def draw_minimapa(superficie, snake, camara):
    mm_w, mm_h = 160, 160
    mm_x = superficie.get_width() - mm_w - 10
    mm_y = 10
    sx_  = mm_w / Ancho
    sy_  = mm_h / Alto

    mm = pygame.Surface((mm_w, mm_h), pygame.SRCALPHA)
    mm.fill((0, 0, 0, 140))
    pygame.draw.rect(mm, (100, 100, 100), (0, 0, mm_w, mm_h), 1)

    pygame.draw.circle(mm, Verde,
                       (int(snake.head[0] * sx_), int(snake.head[1] * sy_)), 4)
    pygame.draw.rect(mm, (200, 200, 200),
                     (int(camara.x * sx_), int(camara.y * sy_),
                      int(superficie.get_width() * sx_),
                      int(superficie.get_height() * sy_)), 1)
    superficie.blit(mm, (mm_x, mm_y))


def draw_hud(superficie, snake, camara=None):
    font_big   = pygame.font.SysFont("consolas", 28, bold=True)
    font_small = pygame.font.SysFont("consolas", 18)
    superficie.blit(font_big.render(f"Score: {snake.score}", True, Amarillo),   (12, 12))
    superficie.blit(font_small.render(f"Length: {len(snake.segments)}", True, Blanco), (12, 46))
    if snake.boost:
        superficie.blit(font_small.render("BOOST", True, (255, 160, 0)), (12, 68))


def draw_lose(snake, superficie, camara=None):
    overlay = pygame.Surface(superficie.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    superficie.blit(overlay, (0, 0))

    font_big   = pygame.font.SysFont("consolas", 64, bold=True)
    font_small = pygame.font.SysFont("consolas", 30)
    sw, sh     = superficie.get_size()

    for surf, y in [
        (font_big.render("GAME OVER", True, Rojo),                                       sh // 2 - 80),
        (font_small.render(f"Score: {snake.score}  Length: {len(snake.segments)}", True, Blanco), sh // 2 + 10),
        (font_small.render("Press R to restart", True, Gris_Claro),                      sh // 2 + 55),
    ]:
        superficie.blit(surf, (sw // 2 - surf.get_width() // 2, y))


def draw_snake(surface, camara=None):
    radius = 18
    border = SNAKE_BORDER_COLOR
    for pos in snake_segments:
        pygame.draw.circle(surface, border, pos, radius + 1)
        pygame.draw.circle(surface, SNAKE_BASE_COLOR, pos, radius)
    head_pos = snake_segments[0]
    pygame.draw.circle(surface, border, head_pos, radius + 1)
    pygame.draw.circle(surface, SNAKE_BASE_COLOR, head_pos, radius)
    eye_y, eye_offset = head_pos[1] - 4, 10
    for side in (-1, 1):
        ex = head_pos[0] + side * eye_offset
        pygame.draw.circle(surface, Blanco, (ex, eye_y), 9)
        pygame.draw.circle(surface, (20, 20, 20), (ex, eye_y), 5)
        pygame.draw.circle(surface, Blanco, (ex + 2, eye_y - 2), 2)