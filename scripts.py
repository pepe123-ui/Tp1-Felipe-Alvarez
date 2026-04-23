import pygame, math, random, sys

# ── COLORES ──────────────────────────────────────────────────────────────────
Negro        = (0,   0,   0  )
Blanco       = (255, 255, 255)
Verde        = (50,  200, 50 )
Verde_Oscuro = (20,  140, 20 )
Rojo         = (220, 60,  60 )
Azul         = (0,   180, 220)
Púrpura      = (180, 80,  255)
Rosa         = (255, 80,  160)
Amarillo     = (255, 220, 0  )
Gris         = (40,  40,  40 )
Gris_Claro   = (80,  80,  80 )

# ── CONFIG ───────────────────────────────────────────────────────────────────
Ancho = Alto = 3000
BG_COLOR   = (15, 15, 15)
GRID_COLOR = (35, 35, 35)

PLAYER_COLORS = [
    (Verde,      Verde_Oscuro),
    (Rojo,       (140, 20, 20)),
    (Azul,       (0,   100, 160)),
    (Amarillo,   (180, 120, 0)),
]

CONTROL_SCHEMES = [
    {'left': pygame.K_a,     'right': pygame.K_d,     'boost': pygame.K_LSHIFT},
    {'left': pygame.K_LEFT,  'right': pygame.K_RIGHT, 'boost': pygame.K_RSHIFT},
    {'left': pygame.K_j,     'right': pygame.K_l,     'boost': pygame.K_i},
    {'left': pygame.K_f,     'right': pygame.K_h,     'boost': pygame.K_t},
]

PLAYER_NAMES = ["P1 (A/D)", "P2 (←/→)", "P3 (J/L)", "P4 (F/H)"]

# ── SKINS ────────────────────────────────────────────────────────────────────
# (nombre, color_cuerpo, color_cabeza, tipo_flag)  tipo_flag=None = color solido
SKINS = [
    ("Verde",      (50,200,50),   (20,140,20),   None),
    ("Rojo",       (220,60,60),   (140,20,20),   None),
    ("Azul",       (0,180,220),   (0,100,160),   None),
    ("Púrpura",    (180,80,255),  (110,30,180),  None),
    ("Rosa",       (255,80,160),  (180,20,100),  None),
    ("Amarillo",   (255,200,0),   (180,120,0),   None),
    ("Argentina",  (75,160,220),  (255,255,255), "ARG"),
    ("Brasil",     (0,160,0),     (255,220,0),   "BRA"),
    ("Alemania",   (30,30,30),    (255,215,0),   "GER"),
    ("Italia",     (0,100,0),     (200,0,0),     "ITA"),
    ("Francia",    (0,0,180),     (255,255,255), "FRA"),
    ("Japón",      (200,0,0),     (255,255,255), "JPN"),
    ("España",     (200,0,0),     (255,200,0),   "ESP"),
    ("USA",        (0,0,180),     (200,0,0),     "USA"),
]

# skin seleccionada por cada jugador
PLAYER_SKINS = [0, 1, 2, 3]

