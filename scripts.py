import os
import random
import pygame
import math
import sys

Negro        = (0,   0,   0  )
Blanco       = (255, 255, 255)
Verde        = (50,  200, 50 )
Verde_Oscuro = (30,  140, 30 )
Rojo         = (220, 60,  60 )
Amarillo     = (255, 220, 0  )
Gris         = (40,  40,  40 )
Gris_Claro   = (80,  80,  80 )

Ancho         = 3000
Alto          = 3000
Bloque        = 20
Comida_minimo = 80

BG_COLOR     = (15, 15, 15)
GRID_COLOR   = (35, 35, 35)
HIGHLIGHT    = (50, 50, 50)
BORDER_COLOR = (80, 80, 80)

HEX_SIZE      = 40
HEX_WIDTH     = HEX_SIZE * 2
HEX_HEIGHT    = int(HEX_SIZE * 1.732)
HEX_H_SPACING = int(HEX_WIDTH * 0.75)
HEX_V_SPACING = HEX_HEIGHT

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


def make_player(skin_index):
    color, head_color, skin_name = SKINS[skin_index]
    return Snake(x=Ancho//2, y=Alto//2, color=color, head_color=head_color, skin_name=skin_name)


def reset_game(skin_index):
    player    = make_player(skin_index)
    bots      = crear_bots()
    food_list = []
    agregar_comida(food_list)
    return player, bots, food_list


def main():
    pygame.init()

    SCREEN_W, SCREEN_H = GAME_CONFIG['resolution']
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("slither.io")
    clock  = pygame.time.Clock()
    FPS = 60

    while True:
        menu_action = run_main_menu(screen)

        if menu_action == 'skins':
            run_skins_menu(screen)
            continue
        elif menu_action == 'options':
            new_res = GAME_CONFIG['resolution']
            if (screen.get_width(), screen.get_height()) != new_res:
                screen = pygame.display.set_mode(new_res)
                SCREEN_W, SCREEN_H = new_res
            run_options_menu(screen)
            continue
        elif menu_action != 'play':
            pygame.quit()
            sys.exit()

        new_res = GAME_CONFIG['resolution']
        if (screen.get_width(), screen.get_height()) != new_res:
            screen = pygame.display.set_mode(new_res)
            SCREEN_W, SCREEN_H = new_res

        result = run_game_setup(screen)
        if result is None:
            continue

        nickname, skin_index, mode = result
        pygame.display.set_caption(f"slither.io  •  {nickname}")

        camara = Camara(SCREEN_W, SCREEN_H)
        player, bots, food_list = reset_game(skin_index)
        game_over = False
        running   = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_r and game_over:
                        player, bots, food_list = reset_game(skin_index)
                        game_over = False

            if not game_over:
                keys = pygame.key.get_pressed()
                player.boost = keys[pygame.K_SPACE]

                if GAME_CONFIG['control_mode'] == 'mouse':
                    mx, my = pygame.mouse.get_pos()
                    player.direccion(mx, my, camara)
                else:
                    player.direccion_teclado(keys)

                player.mover()
                player.colision_pared()
                player.comer(food_list)

                if mode == 'ai':
                    actualizar_bots(bots, food_list)
                    check_collisions(player, bots)

                agregar_comida(food_list)
                for food in food_list:
                    food.update()

                camara.seguir(int(player.head[0]), int(player.head[1]))

                if not player.alive:
                    game_over = True

            draw_mapa(screen, camara)

            for food in food_list:
                food.draw(screen, camara)

            if mode == 'ai':
                dibujar_bots(screen, bots, camara)

            if not game_over:
                player.draw(screen, camara)

            draw_borde(camara, screen)
            draw_hud(screen, player, camara)

            if mode == 'ai':
                draw_leaderboard(screen, player, bots, nickname)

            draw_minimapa(screen, player, camara, bots if mode=='ai' else None)

            if game_over:
                draw_lose(player, screen, camara)

            pygame.display.flip()
            clock.tick(FPS)


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
    return [(cx + r*math.cos(math.radians(60*i)), cy + r*math.sin(math.radians(60*i))) for i in range(6)]


def _build_hex_tile():
    global _hex_tile, _TILE_W, _TILE_H
    r = _HEX_R
    col_w = math.sqrt(3) * r
    row_h = 1.5 * r
    COLS, ROWS = 5, 4
    tw = int(col_w * COLS)
    th = int(row_h * ROWS + r)
    surf = pygame.Surface((tw, th))
    surf.fill(_C_BG)
    for col in range(-2, COLS+2):
        for row in range(-2, ROWS+2):
            cx = col*col_w + (col_w/2 if row%2 else 0)
            cy = row*row_h + r
            if -r*2 <= cx <= tw+r*2 and -r*2 <= cy <= th+r*2:
                outer = _hex_pts(cx, cy, r-_HEX_GAP)
                inner = _hex_pts(cx, cy, r-_HEX_GAP-9)
                pygame.draw.polygon(surf, _C_FILL,   outer)
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
    y = -int(oy)
    while y < sh:
        x = -int(ox)
        while x < sw:
            surface.blit(_hex_tile, (x, y))
            x += _TILE_W
        y += _TILE_H


FOOD_COLORS = [
    (255,80,80),(255,200,50),(80,220,80),
    (80,180,255),(255,120,200),(200,100,255),
]


class Food:
    def __init__(self):
        margin = 100
        self.x      = random.randint(margin, Ancho-margin)
        self.y      = random.randint(margin, Alto -margin)
        self.color  = random.choice(FOOD_COLORS)
        self.radius = random.randint(6, 11)
        self.value  = max(1, self.radius-4)
        self.pulse  = random.uniform(0, math.pi*2)

    def update(self):
        self.pulse += 0.08

    def draw(self, surface, camara):
        sx, sy = camara.aplicar(self.x, self.y)
        sw, sh = surface.get_size()
        if -30 < sx < sw+30 and -30 < sy < sh+30:
            r = self.radius + int(math.sin(self.pulse)*2)
            halo = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
            pygame.draw.circle(halo, (*self.color, 55), (r*2, r*2), r*2)
            surface.blit(halo, (int(sx)-r*2, int(sy)-r*2))
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), r)
            pygame.draw.circle(surface, Blanco,
            (int(sx)-max(1,r//3), int(sy)-max(1,r//3)), max(2,r//3))


def agregar_comida(lista_comida):
    while len(lista_comida) < Comida_minimo:
        lista_comida.append(Food())


def _lerp_color(c1, c2, t):
    return (int(c1[0]+(c2[0]-c1[0])*t), int(c1[1]+(c2[1]-c1[1])*t), int(c1[2]+(c2[2]-c1[2])*t))

def _darker(c, amount=60):
    return (max(0,c[0]-amount), max(0,c[1]-amount), max(0,c[2]-amount))


class Snake:
    largo_inicial   = 10
    velocidad       = 2.5
    velocidad_boost = 5.0
    SPACING         = 3.0

    def __init__(self, x, y, color=Verde, head_color=Verde_Oscuro, skin_name="Clásico"):
        self.color       = color
        self.head_color  = head_color
        self._skin_name  = skin_name
        self.alive       = True
        self.score       = 0
        self.boost       = False
        self.angle       = 0.0
        pts = self.largo_inicial * int(Bloque / self.SPACING)
        self.segments    = [[float(x-i*self.SPACING), float(y)] for i in range(pts)]
        self._grow_accum = 0.0
        self._radii      = []
        self._rebuild_radii()

    @property
    def head(self):
        return self.segments[0]

    @property
    def radius(self):
        return 10 + min(len(self.segments)//80, 7)

    @property
    def skin_name(self):
        """Nombre de la skin basada en el color."""
        return getattr(self, '_skin_name', 'Clásico')

    def _rebuild_radii(self):
        n = len(self.segments)
        r_head = self.radius
        r_tail = max(3, r_head-6)
        constant_segments = 15
        self._radii = []
        for i in range(n):
            if i < constant_segments:
                self._radii.append(r_head)
            else:
                t = (i - constant_segments) / max(1, n - constant_segments - 1)
                self._radii.append(r_head - (r_head - r_tail) * t)

    def direccion(self, mx, my, camara):
        hx, hy = camara.aplicar(self.head[0], self.head[1])
        dx, dy = mx-hx, my-hy
        if abs(dx) > 1 or abs(dy) > 1:
            target = math.atan2(dy, dx)
            diff   = (target-self.angle+math.pi) % (2*math.pi) - math.pi
            self.angle += diff*0.18

    def direccion_teclado(self, keys):
        """Control por teclado: WASD o flechas."""
        turn_speed = 0.08
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= turn_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += turn_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            
            self.angle = self.angle
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            
            pass

    def mover(self):
        speed = self.velocidad_boost if self.boost else self.velocidad
        self.segments.insert(0, [self.head[0]+math.cos(self.angle)*speed,
                                  self.head[1]+math.sin(self.angle)*speed])
        if self._grow_accum >= 1.0:
            self._grow_accum -= 1.0
        else:
            self.segments.pop()
        if len(self._radii) != len(self.segments):
            self._rebuild_radii()

    def crecer(self, amount=1):
        self._grow_accum += amount*2
        self._rebuild_radii()

    def colision_pared(self):
        hx, hy = self.head
        if hx < 0 or hx > Ancho or hy < 0 or hy > Alto:
            self.alive = False

    def comer(self, lista_comida):
        hx, hy = self.head
        r = self.radius+10
        eaten = [f for f in lista_comida if math.hypot(f.x-hx, f.y-hy) < r+f.radius]
        for f in eaten:
            self.score += f.value
            self.crecer(f.value)
            lista_comida.remove(f)
        return bool(eaten)

    def colision_con(self, other):
        """True si la cabeza de self toca el cuerpo de other."""
        hx, hy = self.head
        hr     = self.radius
        step   = max(1, len(other.segments)//60)
        for i in range(0 if other is self else 5, len(other.segments), step):
            seg = other.segments[i]
            if math.hypot(seg[0]-hx, seg[1]-hy) < hr + max(3, int(other.radius*0.7)):
                return True
        return False

    def draw(self, surface, camara):
        sw, sh = surface.get_size()
        n      = len(self.segments)
        radii  = self._radii if len(self._radii)==n else [self.radius]*n
        body_c = self.color
        tail_c = _darker(self.color, 35)
        bord_c = _darker(self.color, 80)
        step = max(1, n//600)
        prev_sx, prev_sy = None, None
        for i in range(n-1, -1, -step):
            seg    = self.segments[i]
            sx, sy = camara.aplicar(seg[0], seg[1])
            if prev_sx is not None:
                if (-60<sx<sw+60 and -60<sy<sh+60) or (-60<prev_sx<sw+60 and -60<prev_sy<sh+60):
                    t   = i/max(1,n-1)
                    col = _lerp_color(body_c, tail_c, t)
                    r   = max(2, int(radii[i]))
                    pygame.draw.line(surface, bord_c, (int(prev_sx),int(prev_sy)), (int(sx),int(sy)), r*2+2)
                    pygame.draw.line(surface, col,    (int(prev_sx),int(prev_sy)), (int(sx),int(sy)), r*2)
            prev_sx, prev_sy = sx, sy
        
        hx, hy = camara.aplicar(self.head[0], self.head[1])
        hr = int(radii[0])
        shadow = pygame.Surface((hr*4,hr*4), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0,0,0,55), (hr*2+4,hr*2+4), hr+1)
        surface.blit(shadow, (int(hx)-hr*2, int(hy)-hr*2))
        pygame.draw.circle(surface, bord_c,          (int(hx),int(hy)), hr+1)

        
        if self._skin_name in FLAG_PATTERNS:
            _draw_flag(surface, int(hx), int(hy), hr * 2, self._skin_name)
        else:
            pygame.draw.circle(surface, self.head_color, (int(hx),int(hy)), hr)

        
        if self._skin_name not in FLAG_PATTERNS:
            gloss = pygame.Surface((hr*2,hr*2), pygame.SRCALPHA)
            pygame.draw.ellipse(gloss, (255,255,255,45), (hr//2,hr//5,hr,hr//2))
            surface.blit(gloss, (int(hx)-hr, int(hy)-hr))

        perp = self.angle+math.pi/2
        eye_dist, fwd = hr*0.52, hr*0.22
        for side in (-1,1):
            ex = hx+math.cos(self.angle)*fwd+math.cos(perp)*eye_dist*side
            ey = hy+math.sin(self.angle)*fwd+math.sin(perp)*eye_dist*side
            er = max(4, hr//2)
            pygame.draw.circle(surface, Blanco,    (int(ex),int(ey)), er)
            px = int(ex+math.cos(self.angle)*(er*0.28))
            py = int(ey+math.sin(self.angle)*(er*0.28))
            pygame.draw.circle(surface, (20,20,20), (px,py), max(2,er//2))
            pygame.draw.circle(surface, Blanco, (px+max(1,er//4),py-max(1,er//4)), max(1,er//4))


def _tshadow(surface, font, text, color, x, y, sh_col=(0,0,0), off=2):
    surface.blit(font.render(text, True, sh_col), (x+off, y+off))
    surface.blit(font.render(text, True, color),  (x, y))


def draw_borde(camara, superficie):
    corners = [camara.aplicar(0,0), camara.aplicar(Ancho,0),
            camara.aplicar(Ancho,Alto), camara.aplicar(0,Alto)]
    pygame.draw.lines(superficie, (255,80,80), True, corners, 3)


def draw_minimapa(superficie, snake, camara, bots=None):
    mm_w, mm_h = 160, 160
    mm_x = superficie.get_width() - mm_w - 10
    mm_y = 10
    sx_ = mm_w/Ancho
    sy_ = mm_h/Alto
    mm = pygame.Surface((mm_w, mm_h), pygame.SRCALPHA)
    mm.fill((0,0,0,150))
    pygame.draw.rect(mm, (100,100,100), (0,0,mm_w,mm_h), 1)
    if bots:
        for bot in bots:
            if bot.alive:
                pygame.draw.circle(mm, bot.color,
                    (int(bot.head[0]*sx_), int(bot.head[1]*sy_)), 3)
    pygame.draw.circle(mm, Verde, (int(snake.head[0]*sx_), int(snake.head[1]*sy_)), 5)
    pygame.draw.rect(mm, (200,200,200),
                    (int(camara.x*sx_), int(camara.y*sy_),
                    int(superficie.get_width()*sx_), int(superficie.get_height()*sy_)), 1)
    superficie.blit(mm, (mm_x, mm_y))


def draw_hud(superficie, snake, camara=None):
    font_big   = pygame.font.SysFont("consolas", 28, bold=True)
    font_small = pygame.font.SysFont("consolas", 18)
    _tshadow(superficie, font_big,   f"Score: {snake.score}",        Amarillo, 12, 12)
    _tshadow(superficie, font_small, f"Length: {len(snake.segments)}", Blanco,  12, 46)
    if snake.boost:
        _tshadow(superficie, font_small, "BOOST", (255,160,0), 12, 68)


def draw_lose(snake, superficie, camara=None):
    overlay = pygame.Surface(superficie.get_size(), pygame.SRCALPHA)
    overlay.fill((0,0,0,160))
    superficie.blit(overlay, (0,0))
    font_big   = pygame.font.SysFont("consolas", 64, bold=True)
    font_small = pygame.font.SysFont("consolas", 30)
    sw, sh = superficie.get_size()
    for surf, y in [
        (font_big.render("GAME OVER", True, Rojo),                                           sh//2-80),
        (font_small.render(f"Score: {snake.score}  Length: {len(snake.segments)}", True, Blanco), sh//2+10),
        (font_small.render("R = reiniciar  •  ESC = menú", True, Gris_Claro),                sh//2+55),
    ]:
        superficie.blit(surf, (sw//2-surf.get_width()//2, y))


def draw_snake(surface, camara=None):
    radius = 18
    border = SNAKE_BORDER_COLOR
    for pos in snake_segments:
        pygame.draw.circle(surface, border, pos, radius+1)
        pygame.draw.circle(surface, SNAKE_BASE_COLOR, pos, radius)
    head_pos = snake_segments[0]
    pygame.draw.circle(surface, border, head_pos, radius+1)
    pygame.draw.circle(surface, SNAKE_BASE_COLOR, head_pos, radius)
    eye_y, eye_offset = head_pos[1]-4, 10
    for side in (-1,1):
        ex = head_pos[0]+side*eye_offset
        pygame.draw.circle(surface, Blanco, (ex, eye_y), 9)
        pygame.draw.circle(surface, (20,20,20), (ex, eye_y), 5)
        pygame.draw.circle(surface, Blanco, (ex+2, eye_y-2), 2)


def draw_leaderboard(surface, player, bots, player_name="Tú"):
    sw = surface.get_width()

    entries = [(player_name, player.score, player.color, player.alive, True)]
    for bot in bots:
        entries.append((bot.name, bot.score, bot.color, bot.alive, False))
    entries.sort(key=lambda e: (0 if e[3] else 1, -e[1]))

    panel_w = 215
    row_h   = 36
    padding = 10
    panel_h = padding*2 + 30 + len(entries)*row_h + 4

    panel_x = sw - panel_w - 180
    panel_y = 10

    
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (8, 8, 20, 210), (0,0,panel_w,panel_h), border_radius=14)
    pygame.draw.rect(panel, (90,80,160,200), (0,0,panel_w,panel_h), 2, border_radius=14)
    surface.blit(panel, (panel_x, panel_y))

    font_title = pygame.font.SysFont("consolas", 15, bold=True)
    font_row   = pygame.font.SysFont("consolas", 15, bold=True)

    title = font_title.render("★  LEADERBOARD", True, (210,190,255))
    surface.blit(title, (panel_x + panel_w//2 - title.get_width()//2, panel_y+padding))

    sep_y = panel_y + padding + 24
    pygame.draw.line(surface, (90,80,160), (panel_x+8,sep_y), (panel_x+panel_w-8,sep_y), 1)

    medals = ["1", "2", "3", "4"]

    for rank, (name, score, color, alive, is_player) in enumerate(entries):
        ry = sep_y + 4 + rank*row_h

        
        if is_player:
            hl = pygame.Surface((panel_w-4, row_h-2), pygame.SRCALPHA)
            hl.fill((255,255,255,20))
            surface.blit(hl, (panel_x+2, ry))

        
        bar_col = color if alive else (50,50,50)
        pygame.draw.rect(surface, bar_col, (panel_x+4, ry+4, 4, row_h-8), border_radius=2)

        
        med_col = [(255,215,0),(192,192,192),(205,127,50),(150,150,150)][min(rank,3)]
        med_surf = font_row.render(f"#{rank+1}", True, med_col if alive else (60,60,60))
        surface.blit(med_surf, (panel_x+12, ry+row_h//2-med_surf.get_height()//2))

        display  = (name[:10]+"..") if len(name)>11 else name
        if not alive: display = f"[{display}]"
        name_col = Blanco if (is_player and alive) else (color if alive else (70,70,70))
        
        sh_n = font_row.render(display, True, (0,0,0))
        surface.blit(sh_n, (panel_x+50, ry+row_h//2-sh_n.get_height()//2+1))
        lbl_n = font_row.render(display, True, name_col)
        surface.blit(lbl_n, (panel_x+49, ry+row_h//2-lbl_n.get_height()//2))

        
        score_col = Amarillo if (is_player and alive) else ((190,190,80) if alive else (60,60,60))
        sh_s  = font_row.render(str(score), True, (0,0,0))
        lbl_s = font_row.render(str(score), True, score_col)
        sx_pos = panel_x + panel_w - lbl_s.get_width() - 10
        surface.blit(sh_s,  (sx_pos+1, ry+row_h//2-sh_s.get_height()//2+1))
        surface.blit(lbl_s, (sx_pos,   ry+row_h//2-lbl_s.get_height()//2))


def check_collisions(player, bots):
    if not player.alive:
        return
    
    for bot in bots:
        if not bot.alive:
            continue
        if player.colision_con(bot):
            player.alive = False
            return
    
    for bot in bots:
        if not bot.alive:
            continue
        if bot.colision_con(player):
            bot.alive = False
    
    for i, ba in enumerate(bots):
        if not ba.alive:
            continue
        for j, bb in enumerate(bots):
            if i == j or not bb.alive:
                continue
            if ba.colision_con(bb):
                ba.alive = False
                break


BOT_PALETTES = [
    ((220,60,180),(150,20,120)),
    ((0,180,220),(0,100,160)),
    ((255,180,0),(180,110,0)),
]
BOT_NAMES = ["Cazador", "Rondador", "Evasivo"]


class Bot(Snake):
    WALL_MARGIN = 120
    SMOOTH      = 0.12

    def __init__(self, x, y, color, head_color, mode='hunter', name='Bot'):
        super().__init__(x, y, color=color, head_color=head_color)
        self.mode          = mode
        self.name          = name
        self._orbit_angle  = random.uniform(0, math.pi*2)
        self._wander_timer = 0

    def _target_angle(self, food_list, others):
        hx, hy = self.head
        wall = self._wall_avoidance(hx, hy)
        if wall is not None: return wall
        if self.mode == 'hunter':  return self._hunt(hx, hy, food_list)
        if self.mode == 'patrol':  return self._patrol(hx, hy, food_list)
        if self.mode == 'evasive': return self._evasive(hx, hy, food_list, others)
        return self.angle

    def _wall_avoidance(self, hx, hy):
        m = self.WALL_MARGIN
        if not (hx<m or hx>Ancho-m or hy<m or hy>Alto-m): return None
        return math.atan2(Alto/2+random.uniform(-300,300)-hy,
                          Ancho/2+random.uniform(-300,300)-hx)

    def _hunt(self, hx, hy, food_list):
        best, best_d = None, float('inf')
        for f in food_list:
            d = math.hypot(f.x-hx, f.y-hy)
            if d < best_d: best_d, best = d, f
        return math.atan2(best.y-hy, best.x-hx) if best else self._wander()

    def _patrol(self, hx, hy, food_list):
        self._orbit_angle += 0.012
        ox = Ancho/2 + math.cos(self._orbit_angle)*700
        oy = Alto /2 + math.sin(self._orbit_angle)*700
        angle = math.atan2(oy-hy, ox-hx)
        for f in food_list:
            if math.hypot(f.x-hx, f.y-hy) < 200:
                fa   = math.atan2(f.y-hy, f.x-hx)
                diff = (fa-angle+math.pi)%(2*math.pi)-math.pi
                angle += diff*0.5
                break
        return angle

    def _evasive(self, hx, hy, food_list, others):
        for other in others:
            if other is self or not other.alive: continue
            if math.hypot(other.head[0]-hx, other.head[1]-hy) < 200:
                flee = math.atan2(hy-other.head[1], hx-other.head[0])
                return flee + random.choice([-1,1])*math.pi/4
        return self._hunt(hx, hy, food_list)

    def _wander(self):
        self._wander_timer -= 1
        if self._wander_timer <= 0:
            self._wander_timer = random.randint(40,120)
            self.angle = random.uniform(-math.pi, math.pi)
        return self.angle

    def update(self, food_list, others):
        if not self.alive: return
        target = self._target_angle(food_list, others)
        diff   = (target-self.angle+math.pi)%(2*math.pi)-math.pi
        self.angle += diff*self.SMOOTH
        self.mover()
        self.colision_pared()
        self.comer(food_list)


def crear_bots():
    bots, margin = [], 400
    modes = ['hunter','patrol','evasive']
    for i in range(3):
        x = random.randint(margin, Ancho-margin)
        y = random.randint(margin, Alto -margin)
        color, head_color = BOT_PALETTES[i]
        bots.append(Bot(x=x, y=y, color=color, head_color=head_color,
                        mode=modes[i], name=BOT_NAMES[i]))
    return bots


def actualizar_bots(bots, food_list):
    for bot in bots: bot.update(food_list, bots)


def dibujar_bots(surface, bots, camara):
    for bot in bots:
        if bot.alive: bot.draw(surface, camara)


SKINS = [
    
    (Verde,          Verde_Oscuro,   "Verde" ),
    ((220,60,60),    (160,20,20),    "Rojo"  ),
    ((0,180,220),    (0,100,160),    "Azul"  ),
    ((180,80,255),   (110,30,180),   "Púrpura"),
    ((255,80,160),   (180,20,100),   "Rosa"  ),
    ((255,190,0),    (180,110,0),    "Amarillo"),
    
    ((75, 160, 220), (255, 255, 255), "Argentina"),
    ((0, 150, 0),    (255, 220, 0),   "Brasil"),
    ((30, 30, 30),   (255, 215, 0),   "Alemania"),
    ((0, 100, 0),    (200, 0, 0),     "Italia"),
    ((0, 0, 180),    (255, 255, 255), "Francia"),
    ((200, 0, 0),    (255, 255, 255), "Japón"),
    ((255, 100, 0),  (0, 0, 150),     "Países Bajos"),
]

_star_cache = None


def _build_stars(sw, sh):
    stars = []
    for _ in range(220):
        x = random.randint(0,sw); y = random.randint(0,sh)
        r = random.choice([1,1,1,2])
        a = random.randint(80,255)
        col = random.choice([(255,255,255,a),(180,220,255,a),(255,200,100,a),(200,180,255,a)])
        stars.append((x,y,r,col))
    return stars


def _draw_menu_bg(surface, tick):
    global _star_cache
    sw, sh = surface.get_size()
    surface.fill((5,5,16))
    for col, ex, ey, ew, eh in [
        ((168,85,247,28), sw*0.05, sh*0.15, sw*0.65, sh*0.55),
        ((0,229,255,16),  sw*0.35, sh*0.4,  sw*0.65, sh*0.5 ),
        ((255,77,172,14), sw*0.2,  sh*0.6,  sw*0.55, sh*0.45),
    ]:
        blob = pygame.Surface((sw,sh), pygame.SRCALPHA)
        pygame.draw.ellipse(blob, col, (int(ex),int(ey),int(ew),int(eh)))
        surface.blit(blob, (0,0))
    if _star_cache is None:
        _star_cache = _build_stars(sw,sh)
    for (x,y,r,col) in _star_cache:
        alpha = int(col[3]*(0.6+0.4*math.sin(tick*0.04+x*0.05)))
        s = pygame.Surface((r*2+1,r*2+1), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col[:3],alpha), (r,r), r)
        surface.blit(s, (x-r,y-r))
    ray = pygame.Surface((sw,sh), pygame.SRCALPHA)
    intensity = int(22+14*math.sin(tick*0.03))
    pts = [(int(sw*0.55),0),(int(sw*0.62),sh//2),(int(sw*0.58),sh)]
    pygame.draw.lines(ray, (0,229,255,intensity), False, pts, 28)
    surface.blit(ray, (0,0))


def _outlined(font, text, color, outline=(0,0,0), thick=3):
    base = font.render(text, True, color)
    w = base.get_width() + thick*2
    h = base.get_height() + thick*2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for dx in range(-thick, thick+1):
        for dy in range(-thick, thick+1):
            if dx*dx+dy*dy <= thick*thick+1:
                o = font.render(text, True, outline)
                surf.blit(o, (dx+thick, dy+thick))
    surf.blit(base, (thick, thick))
    return surf


def _draw_logo(surface, tick):
    sw = surface.get_width()
    try:    font = pygame.font.SysFont("broadway", 72, bold=True)
    except: font = pygame.font.SysFont(None,    72, bold=True)
    colors = [(255,77,172),(255,220,60),(255,107,53)]
    t_cycle = (tick%120)/120.0
    idx   = int(t_cycle*3)%3
    col   = _lerp_color(colors[idx], colors[(idx+1)%3], (t_cycle*3)%1.0)
    lbl   = _outlined(font, "slither.io", col, (0,0,0), 5)
    surface.blit(lbl, (sw//2-lbl.get_width()//2, 42))


FLAG_PATTERNS = {
    "Argentina": {"type": "horizontal", "colors": [(75, 160, 220), (255, 255, 255), (75, 160, 220)], "symbol": "sun"},
    "Brasil": {"type": "horizontal", "colors": [(0, 150, 0), (255, 220, 0)], "symbol": "circle_stars"},
    "Alemania": {"type": "horizontal", "colors": [(30, 30, 30), (200, 0, 0), (255, 215, 0)], "symbol": None},
    "Italia": {"type": "vertical", "colors": [(0, 100, 0), (255, 255, 255), (200, 0, 0)], "symbol": None},
    "Francia": {"type": "vertical", "colors": [(0, 0, 180), (255, 255, 255), (200, 0, 0)], "symbol": None},
    "Japón": {"type": "special", "colors": [(255, 255, 255)], "symbol": "circle"},
    "Países Bajos": {"type": "horizontal", "colors": [(200, 0, 0), (255, 255, 255), (0, 0, 150)], "symbol": None},
}


def _draw_flag(surface, x, y, size, country_name):
    """Dibuja una bandera en el círculo dado."""
    if country_name not in FLAG_PATTERNS:
        return False

    flag_data = FLAG_PATTERNS[country_name]
    colors = flag_data["colors"]
    flag_type = flag_data["type"]
    symbol = flag_data.get("symbol")
    r = size // 2

    pygame.draw.circle(surface, (15, 15, 25), (x, y), r + 3)

    flag_surf = pygame.Surface((size, size), pygame.SRCALPHA)

    if flag_type == "horizontal":
        if len(colors) == 2:
            h = size // 2
            for i, color in enumerate(colors):
                pygame.draw.rect(flag_surf, color, (0, i * h, size, h))
        elif len(colors) == 3:
            h = size // 3
            for i, color in enumerate(colors):
                pygame.draw.rect(flag_surf, color, (0, i * h, size, h))
    elif flag_type == "vertical":
        w = size // 3
        for i, color in enumerate(colors):
            pygame.draw.rect(flag_surf, color, (i * w, 0, w, size))
    elif flag_type == "special":
        if country_name == "Japón":
            pygame.draw.rect(flag_surf, colors[0], (0, 0, size, size))
            pygame.draw.circle(flag_surf, (200, 0, 0), (r, r), r // 2)
        elif country_name == "Corea":
            pygame.draw.rect(flag_surf, colors[0], (0, 0, size, size))
            center_r = r
            pygame.draw.circle(flag_surf, (200, 0, 0), (r, r), center_r, 0, 0, 180)
            pygame.draw.circle(flag_surf, (0, 0, 150), (r, r), center_r, 0, 180, 180)
            pygame.draw.circle(flag_surf, (30, 30, 30), (r + center_r//2, r - center_r//3), center_r//5)
            pygame.draw.circle(flag_surf, (0, 0, 150), (r - center_r//2, r + center_r//3), center_r//5)
        elif country_name == "Inglaterra":
            pygame.draw.rect(flag_surf, (255, 255, 255), (0, 0, size, size))
            cw = size // 8
            pygame.draw.rect(flag_surf, (200, 0, 0), (r - cw//2, 0, cw, size))
            pygame.draw.rect(flag_surf, (200, 0, 0), (0, r - cw//2, size, cw))
            cw2 = size // 12
            pygame.draw.rect(flag_surf, (0, 0, 150), (r - cw2//2, 0, cw2, size))
            pygame.draw.rect(flag_surf, (0, 0, 150), (0, r - cw2//2, size, cw2))
            pygame.draw.line(flag_surf, (255, 255, 255), (0, 0), (size, size), cw2)
            pygame.draw.line(flag_surf, (255, 255, 255), (0, size), (size, 0), cw2)
            pygame.draw.line(flag_surf, (200, 0, 0), (0, 0), (size, size), cw2//2)
            pygame.draw.line(flag_surf, (200, 0, 0), (0, size), (size, 0), cw2//2)

    if symbol == "sun" and country_name == "Argentina":
        sun_r = size // 6
        pygame.draw.circle(flag_surf, (255, 200, 0), (r, r), sun_r)
        for i in range(16):
            angle = i * math.pi / 8
            x1 = r + int(math.cos(angle) * sun_r)
            y1 = r + int(math.sin(angle) * sun_r)
            x2 = r + int(math.cos(angle) * (sun_r + size//10))
            y2 = r + int(math.sin(angle) * (sun_r + size//10))
            pygame.draw.line(flag_surf, (255, 200, 0), (x1, y1), (x2, y2), 2)
    elif symbol == "circle_stars" and country_name == "Brasil":
        circle_r = size // 2.5
        pygame.draw.circle(flag_surf, (0, 50, 150), (r, r), circle_r)
        star_positions = [(r, r - circle_r//2), (r + circle_r//3, r - circle_r//4),
                          (r + circle_r//2, r), (r + circle_r//3, r + circle_r//4),
                          (r, r + circle_r//2), (r - circle_r//3, r + circle_r//4),
                          (r - circle_r//2, r), (r - circle_r//3, r - circle_r//4)]
        for sx, sy in star_positions:
            for j in range(5):
                angle = j * 2 * math.pi / 5 - math.pi/2
                px = sx + int(math.cos(angle) * size//25)
                py = sy + int(math.sin(angle) * size//25)
                if j == 0:
                    points = [(px, py)]
                else:
                    points.append((px, py))
            if points:
                pygame.draw.polygon(flag_surf, (255, 255, 255), points)
    elif symbol == "shield" and country_name == "España":
        shield_r = size // 4
        pygame.draw.circle(flag_surf, (255, 200, 0), (r, r), shield_r)
        pygame.draw.circle(flag_surf, (200, 0, 0), (r, r), shield_r - 2, 2)
    elif symbol == "eagle" and country_name == "México":
        pygame.draw.circle(flag_surf, (0, 100, 0), (r, r), size//5)
    elif symbol == "armillary" and country_name == "Portugal":
        pygame.draw.circle(flag_surf, (255, 220, 0), (r, r), size//5)
        pygame.draw.circle(flag_surf, (200, 0, 0), (r, r), size//5, 2)
    elif symbol == "circle" and country_name == "Japón":
        pass

    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (r, r), r)
    flag_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    surface.blit(flag_surf, (x - r, y - r))
    return True


def _draw_button(surface, rect, text, base_color, font, hovered):
    x, y, w, h = rect
    sh = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0,0,0,110), (0,0,w,h), border_radius=h//2)
    surface.blit(sh, (x+5,y+8))
    col = _lerp_color(base_color, (255,255,255), 0.2) if hovered else base_color
    pygame.draw.rect(surface, col, rect, border_radius=h//2)
    gl = pygame.Surface((w,h//2), pygame.SRCALPHA)
    gl.fill((255,255,255,32))
    surface.blit(gl, (x,y))
    bc = _lerp_color(base_color,(255,255,255),0.55)
    pygame.draw.rect(surface, bc, rect, 2, border_radius=h//2)
    lbl = _outlined(font, text, Blanco, (0,0,0), 2)
    surface.blit(lbl, (x+w//2-lbl.get_width()//2, y+h//2-lbl.get_height()//2))


def run_menu(screen):
    global _star_cache
    _star_cache = None

    sw, sh = screen.get_size()
    clock  = pygame.time.Clock()
    try:
        f_logo  = pygame.font.SysFont("broadway", 75, bold=True)
        f_btn   = pygame.font.SysFont("broadway", 32, bold=True)
        f_label = pygame.font.SysFont("broadway", 26, bold=True)
        f_input = pygame.font.SysFont("consolas", 20)
        f_small = pygame.font.SysFont("consolas", 12)
    except:
        f_logo  = pygame.font.SysFont(None, 90)
        f_btn   = pygame.font.SysFont(None, 42)
        f_label = pygame.font.SysFont(None, 28)
        f_input = pygame.font.SysFont(None, 28)
        f_small = pygame.font.SysFont(None, 20)
    cx   = sw//2
    bw   = 350
    bh   = 64
    by0  = sh//2 - 90

    input_rect = pygame.Rect(cx-bw//2, by0,        bw, 52)
    btn_local  = pygame.Rect(cx-bw//2, by0+76,     bw, bh)
    btn_ai     = pygame.Rect(cx-bw//2, by0+160,    bw, bh)

    sk_size = 46; sk_gap = 16
    total_w = len(SKINS)*sk_size + (len(SKINS)-1)*sk_gap
    sk_sx   = cx - total_w//2
    sk_y    = by0 + 256
    sk_rects = [pygame.Rect(sk_sx+i*(sk_size+sk_gap), sk_y, sk_size, sk_size) for i in range(len(SKINS))]

    nickname     = ""
    selected     = 0
    tick         = 0
    active_input = True

    while True:
        mx, my = pygame.mouse.get_pos()
        tick  += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(mx,my):
                    active_input = True
                elif btn_local.collidepoint(mx,my):
                    return (nickname.strip() or "Jugador", selected, "local")
                elif btn_ai.collidepoint(mx,my):
                    return (nickname.strip() or "Jugador", selected, "ai")
                for i, sr in enumerate(sk_rects):
                    if sr.collidepoint(mx,my): selected = i
            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                elif event.key == pygame.K_RETURN:
                    active_input = False
                elif len(nickname) < 18 and event.unicode.isprintable():
                    nickname += event.unicode

        _draw_menu_bg(screen, tick)
        _draw_logo(screen, tick)

        lbl_ap = _outlined(f_label, "APODO", (160,220,255), (0,0,0), 2)
        screen.blit(lbl_ap, (input_rect.x, input_rect.y - lbl_ap.get_height() - 6))

        inp = pygame.Surface((input_rect.w, input_rect.h), pygame.SRCALPHA)
        inp.fill((0,0,0,130))
        screen.blit(inp, input_rect.topleft)
        border_c = (100,220,120) if active_input else (60,100,60)
        pygame.draw.rect(screen, border_c, input_rect, 2, border_radius=26)
        disp = nickname if nickname else "Escribe tu nombre..."
        ncol = Blanco if nickname else (105,105,105)
        cur  = "|" if active_input and tick%60 < 30 else ""
        nlbl = _outlined(f_input, disp+cur, ncol, (0,0,0), 2)
        screen.blit(nlbl, (input_rect.x+input_rect.w//2-nlbl.get_width()//2,
                            input_rect.y+input_rect.h//2-nlbl.get_height()//2))

        _draw_button(screen, btn_local, "JUGAR LOCAL",     (22,130,210), f_btn, btn_local.collidepoint(mx,my))
        _draw_button(screen, btn_ai,   "JUGAR CONTRA IA", (195,65,25),  f_btn, btn_ai.collidepoint(mx,my))

        dots_y = btn_ai.bottom + 20
        dot_info = [("Cazador",(220,60,180)), ("Rondador",(0,180,220)), ("Evasivo",(255,180,0))]
        for i,(dn,dc) in enumerate(dot_info):
            dx = cx - 100 + i*100
            pulse = int(7+4*math.sin(tick*0.08+i*1.2))
            pygame.draw.circle(screen, dc, (dx,dots_y), pulse)
            nl = _outlined(f_small, dn, dc, (0,0,0), 2)
            screen.blit(nl, (dx-nl.get_width()//2, dots_y+pulse+5))

        sk_hdr = _outlined(f_label, "ELIGE TU SKIN", (160,220,255), (0,0,0), 2)
        screen.blit(sk_hdr, (cx-sk_hdr.get_width()//2, sk_y-sk_hdr.get_height()-8))

        for i,(sc,shc,sname) in enumerate(SKINS):
            sr = sk_rects[i]
            scx = sr.x+sr.w//2; scy = sr.y+sr.h//2
            pygame.draw.circle(screen, (15,15,25), (scx,scy), sr.w//2+3)
            if sname in FLAG_PATTERNS:
                _draw_flag(screen, scx, scy, sr.w, sname)
            else:
                pygame.draw.circle(screen, sc, (scx,scy), sr.w//2)
            if i == selected:
                pygame.draw.circle(screen, Blanco, (scx,scy), sr.w//2+5, 3)
            if sr.collidepoint(mx,my) or i==selected:
                tnl = _outlined(f_small, sname, Blanco, (0,0,0), 2)
                screen.blit(tnl, (scx-tnl.get_width()//2, sr.y-tnl.get_height()-3))

        pygame.display.flip()
        clock.tick(60)


GAME_CONFIG = {
    'resolution': (1280, 720),
    'control_mode': 'mouse',
    'selected_skin': 0,
    'nickname': 'Jugador',
}

RESOLUTIONS = [
    (800, 600),
    (1280, 720),
    (1920, 1080),
]


def run_main_menu(screen):
    """Menú principal con navegación a otros menús."""
    global _star_cache
    _star_cache = None

    sw, sh = screen.get_size()
    clock = pygame.time.Clock()

    try:
        f_title = pygame.font.SysFont("broadway", 55, bold=True)
        f_btn = pygame.font.SysFont("broadway", 30, bold=True)
    except:
        f_title = pygame.font.SysFont(None, 60)
        f_btn = pygame.font.SysFont(None, 40)

    cx = sw // 2
    bw = 280
    bh = 56
    start_y = sh // 2 - 20

    # Botones del menú
    btn_play = pygame.Rect(cx - bw // 2, start_y, bw, bh)
    btn_skins = pygame.Rect(cx - bw // 2, start_y + 70, bw, bh)
    btn_options = pygame.Rect(cx - bw // 2, start_y + 140, bw, bh)
    btn_back = pygame.Rect(cx - bw // 2, start_y + 210, bw, bh)

    tick = 0

    while True:
        mx, my = pygame.mouse.get_pos()
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_play.collidepoint(mx, my):
                    return 'play'
                elif btn_skins.collidepoint(mx, my):
                    return 'skins'
                elif btn_options.collidepoint(mx, my):
                    return 'options'
                elif btn_back.collidepoint(mx, my):
                    pygame.quit(); raise SystemExit

        _draw_menu_bg(screen, tick)
        _draw_logo(screen, tick)

        # Título del menú
        title = _outlined(f_title, "MENÚ PRINCIPAL", (160, 220, 255), (0, 0, 0), 3)
        screen.blit(title, (cx - title.get_width() // 2, start_y - 80))

        # Botones
        _draw_button(screen, btn_play, "JUGAR", (22, 130, 210), f_btn, btn_play.collidepoint(mx, my))
        _draw_button(screen, btn_skins, "SKINS", (180, 80, 255), f_btn, btn_skins.collidepoint(mx, my))
        _draw_button(screen, btn_options, "OPCIONES", (0, 180, 220), f_btn, btn_options.collidepoint(mx, my))
        _draw_button(screen, btn_back, "SALIR", (220, 60, 60), f_btn, btn_back.collidepoint(mx, my))

        pygame.display.flip()
        clock.tick(60)


def run_skins_menu(screen):
    """Menú de selección de skins separado."""
    global _star_cache

    sw, sh = screen.get_size()
    clock = pygame.time.Clock()

    try:
        f_title = pygame.font.SysFont("broadway", 45, bold=True)
        f_btn = pygame.font.SysFont("broadway", 26, bold=True)
        f_small = pygame.font.SysFont("consolas", 14)
    except:
        f_title = pygame.font.SysFont(None, 50)
        f_btn = pygame.font.SysFont(None, 32)
        f_small = pygame.font.SysFont(None, 20)

    cx = sw // 2

    # Grid de skins - 6 columnas
    sk_size = 60
    sk_gap = 20
    cols = 6
    rows = (len(SKINS) + cols - 1) // cols

    # Calcular posición del grid
    grid_w = cols * sk_size + (cols - 1) * sk_gap
    grid_h = rows * sk_size + (rows - 1) * sk_gap
    grid_x = cx - grid_w // 2
    grid_y = max(120, sh // 2 - grid_h // 2)

    sk_rects = []
    for row in range(rows):
        for col in range(cols):
            idx = row * cols + col
            if idx < len(SKINS):
                x = grid_x + col * (sk_size + sk_gap)
                y = grid_y + row * (sk_size + sk_gap)
                sk_rects.append(pygame.Rect(x, y, sk_size, sk_size))
            else:
                sk_rects.append(None)

    # Botón volver
    btn_back = pygame.Rect(cx - 120, sh - 80, 240, 50)

    selected = GAME_CONFIG['selected_skin']
    tick = 0

    while True:
        mx, my = pygame.mouse.get_pos()
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.collidepoint(mx, my):
                    return
                # Seleccionar skin
                for i, sr in enumerate(sk_rects):
                    if sr is not None and sr.collidepoint(mx, my):
                        selected = i
                        GAME_CONFIG['selected_skin'] = i

        _draw_menu_bg(screen, tick)

        # Título
        title = _outlined(f_title, "ELIGE TU SKIN", (160, 220, 255), (0, 0, 0), 3)
        screen.blit(title, (cx - title.get_width() // 2, 60))

        # Grid de skins
        for i, sr in enumerate(sk_rects):
            if sr is None:
                continue
            sc, shc, sname = SKINS[i]
            scx = sr.x + sr.w // 2
            scy = sr.y + sr.h // 2

            # Fondo del círculo
            pygame.draw.circle(screen, (15, 15, 25), (scx, scy), sr.w // 2 + 5)

            # Si es una skin de país, dibujar la bandera
            if sname in FLAG_PATTERNS:
                _draw_flag(screen, scx, scy, sr.w, sname)
            else:
                # Círculo de color para skins normales
                pygame.draw.circle(screen, sc, (scx, scy), sr.w // 2)

            # Borde de selección
            if i == selected:
                pygame.draw.circle(screen, Blanco, (scx, scy), sr.w // 2 + 5, 3)

            # Nombre de la skin al hover
            if sr.collidepoint(mx, my) or i == selected:
                tnl = _outlined(f_small, sname, Blanco, (0, 0, 0), 2)
                screen.blit(tnl, (scx - tnl.get_width() // 2, sr.y - tnl.get_height() - 5))

        # Indicador de skin seleccionada
        info_text = f"Skin seleccionada: {SKINS[selected][2]}"
        info = _outlined(f_btn, info_text, Amarillo, (0, 0, 0), 2)
        screen.blit(info, (cx - info.get_width() // 2, grid_y + grid_h + 20))

        # Botón volver
        _draw_button(screen, btn_back, "VOLVER", (100, 100, 100), f_btn, btn_back.collidepoint(mx, my))

        pygame.display.flip()
        clock.tick(60)


def run_options_menu(screen):
    """Menú de opciones: resolución y controles."""
    global _star_cache

    sw, sh = screen.get_size()
    clock = pygame.time.Clock()

    try:
        f_title = pygame.font.SysFont("broadway", 45, bold=True)
        f_btn = pygame.font.SysFont("broadway", 24, bold=True)
        f_label = pygame.font.SysFont("broadway", 22, bold=True)
    except:
        f_title = pygame.font.SysFont(None, 50)
        f_btn = pygame.font.SysFont(None, 30)
        f_label = pygame.font.SysFont(None, 28)

    cx = sw // 2

    # Sección Resolución
    res_label_y = 150
    res_btns = []
    res_btn_w = 140
    res_btn_h = 40
    res_start_x = cx - (len(RESOLUTIONS) * res_btn_w + (len(RESOLUTIONS) - 1) * 20) // 2

    for i, res in enumerate(RESOLUTIONS):
        x = res_start_x + i * (res_btn_w + 20)
        rect = pygame.Rect(x, res_label_y + 30, res_btn_w, res_btn_h)
        res_btns.append((rect, res))

    # Sección Controles
    ctrl_label_y = 300
    btn_mouse = pygame.Rect(cx - 160, ctrl_label_y + 30, 140, 45)
    btn_keyboard = pygame.Rect(cx + 20, ctrl_label_y + 30, 140, 45)

    # Botón volver
    btn_back = pygame.Rect(cx - 120, sh - 80, 240, 50)

    tick = 0

    while True:
        mx, my = pygame.mouse.get_pos()
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.collidepoint(mx, my):
                    return

                # Cambiar resolución
                for rect, res in res_btns:
                    if rect.collidepoint(mx, my):
                        GAME_CONFIG['resolution'] = res

                # Cambiar modo de control
                if btn_mouse.collidepoint(mx, my):
                    GAME_CONFIG['control_mode'] = 'mouse'
                elif btn_keyboard.collidepoint(mx, my):
                    GAME_CONFIG['control_mode'] = 'keyboard'

        _draw_menu_bg(screen, tick)

        # Título
        title = _outlined(f_title, "OPCIONES", (160, 220, 255), (0, 0, 0), 3)
        screen.blit(title, (cx - title.get_width() // 2, 60))

        # Sección Resolución
        res_label = _outlined(f_label, "RESOLUCIÓN", (255, 200, 100), (0, 0, 0), 2)
        screen.blit(res_label, (cx - res_label.get_width() // 2, res_label_y))

        current_res = GAME_CONFIG['resolution']
        for rect, res in res_btns:
            is_selected = res == current_res
            is_hovered = rect.collidepoint(mx, my)
            color = (100, 200, 100) if is_selected else (60, 60, 80)
            text = f"{res[0]}x{res[1]}"
            _draw_button(screen, rect, text, color, f_btn, is_hovered)

        # Sección Controles
        ctrl_label = _outlined(f_label, "CONTROLES", (100, 200, 255), (0, 0, 0), 2)
        screen.blit(ctrl_label, (cx - ctrl_label.get_width() // 2, ctrl_label_y))

        # Botón Mouse
        mouse_color = (100, 200, 100) if GAME_CONFIG['control_mode'] == 'mouse' else (60, 60, 80)
        _draw_button(screen, btn_mouse, "MOUSE", mouse_color, f_btn, btn_mouse.collidepoint(mx, my))

        # Botón Teclado
        keyb_color = (100, 200, 100) if GAME_CONFIG['control_mode'] == 'keyboard' else (60, 60, 80)
        _draw_button(screen, btn_keyboard, "TECLADO", keyb_color, f_btn, btn_keyboard.collidepoint(mx, my))

        # Instrucciones de teclado
        if GAME_CONFIG['control_mode'] == 'keyboard':
            instr = _outlined(f_btn, "WASD o Flechas para girar", (150, 150, 150), (0, 0, 0), 1)
            screen.blit(instr, (cx - instr.get_width() // 2, ctrl_label_y + 90))

        # Info actual
        info_text = f"Actual: {current_res[0]}x{current_res[1]} | {GAME_CONFIG['control_mode'].upper()}"
        info = _outlined(f_btn, info_text, Amarillo, (0, 0, 0), 2)
        screen.blit(info, (cx - info.get_width() // 2, 400))

        # Botón volver
        _draw_button(screen, btn_back, "VOLVER", (100, 100, 100), f_btn, btn_back.collidepoint(mx, my))

        pygame.display.flip()
        clock.tick(60)


def run_game_setup(screen):
    """Pantalla de configuración antes de jugar (nombre y modo)."""
    global _star_cache
    _star_cache = None

    sw, sh = screen.get_size()
    clock = pygame.time.Clock()

    try:
        f_title = pygame.font.SysFont("broadway", 45, bold=True)
        f_btn = pygame.font.SysFont("broadway", 28, bold=True)
        f_label = pygame.font.SysFont("broadway", 24, bold=True)
        f_input = pygame.font.SysFont("consolas", 22)
    except:
        f_title = pygame.font.SysFont(None, 50)
        f_btn = pygame.font.SysFont(None, 36)
        f_label = pygame.font.SysFont(None, 30)
        f_input = pygame.font.SysFont(None, 28)

    cx = sw // 2
    bw = 300
    bh = 54

    # Input de nombre
    input_rect = pygame.Rect(cx - bw // 2, 180, bw, 50)

    # Botones de modo
    btn_local = pygame.Rect(cx - bw // 2, 300, bw, bh)
    btn_ai = pygame.Rect(cx - bw // 2, 370, bw, bh)

    # Botón volver
    btn_back = pygame.Rect(cx - 100, 450, 200, 45)

    nickname = GAME_CONFIG['nickname']
    selected = GAME_CONFIG['selected_skin']
    active_input = True
    tick = 0

    while True:
        mx, my = pygame.mouse.get_pos()
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(mx, my):
                    active_input = True
                elif btn_local.collidepoint(mx, my):
                    GAME_CONFIG['nickname'] = nickname.strip() or "Jugador"
                    return (GAME_CONFIG['nickname'], selected, "local")
                elif btn_ai.collidepoint(mx, my):
                    GAME_CONFIG['nickname'] = nickname.strip() or "Jugador"
                    return (GAME_CONFIG['nickname'], selected, "ai")
                elif btn_back.collidepoint(mx, my):
                    return None
            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                elif event.key == pygame.K_RETURN:
                    active_input = False
                elif len(nickname) < 15 and event.unicode.isprintable():
                    nickname += event.unicode

        _draw_menu_bg(screen, tick)

        # Título
        title = _outlined(f_title, "NUEVA PARTIDA", (160, 220, 255), (0, 0, 0), 3)
        screen.blit(title, (cx - title.get_width() // 2, 60))

        # Input de nombre
        lbl_ap = _outlined(f_label, "APODO", (160, 220, 255), (0, 0, 0), 2)
        screen.blit(lbl_ap, (input_rect.x, input_rect.y - lbl_ap.get_height() - 8))

        inp = pygame.Surface((input_rect.w, input_rect.h), pygame.SRCALPHA)
        inp.fill((0, 0, 0, 130))
        screen.blit(inp, input_rect.topleft)
        border_c = (100, 220, 120) if active_input else (60, 100, 60)
        pygame.draw.rect(screen, border_c, input_rect, 2, border_radius=25)
        disp = nickname if nickname else "Tu nombre..."
        ncol = Blanco if nickname else (105, 105, 105)
        cur = "|" if active_input and tick % 60 < 30 else ""
        nlbl = _outlined(f_input, disp + cur, ncol, (0, 0, 0), 2)
        screen.blit(nlbl, (input_rect.x + input_rect.w // 2 - nlbl.get_width() // 2,
                           input_rect.y + input_rect.h // 2 - nlbl.get_height() // 2))

        # Botones de modo
        _draw_button(screen, btn_local, "MODO LOCAL", (22, 130, 210), f_btn, btn_local.collidepoint(mx, my))
        _draw_button(screen, btn_ai, "CONTRA IA", (195, 65, 25), f_btn, btn_ai.collidepoint(mx, my))

        # Skin actual
        skin_info = f"Skin: {SKINS[selected][2]}"
        skin_lbl = _outlined(f_label, skin_info, (255, 200, 100), (0, 0, 0), 2)
        screen.blit(skin_lbl, (cx - skin_lbl.get_width() // 2, 440))

        # Botón volver
        _draw_button(screen, btn_back, "VOLVER", (100, 100, 100), f_btn, btn_back.collidepoint(mx, my))

        pygame.display.flip()
        clock.tick(60)