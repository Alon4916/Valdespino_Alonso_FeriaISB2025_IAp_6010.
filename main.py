import pygame # pyright: ignore[reportMissingImports]
import sys
import webbrowser
from pathlib import Path

pygame.init()
pygame.mixer.init()

# ----------------- Config general -------------------
WIDTH, HEIGHT = 900, 560
TITLE = "LAUNCHER FERIA ISB 2025 - MI CARRRERA IDEAL"
FPS = 60
BG_COLOR = (18, 18, 24)

# Intenta cargar un sonido de clic si existe
CLICK_SOUND = None
if Path("assets/click.wav").exists():
    CLICK_SOUND = pygame.mixer.Sound("assets/click.wav")
    
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Montserrat", 26)
SMALL_FONT = pygame.font.SysFont("Montserrat", 20)
BIG_FONT = pygame.font.SysFont("Montserrat", 40, bold=True)

# ----------------- UTILIDADES -------------------
def play_click():
    if CLICK_SOUND:
        CLICK_SOUND.play()
        
def draw_text(surface, text, font, color, center):
    img = font.render(text, True, color)
    rect = img.get_rect(center=center)
    surface.blit(img, rect)

def load_image(path, size=None, falback_color=(60, 60, 80)):
    """Carga una imagen si existe. Si no, devuelve una Surface de color."""
    if Path(path).exists():
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    # Fallback
    surf = pygame.Surface(size if size else (160, 160), pygame.SRCALPHA)
    surf.fill(falback_color)
    pygame.draw.rect(surf, (100, 100, 140), surf.get_rect(), border_radius=16)
    return surf

# ----------------- Modelo de datos -------------------
Universidades = [
    {
        "nombre": "ITAM",
        "area": "Ingeniería",
        "url": "https://www.itam.mx/",
        "img": "assets/itam.png",
        "resumen": "El ITAM ofrece programas de ingeniería con un enfoque en innovación y tecnología."   
    },
    {
        "nombre": "TEC",
        "area": "Tecnologías de la Información",
        "url": "https://tec.mx/",
        "img": "assets/tec.png",
        "resumen": "El TEC es reconocido por sus programas en tecnologías de la información y desarrollo de software."
    },
    {
        "nombre": "Anahuac",
        "area": "Ingenieria y Computción",
        "url": "https://www.anahuac.mx/",
        "img": "assets/anahuac.png",
        "resumen": "La Universidad Anáhuac ofrece carreras en ingeniería y computación con un enfoque global."
    },          
]
#Pre-carga de imágenes (con fallback)
for u in Universidades:
    u["image"] = load_image(u["img"], size=(160, 160))

# ----------------- UI: Botón -------------------
class Button:
    def __init__(self, text, x, y, w, h, on_click, *,
                 bg=(45, 45, 60), fg=(240, 240, 250),
                 hover_bg=(70, 70, 90), hover_fg=(255, 255, 255)): 
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.on_click = on_click
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg
        self.hovered = False
    def draw(self, surface):
        color_bg = self.hover_bg if self.hovered else self.bg
        color_fg = self.hover_fg if self.hovered else self.fg
        pygame.draw.rect(surface, color_bg, self.rect, border_radius=8)
        draw_text(surface, self.text, FONT, color_fg, self.rect.center)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                play_click()
                self.on_click()
        
# ----------------- Pantallas -------------------
class Scene:
    def handle(self, event): ...
    def update(self, dt): ...
    def draw(self, surf): ...

class Splash(Scene):
    def __init__(self, next_scene_callback):
        self.time = 0
        self.duration = 1.8 # seg
        self.next_scene_callback = next_scene_callback
        self.logo = load_image("assets/isb.png", size=(220, 220), fallback_color=(30, 30, 50))

    def update(self, dt):
        self.time += dt
        if self.time >= self.duration:
            self.next_scene_callback(Menu())

    def draw(self, surf):
        surf.fill(BG_COLOR)
        draw_text(surf, "Feria de Universidades ISB 2025",BIG_FONT, (230, 230, 245), (WIDTH//2, 70))
        # Efecto de aparición
        alpha = min(255, int(255 * (self.time / self.duration)))
        logo = self.logo.copy()
        logo.set_alpha(alpha)
        surf.blit(logo, logo.get_rect(center=(WIDTH//2, HEIGHT//2)))
        
        draw_text(surf, "Cargando launcher...",SMALL_FONT, (190, 190, 210), (WIDTH//2, HEIGHT - 40))

class Menu(Scene):
    def __init__(self):
        self.buttons = []
        self.title_y = 36
        padding_x = 60
        y = 120
        w, h, gap = 240, 60, 18

        # Botones dinámicos por universidad
        self.card_rects = []
        start_x = 60
        for i, u in enumerate(Universidades):
            rect = pygame.Rect(start_x + i * 280, 130, 260, 300)
            self.card_rects.append((rect, u))

        # Botones inferiores
        self.buttons.append(Button("Acerca de", padding_x, HEIGHT-80, w, h,
            lambda: set_scene(InfoScreen( # pyright: ignore[reportUndefinedVariable]
                title="Acerca del Launcher",
                body=("Este launcher es una base en Pygame.\n"
                      "Selecciona una universidad para ver detalles\n"
                      "y abre su sitio oficial."),
                url=None
            ))))
        self.buttons.append(Button("Salir", WIDTH - padding_x - w, HEIGHT-80, w, h,
            lambda: sys.exit(0)))

    def handle(self, event):
        for b in self.buttons:
            b.handle(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            #Click sobre tarjeta de universidad
            for rect, u in self.card_rects:
                if rect.collidepoint(event.pos):
                    set_scene(Detail(u))
                break
            
    def update(self, dt): ...
    
    def draw(self, surf):
        surf.fill(BG_COLOR)
        draw_text
        
        for rect, u in self.card_rects:
            pygame.draw.rect(surf, (34, 34, 46), rect, border_radius=16)
            pygame.draw.rect(surf, (90, 90, 130), rect, width=2, border_radius=16)
            # Imagen/logo
            img_rect = u["image_surf"].get_rect(center=(rect.centerx, rect.y + 95))
            surf.blitu(u["image surf"], img_rect)