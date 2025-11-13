import pygame  # pyright: ignore[reportMissingImports]
import sys
import webbrowser
from pathlib import Path

pygame.init()
pygame.mixer.init()

# ----------------- Config general -------------------
WIDTH, HEIGHT = 900, 560
TITLE = "LAUNCHER FERIA ISB 2025 - MI CARRERA IDEAL"
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
FONT_SMALL = pygame.font.SysFont("Montserrat", 20)
FONT_BIG = pygame.font.SysFont("Montserrat", 40, bold=True)

# ----------------- UTILIDADES -------------------
def play_click():
    if CLICK_SOUND:
        CLICK_SOUND.play()

def draw_text(surface, text, font, color, center):
    img = font.render(text, True, color)
    rect = img.get_rect(center=center)
    surface.blit(img, rect)

def load_image(path, size=None, fallback_color=(60, 60, 80)):
    """Carga una imagen si existe. Si no, devuelve una Surface de color."""
    if Path(path).exists():
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    # Fallback
    surf = pygame.Surface(size if size else (160, 160), pygame.SRCALPHA)
    surf.fill(fallback_color)
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
        "url": "https://tec.mx/es/profesional?utm_campaign=PECA&utm_source=google&utm_medium=search&utm_content=Profe_26_PECA_Texto_NA_GENERAL&utm_cve_periodo_iniciativa=202613&utm_cve_sede_iniciativa=NAL&PAUTA=/1&gclsrc=aw.ds&gad_source=1",
        "img": "assets/tec.png",
        "resumen": "El TEC es reconocido por sus programas en tecnologías de la información y desarrollo de software."
    },
    {
        "nombre": "Anahuac",
        "area": "Ingeniería y Computación",
        "url": "https://www.anahuac.mx/",
        "img": "assets/anahuac.png",
        "resumen": "La Universidad Anáhuac ofrece carreras en ingeniería y computación con un enfoque global."
    }
]

# Pre-carga de imágenes (con fallback)
for u in Universidades:
    u["image_surf"] = load_image(u["img"], size=(160, 160))

# ----------------- Botón reutilizable -------------------
class Button:
    def __init__(self, text, x, y, w, h, on_click, bg=(40, 40, 60), fg=(240, 240, 250),
                 hover_bg=(60, 60, 90), hover_fg=(255, 255, 255)):
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

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                play_click()
                if callable(self.on_click):
                    self.on_click()

# ----------------- Pantallas -------------------
class Scene:
    def handle(self, event): ...
    def update(self, dt): ...
    def draw(self, surf): ...

