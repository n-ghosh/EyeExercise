"""
Eye Pursuit Game (Part of Eye Exercise Series)

A simple interactive game for visual tracking practice. The user controls:
- Object size (slider)
- Movement speed (slider)
- Movement pattern (dropdown: circle, horizontal, vertical, diagonal, figure-eight)

The object moves smoothly along the selected path. Designed for visual/oculomotor training.
"""

import pygame
import math

# --- Config ---
WIDTH, HEIGHT = 1400, 800
FPS = 600
SIDEBAR_WIDTH = 280

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)
BLUE = (100, 180, 255)
RED = (255, 100, 100)
SIDEBAR_BG = (245, 245, 245)

# --- Movement Patterns ---
PATTERNS = [
    "Circle",
    "Circle CCW",
    "Horizontal",
    "Vertical",
    "Diagonal",
    "Diagonal 2",
    "Figure-Eight",
    "Figure-Eight 2",
]
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Eye Pursuit")
clock = pygame.time.Clock()

# --- Control State ---
circle_radius = 40
circle_speed = 150
pattern_idx = 0
sidebar_open = True

# --- Slider/Dropdown UI ---
def draw_slider(x, y, w, h, min_val, max_val, value, label):
    pygame.draw.rect(screen, GRAY, (x, y, w, h), border_radius=6)
    # Slider bar
    pos = int((value - min_val) / (max_val - min_val) * (w - 20)) + x + 10
    pygame.draw.rect(screen, BLUE, (x+10, y+h//2-3, w-20, 6), border_radius=3)
    # Slider knob
    pygame.draw.circle(screen, RED, (pos, y+h//2), h//2-2)
    # Label
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"{label}: {value:.0f}", True, BLACK)
    screen.blit(text, (x, y-30))
    return pos

def draw_dropdown(x, y, w, h, options, selected_idx, open_):
    font = pygame.font.SysFont(None, 24)
    pygame.draw.rect(screen, GRAY, (x, y, w, h), border_radius=6)
    text = font.render(options[selected_idx], True, BLACK)
    screen.blit(text, (x+10, y+5))
    pygame.draw.polygon(screen, BLACK, [(x+w-20, y+h//2-5), (x+w-10, y+h//2-5), (x+w-15, y+h//2+5)])
    if open_:
        for i, opt in enumerate(options):
            rect = pygame.Rect(x, y+(i+1)*h, w, h)
            pygame.draw.rect(screen, LIGHT_GRAY if i==selected_idx else GRAY, rect, border_radius=6)
            t = font.render(opt, True, BLACK)
            screen.blit(t, (x+10, y+(i+1)*h+5))
    return

def draw_toggle_button(x, y, w, h, is_open):
    pygame.draw.rect(screen, DARK_GRAY, (x, y, w, h), border_radius=8)
    font_icon = pygame.font.SysFont(None, 28)
    font_label = pygame.font.SysFont(None, 22, bold=True)
    # Icon
    icon = font_icon.render("◀" if is_open else "▶", True, WHITE)
    icon_rect = icon.get_rect(left=x+8, centery=y+h//2)
    screen.blit(icon, icon_rect)
    # Label
    label = font_label.render("Settings", True, WHITE)
    label_rect = label.get_rect(left=icon_rect.right+6, centery=y+h//2)
    screen.blit(label, label_rect)

def draw_sidebar():
    # Sidebar background
    pygame.draw.rect(screen, SIDEBAR_BG, (0, 0, SIDEBAR_WIDTH, HEIGHT))
    pygame.draw.line(screen, GRAY, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, HEIGHT), 2)
    # Size slider
    draw_slider(20, 120, 240, 30, 10, 100, circle_radius, "Size")
    # Speed slider
    draw_slider(20, 220, 240, 30, 20, 400, circle_speed, "Speed")
    # Pattern dropdown
    font = pygame.font.SysFont(None, 22)
    screen.blit(font.render("Pattern", True, BLACK), (20, 300))
    draw_dropdown(20, 330, 240, 30, PATTERNS, pattern_idx, dropdown_open)

# --- Movement Functions ---
def get_position(t, pattern, speed, radius):
    # Calculate center based on whether sidebar is open
    offset = SIDEBAR_WIDTH if sidebar_open else 0
    available_width = WIDTH - offset
    cx = offset + available_width // 2
    cy = HEIGHT // 2
    
    # Calculate max movement radii so the circle stays inside the screen
    max_rx = available_width // 2 - circle_radius - 20
    max_ry = cy - circle_radius - 20
    
    if pattern == "Circle":
        angle = (speed/100) * t
        x = cx + max_ry * math.cos(angle) # Using max_ry to keep circle within vertical bounds
        y = cy + max_ry * math.sin(angle)
    elif pattern == "Circle CCW":
        angle = -(speed / 100) * t
        x = cx + max_ry * math.cos(angle)
        y = cy + max_ry * math.sin(angle)
    elif pattern == "Horizontal":
        x = cx + (max_rx) * math.sin((speed/100)*t)
        y = cy
    elif pattern == "Vertical":
        x = cx
        y = cy + (max_ry) * math.sin((speed/100)*t)
    elif pattern == "Diagonal":
        diag_r = min(max_rx, max_ry)
        x = cx + diag_r * math.sin((speed/100)*t)
        y = cy + diag_r * math.sin((speed/100)*t)
    elif pattern == "Diagonal 2":
        diag_r = min(max_rx, max_ry)
        x = cx + diag_r * math.sin((speed / 100) * t)
        y = cy - diag_r * math.sin((speed / 100) * t)
    elif pattern == "Figure-Eight":
        angle = (speed/100) * t
        x = cx + max_rx * math.sin(angle)
        y = cy + max_ry * math.sin(angle) * math.cos(angle)
    elif pattern == "Figure-Eight 2":
        angle = -(speed / 100) * t
        x = cx + max_rx * math.sin(angle)
        y = cy + max_ry * math.sin(angle) * math.cos(angle)
    else:
        x, y = cx, cy
    return int(x), int(y)

# --- Main Loop ---
slider_drag = None  # None, 'size', or 'speed'
dropdown_open = False
running = True
start_ticks = pygame.time.get_ticks()

while running:
    dt = clock.tick(FPS) / 10000
    t = (pygame.time.get_ticks() - start_ticks) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Toggle button (in top-left corner)
            if sidebar_open:
                if 0 <= mx <= 120 and 0 <= my <= 40:
                    sidebar_open = False
                    dropdown_open = False
                    continue
            else:
                if 0 <= mx <= 120 and 0 <= my <= 40:
                    sidebar_open = True
                    dropdown_open = False
                    continue
            # Only handle sidebar controls if sidebar is open
            if sidebar_open:
                # Size slider
                if 20 <= mx <= 260 and 120 <= my <= 150:
                    slider_drag = 'size'
                # Speed slider
                elif 20 <= mx <= 260 and 220 <= my <= 250:
                    slider_drag = 'speed'
                # Dropdown
                elif 20 <= mx <= 260 and 330 <= my <= 360:
                    dropdown_open = not dropdown_open
                elif dropdown_open and 20 <= mx <= 260 and 360 < my <= 360+len(PATTERNS)*30:
                    idx = (my-360)//30
                    if 0 <= idx < len(PATTERNS):
                        pattern_idx = idx
                    dropdown_open = False
                else:
                    dropdown_open = False
            else:
                dropdown_open = False
                
        elif event.type == pygame.MOUSEBUTTONUP:
            slider_drag = None
        elif event.type == pygame.MOUSEMOTION and slider_drag and sidebar_open:
            mx, my = event.pos
            if slider_drag == 'size':
                # Map mouse x to size
                circle_radius = max(10, min(100, (mx-20)*0.375))
            elif slider_drag == 'speed':
                circle_speed = max(20, min(400, (mx-20)*1.583))

    # Draw background
    screen.fill(WHITE)

    # Draw moving circle
    x, y = get_position(t, PATTERNS[pattern_idx], circle_speed, circle_radius)
    pygame.draw.circle(screen, BLUE, (x, y), int(circle_radius))

    # Draw sidebar if open
    if sidebar_open:
        draw_sidebar()
    # Draw toggle button in top-left corner, with 'Settings' inside
    if sidebar_open:
        draw_toggle_button(0, 0, 120, 40, True)
    else:
        draw_toggle_button(0, 0, 120, 40, False)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()