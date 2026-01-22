import pygame
import os

FONT_PATH = "res/fonts/msa/Ac437_TridentEarly_8x14.ttf"
SAVE_DIR = os.path.join("config", "live", "PyOS", "User", "Pictures", "PyPaint")

class PyPaintApp:
    def __init__(self):
        self.font = pygame.font.Font(FONT_PATH, 18)

        self.canvas = None
        self.canvas_rect = None

        self.drawing = False
        self.last_pos = None

        self.brush_color = (255, 255, 255)
        self.brush_size = 4

        self.tool = "brush"  # brush, eraser
        self.bg_color = (0, 0, 0)

        self.status = "PyPaint ready"
        self.needs_init = True

    def _init_canvas(self, surface):
        w, h = surface.get_size()
        self.canvas_rect = pygame.Rect(10, 50, w - 20, h - 60)
        self.canvas = pygame.Surface(self.canvas_rect.size)
        self.canvas.fill(self.bg_color)
        os.makedirs(SAVE_DIR, exist_ok=True)
        self.needs_init = False

    def update(self, surface, mouse_pos):
        if self.needs_init:
            self._init_canvas(surface)

        surface.fill((30, 30, 30))

        title = self.font.render("PyPaint", True, (255, 255, 255))
        surface.blit(title, (10, 10))

        # Toolbar
        toolbar_y = 10
        x = 120
        buttons = [
            ("Brush", "brush"),
            ("Eraser", "eraser"),
            ("- Size", "size_dec"),
            ("+ Size", "size_inc"),
            ("Save", "save"),
            ("Clear", "clear"),
        ]
        self.button_rects = []
        for label, action in buttons:
            rect = pygame.Rect(x, toolbar_y, 80, 30)
            pygame.draw.rect(surface, (60, 60, 60), rect)
            txt = self.font.render(label, True, (255, 255, 255))
            surface.blit(txt, (rect.x + 5, rect.y + 5))
            self.button_rects.append((rect, action))
            x += 90

        # Color palette
        colors = [
            (255, 255, 255),
            (0, 0, 0),
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (0, 255, 255),
            (255, 0, 255),
        ]
        self.color_rects = []
        cx = 10
        cy = surface.get_height() - 40
        for c in colors:
            rect = pygame.Rect(cx, cy, 30, 30)
            pygame.draw.rect(surface, c, rect)
            if c == self.brush_color:
                pygame.draw.rect(surface, (255, 255, 255), rect, 2)
            self.color_rects.append((rect, c))
            cx += 40

        # Canvas
        pygame.draw.rect(surface, (80, 80, 80), self.canvas_rect, 1)
        surface.blit(self.canvas, self.canvas_rect.topleft)

        # Status
        status_txt = self.font.render(self.status, True, (200, 200, 200))
        surface.blit(status_txt, (150, surface.get_height() - 35))

    def handle_event(self, event, rect):
        # rect is window rect; convert to local coords
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            local = (mx - rect.x, my - (rect.y + 30))

            # Toolbar buttons
            for brect, action in getattr(self, "button_rects", []):
                if brect.collidepoint(local):
                    self._handle_button(action)
                    return

            # Color palette
            for crect, color in getattr(self, "color_rects", []):
                if crect.collidepoint(local):
                    self.brush_color = color
                    self.status = f"Color set to {color}"
                    return

            # Canvas
            if self.canvas_rect and self.canvas_rect.collidepoint(local):
                self.drawing = True
                self.last_pos = (local[0] - self.canvas_rect.x,
                                 local[1] - self.canvas_rect.y)
                self._draw_point(self.last_pos)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drawing = False
            self.last_pos = None

        if event.type == pygame.MOUSEMOTION:
            if self.drawing and self.canvas_rect:
                mx, my = event.pos
                local = (mx - rect.x, my - (rect.y + 30))
                if self.canvas_rect.collidepoint(local):
                    pos = (local[0] - self.canvas_rect.x,
                           local[1] - self.canvas_rect.y)
                    self._draw_line(self.last_pos, pos)
                    self.last_pos = pos

    def _draw_point(self, pos):
        if self.tool == "brush":
            pygame.draw.circle(self.canvas, self.brush_color, pos, self.brush_size)
        elif self.tool == "eraser":
            pygame.draw.circle(self.canvas, self.bg_color, pos, self.brush_size)

    def _draw_line(self, start, end):
        if start is None:
            self._draw_point(end)
            return
        color = self.brush_color if self.tool == "brush" else self.bg_color
        pygame.draw.line(self.canvas, color, start, end, self.brush_size * 2)

    def _handle_button(self, action):
        if action == "brush":
            self.tool = "brush"
            self.status = "Tool: brush"
        elif action == "eraser":
            self.tool = "eraser"
            self.status = "Tool: eraser"
        elif action == "size_inc":
            self.brush_size = min(50, self.brush_size + 1)
            self.status = f"Brush size: {self.brush_size}"
        elif action == "size_dec":
            self.brush_size = max(1, self.brush_size - 1)
            self.status = f"Brush size: {self.brush_size}"
        elif action == "clear":
            self.canvas.fill(self.bg_color)
            self.status = "Canvas cleared"
        elif action == "save":
            self._save_image()

    def _save_image(self):
        os.makedirs(SAVE_DIR, exist_ok=True)
        i = 1
        while True:
            path = os.path.join(SAVE_DIR, f"pypaint_{i}.png")
            if not os.path.exists(path):
                break
            i += 1
        pygame.image.save(self.canvas, path)
        self.status = f"Saved to {path}"
