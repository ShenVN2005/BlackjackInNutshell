import pygame
import os

CARD_WIDTH = 70
CARD_HEIGHT = 100
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

_image_cache = {}

def get_image(filename):
    if filename not in _image_cache:
        path = os.path.join(ASSETS_DIR, filename)
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
            _image_cache[filename] = img
        except FileNotFoundError:
            sur = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            sur.fill((255, 255, 255))
            _image_cache[filename] = sur
    return _image_cache[filename]

def draw_card(surface, font, x, y, val_str, hidden=False):
    if hidden or val_str == "HIDDEN":
        img = get_image("BackCard.png")
        surface.blit(img, (x, y))
        return
        
    img = get_image(val_str + ".png")
    surface.blit(img, (x, y))
    
    # Requirement: small 10 at the corner of J, Q, K
    if val_str.startswith('J') or val_str.startswith('Q') or val_str.startswith('K'):
        small_font = pygame.font.SysFont("Arial", 14, bold=True)
        color = (255, 0, 0) if "Co" in val_str or "Ro" in val_str else (0, 0, 0)
        text_surf = small_font.render("10", True, color)
        # Top-right corner pad 3px
        surface.blit(text_surf, (x + CARD_WIDTH - text_surf.get_width() - 3, y + 3))