class Splash(Scene):
    def __init__(self, next_scene_callback):
        self.time = 0
        self.duration = 1.8  # seg
        self.next_scene_callback = next_scene_callback
        self.logo = load_image("assets/isb.png", size=(220, 220), fallback_color=(30, 30, 50))

    def update(self, dt):
        self.time += dt
        if self.time >= self.duration:
            self.next_scene_callback(Menu())

    def draw(self, surf):
        surf.fill(BG_COLOR)
        draw_text(surf, "Feria de Universidades ISB 2025", FONT_BIG, (230, 230, 245), (WIDTH // 2, 70))
        alpha = min(255, int(255 * (self.time / self.duration)))
        logo = self.logo.copy()
        logo.set_alpha(alpha)
        surf.blit(logo, logo.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        draw_text(surf, "Cargando launcher...", FONT_SMALL, (190, 190, 210), (WIDTH // 2, HEIGHT - 40))

class Menu(Scene):
    def __init__(self):
        self.buttons = []
        padding_x = 60
        w, h = 240, 60

        self.card_rects = []
        start_x = 60
        for i, u in enumerate(Universidades):
            rect = pygame.Rect(start_x + i * 280, 130, 260, 300)
            self.card_rects.append((rect, u))

        self.buttons.append(Button(
            "Acerca de", padding_x, HEIGHT - 80, w, h,
            lambda: set_scene(InfoScreen(
                title="Acerca del Launcher",
                body=("Este launcher es una base en Pygame.\n"
                      "Selecciona una universidad para ver detalles\n"
                      "y abre su sitio oficial."),
                url=None
            ))
        ))
        self.buttons.append(Button(
            "Salir", WIDTH - padding_x - w, HEIGHT - 80, w, h,
            lambda: sys.exit(0)
        ))

    def handle(self, event):
        for b in self.buttons:
            b.handle(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, u in self.card_rects:
                if rect.collidepoint(event.pos):
                    set_scene(Detalle(u))
                    break

    def update(self, dt): ...

    def draw(self, surf):
        surf.fill(BG_COLOR)
        draw_text(surf, "Elige una opción para explorar", FONT_BIG, (235, 235, 245), (WIDTH // 2, 42))
        for rect, u in self.card_rects:
            pygame.draw.rect(surf, (34, 34, 46), rect, border_radius=16)
            pygame.draw.rect(surf, (90, 98, 130), rect, width=2, border_radius=16)
            img_rect = u["image_surf"].get_rect(center=(rect.centerx, rect.y + 95))
            surf.blit(u["image_surf"], img_rect)
            draw_text(surf, u["nombre"], FONT, (240, 240, 250), (rect.centerx, rect.y + 195))
            draw_text(surf, u["area"], FONT_SMALL, (200, 200, 220), (rect.centerx, rect.y + 230))
            btn = pygame.Rect(rect.centerx - 80, rect.y + 260, 160, 44)
            mouse_over = btn.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(surf, (70, 70, 110) if mouse_over else (50, 50, 85), btn, border_radius=10)
            draw_text(surf, "Ver más", FONT_SMALL, (240, 240, 250), btn.center)
        for b in self.buttons:
            b.draw(surf)

class Detalle(Scene):
    def __init__(self, data):
        self.data = data
        self.img = data["image_surf"]
        self.btn_back = Button("Regresar", 40, HEIGHT - 80, 280, 56, lambda: set_scene(Menu()))
        self.btn_open = Button("Abrir sitio oficial", WIDTH - 280, HEIGHT - 80, 240, 56, self.open_site)

    def open_site(self):
        play_click()
        webbrowser.open(self.data["url"], new=2)

    def handle(self, event):
        self.btn_back.handle(event)
        self.btn_open.handle(event)

    def update(self, dt): ...

    def draw(self, surf):
        surf.fill(BG_COLOR)
        draw_text(surf, f"{self.data['nombre']} - {self.data['area']}", FONT_BIG, (235, 235, 245), (WIDTH // 2, 42))
        card = pygame.Rect(68, 90, WIDTH - 120, 360)
        pygame.draw.rect(surf, (34, 34, 46), card, border_radius=16)
        pygame.draw.rect(surf, (90, 90, 130), card, width=2, border_radius=16)
        img_rect = self.img.get_rect(center=(card.x + 140, card.centery))
        surf.blit(self.img, img_rect)
        body = (f"Resumen: {self.data['resumen']}\n\n"
                f"Sitio oficial: {self.data['url']}\n"
                "Tip: investiga becas, requisitos y campo laboral.\n"
                "Tarea: agrega esta info a tu Google Sites en la sección Feria ISB.")
        draw_multiline_text(surf, body, FONT_SMALL, (220, 220, 235), (img_rect.right + 30, card.y + 30),
                            max_width=WIDTH - 120 - 220 - 160)
        self.btn_back.draw(surf)
        self.btn_open.draw(surf)

class InfoScreen(Scene):
    def __init__(self, title, body, url=None):
        self.title = title
        self.body = body
        self.url = url
        self.btn_back = Button("Regresar", 40, HEIGHT - 80, 200, 56, lambda: set_scene(Menu()))
        self.btn_open = Button("Abrir enlace", WIDTH - 260, HEIGHT - 80, 220, 56,
                               lambda: webbrowser.open(url, new=2)) if url else None

    def handle(self, event):
        self.btn_back.handle(event)
        if self.btn_open:
            self.btn_open.handle(event)

    def update(self, dt): ...

    def draw(self, surf):
        surf.fill(BG_COLOR)
        draw_text(surf, self.title, FONT_BIG, (235, 235, 245), (WIDTH // 2, 42))
        draw_multiline_text(surf, self.body, FONT_SMALL, (220, 220, 235), (70, 110), max_width=WIDTH - 140)
        self.btn_back.draw(surf)
        if self.btn_open:
            self.btn_open.draw(surf)

# --------------- Helper para texto multilinea ---------------
def draw_multiline_text(surf, text, font, color, topleft, max_width):
    x, y = topleft
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for w in words:
            test = line + w + " "
            if font.size(test)[0] < max_width:
                line = test
            else:
                line_surf = font.render(line, True, color)
                surf.blit(line_surf, (x, y))
                y += font.get_linesize()
                line = w + " "
        if line:
            line_surf = font.render(line, True, color)
            surf.blit(line_surf, (x, y))
            y += font.get_linesize() + 8  # extra espacio entre párrafos

# ---------------- Loop principal ----------------
current_scene = None
def set_scene(scene):
    global current_scene
    current_scene = scene

def main():
    set_scene(Splash(next_scene_callback=set_scene))
    while True:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if current_scene:
                current_scene.handle(event)
        if current_scene:
            current_scene.update(dt)
            current_scene.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()

    