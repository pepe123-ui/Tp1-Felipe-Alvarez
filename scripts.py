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