def _draw_flag(surface, cx, cy, r, flag_code):
    """Dibuja bandera dentro de circulo de radio r centrado en cx,cy."""
    size = r*2
    fs = pygame.Surface((size,size), pygame.SRCALPHA)

    if flag_code == "ARG":
        for i,c in enumerate([(75,160,220),(255,255,255),(75,160,220)]):
            pygame.draw.rect(fs, c, (0, i*(size//3), size, size//3+1))
        pygame.draw.circle(fs, (255,200,0), (r,r), r//3)

    elif flag_code == "BRA":
        pygame.draw.rect(fs, (0,160,0), (0,0,size,size))
        pts=[(r,4),(size-4,r),(r,size-4),(4,r)]
        pygame.draw.polygon(fs, (255,220,0), pts)
        pygame.draw.circle(fs, (0,50,150), (r,r), r//3)

    elif flag_code == "GER":
        for i,c in enumerate([(20,20,20),(200,0,0),(255,215,0)]):
            pygame.draw.rect(fs, c, (0, i*(size//3), size, size//3+1))

    elif flag_code == "ITA":
        for i,c in enumerate([(0,140,0),(255,255,255),(200,0,0)]):
            pygame.draw.rect(fs, c, (i*(size//3),0, size//3+1, size))

    elif flag_code == "FRA":
        for i,c in enumerate([(0,0,180),(255,255,255),(200,0,0)]):
            pygame.draw.rect(fs, c, (i*(size//3),0, size//3+1, size))

    elif flag_code == "JPN":
        pygame.draw.rect(fs, (255,255,255), (0,0,size,size))
        pygame.draw.circle(fs, (200,0,0), (r,r), r//2)

    elif flag_code == "ESP":
        pygame.draw.rect(fs, (200,0,0), (0,0,size,size))
        pygame.draw.rect(fs, (255,200,0), (0,size//4, size, size//2))

    elif flag_code == "USA":
        stripe_h = max(1, size//13)
        for i in range(13):
            c = (200,0,0) if i%2==0 else (255,255,255)
            pygame.draw.rect(fs, c, (0,i*stripe_h,size,stripe_h+1))
        pygame.draw.rect(fs, (0,0,150), (0,0,size//2,size//2))
        for row in range(3):
            for col in range(3):
                pygame.draw.circle(fs,(255,255,255),(size//12+col*(size//6), size//12+row*(size//8)),2)

    # mascara circular
    mask = pygame.Surface((size,size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255,255,255,255), (r,r), r)
    fs.blit(mask,(0,0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(fs, (cx-r, cy-r))

def _draw_skin_circle(surface, cx, cy, r, skin_idx):
    """Dibuja preview de skin (bandera o color solido)."""
    sname,scol,shcol,flag = SKINS[skin_idx]
    pygame.draw.circle(surface, (10,10,20), (cx,cy), r+3)
    if flag:
        _draw_flag(surface, cx, cy, r, flag)
    else:
        pygame.draw.circle(surface, scol, (cx,cy), r)
    pygame.draw.circle(surface, (60,60,80), (cx,cy), r, 2)

def menu_skins(screen, player_idx=0):
    """Mini menú de skins para un jugador. Retorna skin_idx elegido."""
    global _star_cache; _star_cache=None
    sw,sh=screen.get_size(); clock=pygame.time.Clock()
    try:
        f_title=pygame.font.SysFont("broadway",36,bold=True)
        f_btn=pygame.font.SysFont("broadway",22,bold=True)
        f_sm=pygame.font.SysFont("consolas",14)
    except:
        f_title=pygame.font.SysFont(None,42); f_btn=pygame.font.SysFont(None,28); f_sm=pygame.font.SysFont(None,18)

    cx=sw//2; sk_r=28; sk_gap=14; cols=7
    rows=(len(SKINS)+cols-1)//cols
    grid_w=cols*(sk_r*2+sk_gap)-sk_gap
    gx=cx-grid_w//2; gy=sh//2-80

    sk_rects=[]
    for idx in range(len(SKINS)):
        col_i=idx%cols; row_i=idx//cols
        scx=gx+col_i*(sk_r*2+sk_gap)+sk_r
        scy=gy+row_i*(sk_r*2+sk_gap+8)+sk_r
        sk_rects.append((scx,scy))

    selected=PLAYER_SKINS[player_idx]
    btn_ok=pygame.Rect(cx-90,sh-80,180,46); tick=0

    while True:
        mx,my=pygame.mouse.get_pos(); tick+=1
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                for i,(scx,scy) in enumerate(sk_rects):
                    if math.hypot(mx-scx,my-scy)<sk_r+4: selected=i
                if btn_ok.collidepoint(mx,my):
                    PLAYER_SKINS[player_idx]=selected; return selected
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                return PLAYER_SKINS[player_idx]

        draw_menu_bg(screen,tick)
        pcol=PLAYER_COLORS[player_idx][0]
        title=_outlined(f_title,f"SKIN - P{player_idx+1}",pcol,(0,0,0),3)
        screen.blit(title,(cx-title.get_width()//2,sh//4))

        for i,(scx,scy) in enumerate(sk_rects):
            _draw_skin_circle(screen,scx,scy,sk_r,i)
            if i==selected:
                pygame.draw.circle(screen,Blanco,(scx,scy),sk_r+5,3)
            if math.hypot(mx-scx,my-scy)<sk_r+4 or i==selected:
                nl=_outlined(f_sm,SKINS[i][0],Blanco,(0,0,0),1)
                screen.blit(nl,(scx-nl.get_width()//2,scy-sk_r-nl.get_height()-2))

        info=_outlined(f_btn,f"Elegida: {SKINS[selected][0]}",Amarillo,(0,0,0),2)
        screen.blit(info,(cx-info.get_width()//2,gy+rows*(sk_r*2+sk_gap+8)+10))
        _draw_button(screen,btn_ok,"CONFIRMAR",(22,130,210),f_btn,btn_ok.collidepoint(mx,my))
        pygame.display.flip(); clock.tick(60)

# ── HEX TILE (fondo) ─────────────────────────────────────────────────────────
_hex_tile = None
_TILE_W = _TILE_H = 0
_HEX_R = 42; _HEX_GAP = 3
_C_BG = (10, 12, 16); _C_FILL = (18, 22, 28); _C_INNER = (14, 17, 22); _C_BORDER = (44, 52, 62)

def _hex_pts(cx, cy, r):

def _build_hex_tile():
    global _hex_tile, _TILE_W, _TILE_H
    r = _HEX_R; col_w = math.sqrt(3)*r; row_h = 1.5*r
    COLS, ROWS = 5, 4; tw = int(col_w*COLS); th = int(row_h*ROWS+r)
    surf = pygame.Surface((tw, th)); surf.fill(_C_BG)
    for col in range(-2, COLS+2):
        for row in range(-2, ROWS+2):
            cx = col*col_w + (col_w/2 if row%2 else 0); cy = row*row_h + r
            if -r*2 <= cx <= tw+r*2 and -r*2 <= cy <= th+r*2:
                pygame.draw.polygon(surf, _C_FILL,   _hex_pts(cx, cy, r-_HEX_GAP))
                pygame.draw.polygon(surf, _C_BORDER, _hex_pts(cx, cy, r-_HEX_GAP), 2)
                pygame.draw.polygon(surf, _C_INNER,  _hex_pts(cx, cy, r-_HEX_GAP-9))
    _hex_tile = surf; _TILE_W = tw; _TILE_H = th

def draw_mapa(surface, camara):
    global _hex_tile
    if _hex_tile is None: _build_hex_tile()
    sw, sh = surface.get_size()
    ox = camara.x % _TILE_W; oy = camara.y % _TILE_H
    y = -int(oy)
    while y < sh:
        x = -int(ox)
        while x < sw:
            surface.blit(_hex_tile, (x, y)); x += _TILE_W
        y += _TILE_H

# ── CAMERA ───────────────────────────────────────────────────────────────────
class Camera:
    def __init__(self, w, h): self.x = self.y = 0; self.w = w; self.h = h
    def apply(self, x, y):    return x - self.x, y - self.y
    def follow(self, x, y):
        self.x = max(0, min(x - self.w//2, Ancho - self.w))
        self.y = max(0, min(y - self.h//2, Alto  - self.h))

# ── FOOD ─────────────────────────────────────────────────────────────────────
FOOD_COLORS = [(255,80,80),(255,200,50),(80,220,80),(80,180,255),(255,120,200),(200,100,255)]

class Food:
    def __init__(self):
        self.x = random.randint(100, Ancho-100); self.y = random.randint(100, Alto-100)
        self.color = random.choice(FOOD_COLORS)
        self.radius = random.randint(6, 11); self.value = max(1, self.radius-4)
        self.pulse = random.uniform(0, math.pi*2)

    def update(self): self.pulse += 0.08

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        sw, sh = surface.get_size()
        if -30 < sx < sw+30 and -30 < sy < sh+30:
            r = self.radius + int(math.sin(self.pulse)*2)
            halo = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
            pygame.draw.circle(halo, (*self.color, 55), (r*2, r*2), r*2)
            surface.blit(halo, (int(sx)-r*2, int(sy)-r*2))
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), r)
            pygame.draw.circle(surface, Blanco, (int(sx)-max(1,r//3), int(sy)-max(1,r//3)), max(2,r//3))

# ── HELPERS ───────────────────────────────────────────────────────────────────
def _lerp_color(c1, c2, t):

def _darker(c, a=60): return (max(0,c[0]-a), max(0,c[1]-a), max(0,c[2]-a))

def _tshadow(surf, font, text, col, x, y, sc=(0,0,0), off=2):
    surf.blit(font.render(text, True, sc), (x+off, y+off))
    surf.blit(font.render(text, True, col), (x, y))

# ── SNAKE ────────────────────────────────────────────────────────────────────
class Snake:
    def __init__(self, x, y, color, head_color):
        self.color = color; self.head_color = head_color
        self.alive = True; self.score = 0; self.boost = False; self.angle = 0.0
        self.segments = [[float(x-i*3), float(y)] for i in range(30)]
        self._grow_accum = 0.0

    @property
    def head(self): return self.segments[0]

    @property
    def radius(self): return 10 + min(len(self.segments)//80, 7)

    def turn(self, direction):
        spd = 0.08
        if direction == 'left':  self.angle -= spd
        elif direction == 'right': self.angle += spd

    def aim_mouse(self, mx, my, cam):
        hx, hy = cam.apply(self.head[0], self.head[1])
        dx, dy = mx-hx, my-hy
        if abs(dx) > 1 or abs(dy) > 1:
            target = math.atan2(dy, dx)
            diff = (target-self.angle+math.pi) % (2*math.pi) - math.pi
            self.angle += diff*0.18

    def move(self):
        speed = 5.0 if self.boost else 2.5
        nx = (self.head[0] + math.cos(self.angle)*speed) % Ancho
        ny = (self.head[1] + math.sin(self.angle)*speed) % Alto
        self.segments.insert(0, [nx, ny])
        if self._grow_accum >= 1.0: self._grow_accum -= 1.0
        else: self.segments.pop()

    def grow(self, amount=1): self._grow_accum += amount*2

    def eat(self, food_list):
        hx, hy = self.head; r = self.radius+10
        eaten = [f for f in food_list if math.hypot(f.x-hx, f.y-hy) < r+f.radius]
        for f in eaten:
            self.score += f.value; self.grow(f.value); food_list.remove(f)

    def collides_with(self, other):
        if not other.alive: return False
        hx, hy = self.head; hr = self.radius
        start = 0 if other is self else 5
        step = max(1, len(other.segments)//60)
        for i in range(start, len(other.segments), step):
            if math.hypot(other.segments[i][0]-hx, other.segments[i][1]-hy) < hr + max(3, int(other.radius*0.7)):
                return True
        return False

    def draw(self, surface, cam):
        sw, sh = surface.get_size(); n = len(self.segments)
        body_c = self.color; tail_c = _darker(self.color, 35); bord_c = _darker(self.color, 80)
        step = max(1, n//600); prev = None
        for i in range(n-1, -1, -step):
            sx, sy = cam.apply(self.segments[i][0], self.segments[i][1])
            if prev:
                if (-60<sx<sw+60 and -60<sy<sh+60) or (-60<prev[0]<sw+60 and -60<prev[1]<sh+60):
                    t = i/max(1, n-1); col = _lerp_color(body_c, tail_c, t)
                    r = max(2, int((10 + min(n//80, 7))*(1-t*0.3)))
                    pygame.draw.line(surface, bord_c, prev, (int(sx),int(sy)), r*2+2)
                    pygame.draw.line(surface, col,    prev, (int(sx),int(sy)), r*2)
            prev = (int(sx), int(sy))
        # cabeza
        hx, hy = cam.apply(self.head[0], self.head[1]); hr = self.radius
        pygame.draw.circle(surface, bord_c, (int(hx),int(hy)), hr+1)
        flag=getattr(self,'flag',None)
        if flag: _draw_flag(surface,int(hx),int(hy),hr,flag)
        else: pygame.draw.circle(surface, self.head_color, (int(hx),int(hy)), hr)
        perp = self.angle+math.pi/2; eye_d = hr*0.52; fwd = hr*0.22
        for side in (-1,1):
            ex = hx+math.cos(self.angle)*fwd+math.cos(perp)*eye_d*side
            ey = hy+math.sin(self.angle)*fwd+math.sin(perp)*eye_d*side
            er = max(4, hr//2)
            pygame.draw.circle(surface, Blanco, (int(ex),int(ey)), er)
            px = int(ex+math.cos(self.angle)*(er*0.28)); py = int(ey+math.sin(self.angle)*(er*0.28))
            pygame.draw.circle(surface, (20,20,20), (px,py), max(2,er//2))

# ── BOT ──────────────────────────────────────────────────────────────────────
class Bot(Snake):
    def __init__(self, x, y, color, head_color, name='Bot'):
        super().__init__(x, y, color, head_color)
        self.name = name; self._wander_timer = 0

    def update(self, food_list, others):
        if not self.alive: return
        hx, hy = self.head
        # wall avoidance
        m = 150
        if hx<m or hx>Ancho-m or hy<m or hy>Alto-m:
            ta = math.atan2(Alto/2-hy, Ancho/2-hx)
        else:
            best, bd = None, float('inf')
            for f in food_list:
                d = math.hypot(f.x-hx, f.y-hy)
                if d < bd: bd, best = d, f
            if best: ta = math.atan2(best.y-hy, best.x-hx)
            else:
                self._wander_timer -= 1
                if self._wander_timer <= 0:
                    self.angle = random.uniform(-math.pi, math.pi); self._wander_timer = random.randint(40,120)
                ta = self.angle
        diff = (ta-self.angle+math.pi)%(2*math.pi)-math.pi
        self.angle += diff*0.12
        self.move(); self.eat(food_list)

# ── DRAW HELPERS ─────────────────────────────────────────────────────────────
def draw_border(surface, cam):
    corners = [cam.apply(0,0), cam.apply(Ancho,0), cam.apply(Ancho,Alto), cam.apply(0,Alto)]
    pygame.draw.lines(surface, (255,80,80), True, corners, 3)

def draw_minimap(surface, snakes, cam, colors):
    mw = mh = 160; mx0 = surface.get_width()-mw-10; my0 = 10
    sx_ = mw/Ancho; sy_ = mh/Alto
    mm = pygame.Surface((mw, mh), pygame.SRCALPHA); mm.fill((0,0,0,150))
    pygame.draw.rect(mm, (100,100,100), (0,0,mw,mh), 1)
    for s, col in zip(snakes, colors):
        if s.alive:
            pygame.draw.circle(mm, col, (int(s.head[0]*sx_), int(s.head[1]*sy_)), 4)
    pygame.draw.rect(mm, (200,200,200),
        (int(cam.x*sx_), int(cam.y*sy_), int(surface.get_width()*sx_), int(surface.get_height()*sy_)), 1)
    surface.blit(mm, (mx0, my0))

def draw_hud_multi(surface, players, names):
    font = pygame.font.SysFont("consolas", 22, bold=True)
    font_sm = pygame.font.SysFont("consolas", 15)
    y = 12
    for i, (p, n) in enumerate(zip(players, names)):
        col = PLAYER_COLORS[i][0]
        status = f"{n}: {p.score}" if p.alive else f"{n}: MUERTO"
        _tshadow(surface, font, status, col, 12, y)
        y += 28
    # controles hint
    hints = ["P1:A/D+LShift", "P2:←/→+RShift", "P3:J/L+I", "P4:F/H+T"]
    for i, h in enumerate(hints[:len(players)]):
        col = PLAYER_COLORS[i][0]
        lbl = font_sm.render(h, True, col)
        surface.blit(lbl, (12, surface.get_height()-20-(len(players)-i)*18))

def draw_hud_solo(surface, player, cam):
    font = pygame.font.SysFont("consolas", 28, bold=True)
    font_sm = pygame.font.SysFont("consolas", 18)
    _tshadow(surface, font,    f"Score: {player.score}",         Amarillo, 12, 12)
    _tshadow(surface, font_sm, f"Length: {len(player.segments)}", Blanco,  12, 46)
    if player.boost: _tshadow(surface, font_sm, "BOOST", (255,160,0), 12, 68)

def draw_game_over(surface, players, names, mode):
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA); overlay.fill((0,0,0,170))
    surface.blit(overlay, (0,0))
    sw, sh = surface.get_size()
    font_big  = pygame.font.SysFont("consolas", 60, bold=True)
    font_med  = pygame.font.SysFont("consolas", 28)
    font_sm   = pygame.font.SysFont("consolas", 22)
    _tshadow(surface, font_big, "GAME OVER", Rojo, sw//2-180, sh//2-120)
    if mode == 'local':
        entries = sorted(enumerate(players), key=lambda x: -x[1].score)
        for rank, (i, p) in enumerate(entries):
            col = PLAYER_COLORS[i][0]
            txt = f"#{rank+1} {names[i]}: {p.score} pts"
            lbl = font_med.render(txt, True, col)
            surface.blit(lbl, (sw//2-lbl.get_width()//2, sh//2-40+rank*38))
    else:
        lbl = font_med.render(f"Score: {players[0].score}  Length: {len(players[0].segments)}", True, Blanco)
        surface.blit(lbl, (sw//2-lbl.get_width()//2, sh//2+10))
    hint = font_sm.render("R = reiniciar  •  ESC = menú", True, Gris_Claro)
    surface.blit(hint, (sw//2-hint.get_width()//2, sh//2+160))

def draw_leaderboard(surface, players, bots, names):
    entries = [(names[i], p.score, PLAYER_COLORS[i][0], p.alive) for i,p in enumerate(players)]
    for b in bots: entries.append((b.name, b.score, b.color, b.alive))
    entries.sort(key=lambda e: (0 if e[3] else 1, -e[1]))
    font = pygame.font.SysFont("consolas", 15, bold=True)
    pw = 200; rh = 32; pad = 8; ph = pad*2+24+len(entries)*rh
    px = surface.get_width()-pw-10; py0 = 180
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(panel, (8,8,20,210), (0,0,pw,ph), border_radius=12)
    pygame.draw.rect(panel, (90,80,160,200), (0,0,pw,ph), 2, border_radius=12)
    surface.blit(panel, (px, py0))
    title = font.render("★ RANKING", True, (210,190,255))
    surface.blit(title, (px+pw//2-title.get_width()//2, py0+pad))
    sep_y = py0+pad+20; pygame.draw.line(surface, (90,80,160), (px+6,sep_y),(px+pw-6,sep_y),1)
    for rank,(name,score,col,alive) in enumerate(entries):
        ry = sep_y+2+rank*rh
        c = col if alive else (50,50,50)
        pygame.draw.rect(surface, c, (px+4, ry+4, 4, rh-8), border_radius=2)
        mc = [(255,215,0),(192,192,192),(205,127,50),(120,120,120)][min(rank,3)]
        surface.blit(font.render(f"#{rank+1}", True, mc if alive else (60,60,60)), (px+12, ry+rh//2-8))
        disp = (name[:9]+"..") if len(name)>10 else name
        if not alive: disp = f"[{disp}]"
        surface.blit(font.render(disp, True, Blanco if alive else (70,70,70)), (px+46, ry+rh//2-8))
        sl = font.render(str(score), True, Amarillo if alive else (60,60,60))
        surface.blit(sl, (px+pw-sl.get_width()-8, ry+rh//2-8))

# ── MENU BG / UI ─────────────────────────────────────────────────────────────
_star_cache = None

def _build_stars(sw, sh):
    stars = []
    for _ in range(200):
        x=random.randint(0,sw); y=random.randint(0,sh); r=random.choice([1,1,2]); a=random.randint(80,255)
        col=random.choice([(255,255,255,a),(180,220,255,a),(255,200,100,a)])
        stars.append((x,y,r,col))
    return stars

def draw_menu_bg(surface, tick):
    global _star_cache
    sw, sh = surface.get_size(); surface.fill((5,5,16))
    for col,ex,ey,ew,eh in [
        ((168,85,247,28), sw*.05, sh*.15, sw*.65, sh*.55),
        ((0,229,255,16),  sw*.35, sh*.4,  sw*.65, sh*.5 ),
        ((255,77,172,14), sw*.2,  sh*.6,  sw*.55, sh*.45),
    ]:
        blob=pygame.Surface((sw,sh),pygame.SRCALPHA)
        pygame.draw.ellipse(blob,col,(int(ex),int(ey),int(ew),int(eh)))
        surface.blit(blob,(0,0))
    if _star_cache is None: _star_cache = _build_stars(sw,sh)
    for (x,y,r,col) in _star_cache:
        alpha=int(col[3]*(0.6+0.4*math.sin(tick*0.04+x*0.05)))
        s=pygame.Surface((r*2+1,r*2+1),pygame.SRCALPHA)
        pygame.draw.circle(s,(*col[:3],alpha),(r,r),r); surface.blit(s,(x-r,y-r))

def _outlined(font, text, color, outline=(0,0,0), thick=3):
    base=font.render(text,True,color); w=base.get_width()+thick*2; h=base.get_height()+thick*2
    surf=pygame.Surface((w,h),pygame.SRCALPHA)
    for dx in range(-thick,thick+1):
        for dy in range(-thick,thick+1):
            if dx*dx+dy*dy<=thick*thick+1:
                surf.blit(font.render(text,True,outline),(dx+thick,dy+thick))
    surf.blit(base,(thick,thick)); return surf

def _draw_logo(surface, tick):
    sw=surface.get_width()
    try: f=pygame.font.SysFont("broadway",72,bold=True)
    except: f=pygame.font.SysFont(None,72,bold=True)
    colors=[(255,77,172),(255,220,60),(255,107,53)]
    t_c=(tick%120)/120.0; idx=int(t_c*3)%3
    col=_lerp_color(colors[idx],colors[(idx+1)%3],(t_c*3)%1.0)
    lbl=_outlined(f,"slither.io",col,(0,0,0),5)
    surface.blit(lbl,(sw//2-lbl.get_width()//2,40))

def _draw_button(surface, rect, text, base_col, font, hovered):
    x,y,w,h=rect
    sh=pygame.Surface((w,h),pygame.SRCALPHA)
    pygame.draw.rect(sh,(0,0,0,110),(0,0,w,h),border_radius=h//2); surface.blit(sh,(x+5,y+8))
    col=_lerp_color(base_col,(255,255,255),0.2) if hovered else base_col
    pygame.draw.rect(surface,col,rect,border_radius=h//2)
    gl=pygame.Surface((w,h//2),pygame.SRCALPHA); gl.fill((255,255,255,32)); surface.blit(gl,(x,y))
    pygame.draw.rect(surface,_lerp_color(base_col,(255,255,255),0.55),rect,2,border_radius=h//2)
    lbl=_outlined(font,text,Blanco,(0,0,0),2)
    surface.blit(lbl,(x+w//2-lbl.get_width()//2,y+h//2-lbl.get_height()//2))

# ── MENÚS ────────────────────────────────────────────────────────────────────
def menu_main(screen):
    global _star_cache; _star_cache = None
    sw, sh = screen.get_size(); clock = pygame.time.Clock()
    try: f_btn=pygame.font.SysFont("broadway",32,bold=True)
    except: f_btn=pygame.font.SysFont(None,38)
    cx=sw//2; bw=300; bh=58; sy0=sh//2-60
    btns=[
        (pygame.Rect(cx-bw//2, sy0,       bw,bh), "JUGAR",   (22,130,210)),
        (pygame.Rect(cx-bw//2, sy0+80,    bw,bh), "OPCIONES",(0,180,220)),
        (pygame.Rect(cx-bw//2, sy0+160,   bw,bh), "SALIR",   (220,60,60)),
    ]
    tick=0
    while True:
        mx,my=pygame.mouse.get_pos(); tick+=1
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if btns[0][0].collidepoint(mx,my): return 'play'
                if btns[1][0].collidepoint(mx,my): return 'options'
                if btns[2][0].collidepoint(mx,my): pygame.quit(); sys.exit()
        draw_menu_bg(screen,tick); _draw_logo(screen,tick)
        for rect,label,col in btns:
            _draw_button(screen,rect,label,col,f_btn,rect.collidepoint(mx,my))
        pygame.display.flip(); clock.tick(60)

def menu_setup(screen):
    """Configurar número de jugadores y modo."""
    global _star_cache; _star_cache = None
    sw, sh = screen.get_size(); clock = pygame.time.Clock()
    try:
        f_title=pygame.font.SysFont("broadway",42,bold=True)
        f_btn=pygame.font.SysFont("broadway",28,bold=True)
        f_sm=pygame.font.SysFont("consolas",16)
    except:
        f_title=pygame.font.SysFont(None,48); f_btn=pygame.font.SysFont(None,34); f_sm=pygame.font.SysFont(None,20)

    cx=sw//2; bw=260; bh=50
    num_players=1
    btn_minus =pygame.Rect(cx-160, sh//2-110, 54, 50)
    btn_plus  =pygame.Rect(cx+106, sh//2-110, 54, 50)
    btn_local =pygame.Rect(cx-bw//2, sh//2-20,  bw, bh)
    btn_ai    =pygame.Rect(cx-bw//2, sh//2+42,  bw, bh)
    btn_back  =pygame.Rect(cx-bw//2, sh//2+106, bw, bh)
    # Botones skin por jugador (pequeños)
    sk_r=22; sk_gap=10
    skin_btn_y = sh//2+175

    tick=0
    while True:
        mx,my=pygame.mouse.get_pos(); tick+=1
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if btn_minus.collidepoint(mx,my) and num_players>1: num_players-=1
                if btn_plus.collidepoint(mx,my)  and num_players<4: num_players+=1
                if btn_local.collidepoint(mx,my): return num_players,'local'
                if btn_ai.collidepoint(mx,my):    return 1,'ai'
                if btn_back.collidepoint(mx,my):  return None,None
                # click en icono skin => abrir menu_skins para ese jugador
                total_sk_w = num_players*(sk_r*2+sk_gap)-sk_gap
                sk_start_x = cx - total_sk_w//2 + sk_r
                for i in range(num_players):
                    scx = sk_start_x + i*(sk_r*2+sk_gap)
                    if math.hypot(mx-scx, my-skin_btn_y) < sk_r+6:
                        menu_skins(screen, i)
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return None,None

        draw_menu_bg(screen,tick); _draw_logo(screen,tick)
        title=_outlined(f_title,"NUEVA PARTIDA",(160,220,255),(0,0,0),3)
        screen.blit(title,(cx-title.get_width()//2,sh//4-10))

        # Selector jugadores
        lbl=_outlined(f_title,f"JUGADORES: {num_players}",(255,220,100),(0,0,0),3)
        screen.blit(lbl,(cx-lbl.get_width()//2, sh//2-160))
        _draw_button(screen,btn_minus,"−",(60,60,120),f_btn,btn_minus.collidepoint(mx,my))
        _draw_button(screen,btn_plus, "+",(60,120,60),f_btn,btn_plus.collidepoint(mx,my))

        mode_note=_outlined(f_sm,"IA = 1 jugador vs bots | LOCAL = hasta 4P",(150,150,150),(0,0,0),1)
        screen.blit(mode_note,(cx-mode_note.get_width()//2,sh//2-52))

        _draw_button(screen,btn_local,f"LOCAL ({num_players}P)",(22,130,210),f_btn,btn_local.collidepoint(mx,my))
        _draw_button(screen,btn_ai,"CONTRA IA",(195,65,25),f_btn,btn_ai.collidepoint(mx,my))
        _draw_button(screen,btn_back,"VOLVER",(80,80,80),f_btn,btn_back.collidepoint(mx,my))

        # Previews de skins + etiqueta "SKINS"
        sk_lbl=_outlined(f_sm,"SKINS (clic para cambiar)",Blanco,(0,0,0),1)
        screen.blit(sk_lbl,(cx-sk_lbl.get_width()//2, skin_btn_y-sk_r-sk_lbl.get_height()-4))
        total_sk_w = num_players*(sk_r*2+sk_gap)-sk_gap
        sk_start_x = cx - total_sk_w//2 + sk_r
        for i in range(num_players):
            scx = sk_start_x + i*(sk_r*2+sk_gap)
            hovered = math.hypot(mx-scx,my-skin_btn_y)<sk_r+6
            if hovered: pygame.draw.circle(screen,(255,255,255),(scx,skin_btn_y),sk_r+7,2)
            _draw_skin_circle(screen,scx,skin_btn_y,sk_r,PLAYER_SKINS[i])
            pcol=PLAYER_COLORS[i][0]
            nl=_outlined(f_sm,f"P{i+1}",pcol,(0,0,0),1)
            screen.blit(nl,(scx-nl.get_width()//2,skin_btn_y+sk_r+3))

        pygame.display.flip(); clock.tick(60)

def menu_options(screen):
    global _star_cache; _star_cache=None
    sw,sh=screen.get_size(); clock=pygame.time.Clock()
    try: f_btn=pygame.font.SysFont("broadway",26,bold=True); f_t=pygame.font.SysFont("broadway",42,bold=True)
    except: f_btn=pygame.font.SysFont(None,32); f_t=pygame.font.SysFont(None,48)
    cx=sw//2; RESOLUTIONS=[(800,600),(1280,720),(1920,1080)]
    res_btns=[(pygame.Rect(cx-210+i*140, sh//2-60, 130, 44), r) for i,r in enumerate(RESOLUTIONS)]
    current_res=list(screen.get_size())
    btn_back=pygame.Rect(cx-120,sh-80,240,50); tick=0
    while True:
        mx,my=pygame.mouse.get_pos(); tick+=1
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                for rect,res in res_btns:
                    if rect.collidepoint(mx,my): current_res=list(res)
                if btn_back.collidepoint(mx,my): return tuple(current_res)
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return tuple(current_res)
        draw_menu_bg(screen,tick); _draw_logo(screen,tick)
        title=_outlined(f_t,"OPCIONES",(160,220,255),(0,0,0),3)
        screen.blit(title,(cx-title.get_width()//2,sh//4))
        for rect,res in res_btns:
            sel=tuple(current_res)==res
            _draw_button(screen,rect,f"{res[0]}x{res[1]}",(80,160,80) if sel else (60,60,90),f_btn,rect.collidepoint(mx,my))
        _draw_button(screen,btn_back,"VOLVER",(80,80,80),f_btn,btn_back.collidepoint(mx,my))
        pygame.display.flip(); clock.tick(60)

# ── GAME LOOP ─────────────────────────────────────────────────────────────────
def run_game(screen, num_players, mode):
    clock = pygame.time.Clock(); sw, sh = screen.get_size()
    cam = Camera(sw, sh)

    def make_players():
        ps=[]
        for i in range(num_players):
            x=(Ancho//(num_players+1))*(i+1); y=Alto//2
            si=PLAYER_SKINS[i]; _,col,hcol,flag=SKINS[si]
            s=Snake(x,y,col,hcol); s.flag=flag; s.skin_idx=si
            ps.append(s)
        return ps

    def make_bots(n=3):
        bs=[]; bc=[(220,60,180),(150,20,120)]; bnames=["Cazador","Rondador","Evasivo"]
        bot_colors=[(220,60,180),(0,180,220),(255,180,0)]
        for i in range(n):
            x=random.randint(400,Ancho-400); y=random.randint(400,Alto-400)
            c=bot_colors[i%3]; hc=_darker(c,60)
            bs.append(Bot(x,y,c,hc,bnames[i%3]))
        return bs

    def make_food(n=100):
        return [Food() for _ in range(n)]

    players=make_players()
    bots=make_bots(3) if mode=='ai' else []
    food=make_food()
    names=PLAYER_NAMES[:num_players]
    game_over=False

    while True:
        keys=pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: return
                if event.key==pygame.K_r and game_over:
                    players=make_players(); bots=make_bots(3) if mode=='ai' else []
                    food=make_food(); game_over=False

        if not game_over:
            # Mover jugadores
            for i,p in enumerate(players):
                if not p.alive: continue
                cs=CONTROL_SCHEMES[i]
                if mode=='ai' and i==0:  # modo IA: mouse para P1
                    mx2,my2=pygame.mouse.get_pos(); p.aim_mouse(mx2,my2,cam)
                    p.boost=keys[pygame.K_SPACE]
                else:
                    if keys[cs['left']]:  p.turn('left')
                    if keys[cs['right']]: p.turn('right')
                    p.boost=keys[cs['boost']]
                p.move(); p.eat(food)

            # Mover bots
            for b in bots: b.update(food, players+bots)

            # Colisiones jugador vs bot
            for p in players:
                if not p.alive: continue
                for b in bots:
                    if b.alive and p.collides_with(b): p.alive=False; break

            # Colisiones jugadores entre sí
            for i,p in enumerate(players):
                if not p.alive: continue
                for j,q in enumerate(players):
                    if i!=j and q.alive and p.collides_with(q): p.alive=False; break

            # Colisiones bot vs jugador
            for b in bots:
                if not b.alive: continue
                for p in players:
                    if p.alive and b.collides_with(p): b.alive=False; break

            # Comida
            while len(food)<80: food.append(Food())
            for f in food: f.update()

            # Cámara: seguir jugador vivo (P1 en modo AI, votación en local)
            target=None
            for p in players:
                if p.alive: target=p; break
            if target is None and bots:
                for b in bots:
                    if b.alive: target=b; break
            if target: cam.follow(int(target.head[0]), int(target.head[1]))

            # Game over
            if mode=='ai' and not players[0].alive: game_over=True
            if mode=='local' and not any(p.alive for p in players): game_over=True

        # DRAW
        draw_mapa(screen, cam)
        for f in food: f.draw(screen, cam)
        for b in bots:
            if b.alive: b.draw(screen, cam)
        for p in players:
            if p.alive: p.draw(screen, cam)
        draw_border(screen, cam)

        if mode=='local':
            draw_hud_multi(screen, players, names)
            draw_leaderboard(screen, players, [], names)
        else:
            draw_hud_solo(screen, players[0], cam)
            draw_leaderboard(screen, players, bots, names)

        all_snakes=[p for p in players]+bots
        all_cols=[PLAYER_COLORS[i][0] for i in range(len(players))]+[b.color for b in bots]
        draw_minimap(screen, all_snakes, cam, all_cols)

        if game_over:
            draw_game_over(screen, players, names, mode)

        pygame.display.flip(); clock.tick(60)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    res=(1280,720)
    screen=pygame.display.set_mode(res)
    pygame.display.set_caption("slither.io")
    clock=pygame.time.Clock()

    while True:
        action=menu_main(screen)
        if action=='options':
            new_res=menu_options(screen)
            if new_res!=res:
                res=new_res; screen=pygame.display.set_mode(res)
        elif action=='play':
            num_players,mode=menu_setup(screen)
            if mode is None: continue
            if (screen.get_width(),screen.get_height())!=res:
                screen=pygame.display.set_mode(res)
