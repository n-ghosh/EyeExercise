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

# --- UI Constants ---
SLIDER_X = 20
SLIDER_WIDTH = 240
SLIDER_HEIGHT = 30
SLIDER_KNOB_RADIUS_OFFSET = 2
SLIDER_BAR_HEIGHT = 6
SLIDER_BAR_OFFSET = 10
SLIDER_LABEL_OFFSET_Y = 30

TOGGLE_BTN_X = 0
TOGGLE_BTN_Y = 0
TOGGLE_BTN_WIDTH = 120
TOGGLE_BTN_HEIGHT = 40
TOGGLE_BTN_ICON_LEFT = 8
TOGGLE_BTN_LABEL_LEFT = 6

PATTERN_LABEL_X = 20
PATTERN_LABEL_Y = 300
PATTERN_DROPDOWN_X = 20
PATTERN_DROPDOWN_Y = 330
PATTERN_DROPDOWN_WIDTH = 240
PATTERN_DROPDOWN_HEIGHT = 30
PATTERN_OPTION_HEIGHT = 30

# --- Slider Ranges ---
SIZE_MIN = 10
SIZE_MAX = 100
SPEED_MIN = 20
SPEED_MAX = 400

# --- Sidebar Padding ---
SIDEBAR_PADDING = 20

# --- Animation/Geometry ---
MOVEMENT_PADDING = 20
ANGLE_DIVISOR = 50
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
circle_radius = 10
circle_speed = 200
pattern_idx = 0
sidebar_open = True

# --- Slider/Dropdown UI ---
def draw_slider(x, y, w, h, min_val, max_val, value, label):
    pygame.draw.rect(screen, GRAY, (x, y, w, h), border_radius=6)
    # Slider bar
    bar_width = w - 2 * SLIDER_BAR_OFFSET
    pos = int((value - min_val) / (max_val - min_val) * bar_width) + x + SLIDER_BAR_OFFSET
    pygame.draw.rect(screen, BLUE, (x+SLIDER_BAR_OFFSET, y+h//2-SLIDER_BAR_HEIGHT//2, bar_width, SLIDER_BAR_HEIGHT), border_radius=SLIDER_BAR_HEIGHT//2)
    # Slider knob
    pygame.draw.circle(screen, RED, (pos, y+h//2), h//2-SLIDER_KNOB_RADIUS_OFFSET)
    # Label
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"{label}: {value:.0f}", True, BLACK)
    screen.blit(text, (x, y-SLIDER_LABEL_OFFSET_Y))
    return pos

def draw_dropdown(x, y, w, h, options, selected_idx, open_):
    font = pygame.font.SysFont(None, 24)
    pygame.draw.rect(screen, GRAY, (x, y, w, h), border_radius=6)
    text = font.render(options[selected_idx], True, BLACK)
    screen.blit(text, (x+SLIDER_BAR_OFFSET, y+5))
    pygame.draw.polygon(screen, BLACK, [(x+w-20, y+h//2-5), (x+w-10, y+h//2-5), (x+w-15, y+h//2+5)])
    if open_:
        for i, opt in enumerate(options):
            rect = pygame.Rect(x, y+(i+1)*h, w, h)
            pygame.draw.rect(screen, LIGHT_GRAY if i==selected_idx else GRAY, rect, border_radius=6)
            t = font.render(opt, True, BLACK)
            screen.blit(t, (x+SLIDER_BAR_OFFSET, y+(i+1)*h+5))
    return

def draw_toggle_button(x, y, w, h, is_open):
    pygame.draw.rect(screen, DARK_GRAY, (x, y, w, h), border_radius=8)
    font_icon = pygame.font.SysFont(None, 28)
    font_label = pygame.font.SysFont(None, 22, bold=True)
    # Icon
    icon = font_icon.render("\u25C0" if is_open else "\u25B6", True, WHITE)
    icon_rect = icon.get_rect(left=x+TOGGLE_BTN_ICON_LEFT, centery=y+h//2)
    screen.blit(icon, icon_rect)
    # Label
    label = font_label.render("Settings", True, WHITE)
    label_rect = label.get_rect(left=icon_rect.right+TOGGLE_BTN_LABEL_LEFT, centery=y+h//2)
    screen.blit(label, label_rect)

def draw_sidebar():
    # Sidebar background
    pygame.draw.rect(screen, SIDEBAR_BG, (0, 0, SIDEBAR_WIDTH, HEIGHT))
    pygame.draw.line(screen, GRAY, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, HEIGHT), 2)
    # Size slider
    draw_slider(SLIDER_X, 120, SLIDER_WIDTH, SLIDER_HEIGHT, SIZE_MIN, SIZE_MAX, circle_radius, "Size")
    # Speed slider
    draw_slider(SLIDER_X, 220, SLIDER_WIDTH, SLIDER_HEIGHT, SPEED_MIN, SPEED_MAX, circle_speed, "Speed")
    # Pattern dropdown
    font = pygame.font.SysFont(None, 22)
    screen.blit(font.render("Pattern", True, BLACK), (PATTERN_LABEL_X, PATTERN_LABEL_Y))
    draw_dropdown(PATTERN_DROPDOWN_X, PATTERN_DROPDOWN_Y, PATTERN_DROPDOWN_WIDTH, PATTERN_DROPDOWN_HEIGHT, PATTERNS, pattern_idx, dropdown_open)

# --- Movement Functions ---
def get_position(t, pattern, speed, radius):
    # Calculate center based on whether sidebar is open
    offset = SIDEBAR_WIDTH if sidebar_open else 0
    available_width = WIDTH - offset
    cx = offset + available_width // 2
    cy = HEIGHT // 2

    # Calculate max movement radii so the circle stays inside the screen
    max_rx = available_width // 2 - circle_radius - MOVEMENT_PADDING
    max_ry = cy - circle_radius - MOVEMENT_PADDING

    angle = (speed / ANGLE_DIVISOR) * t
    if pattern == "Circle":
        x = cx + max_ry * math.cos(angle)  # Using max_ry to keep circle within vertical bounds
        y = cy + max_ry * math.sin(angle)
    elif pattern == "Circle CCW":
        x = cx + max_ry * math.cos(-angle)
        y = cy + max_ry * math.sin(-angle)
    elif pattern == "Horizontal":
        x = cx + max_rx * math.sin(angle)
        y = cy
    elif pattern == "Vertical":
        x = cx
        y = cy + max_ry * math.sin(angle)
    elif pattern == "Diagonal":
        diag_r = min(max_rx, max_ry)
        x = cx + diag_r * math.sin(angle)
        y = cy + diag_r * math.sin(angle)
    elif pattern == "Diagonal 2":
        diag_r = min(max_rx, max_ry)
        x = cx + diag_r * math.sin(angle)
        y = cy - diag_r * math.sin(angle)
    elif pattern == "Figure-Eight":
        x = cx + max_rx * math.sin(angle)
        y = cy + max_ry * math.sin(angle) * math.cos(angle)
    elif pattern == "Figure-Eight 2":
        x = cx + max_rx * math.sin(-angle)
        y = cy + max_ry * math.sin(-angle) * math.cos(-angle)
    else:
        print("Unknown pattern:", pattern)
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
                if TOGGLE_BTN_X <= mx <= TOGGLE_BTN_X + TOGGLE_BTN_WIDTH and TOGGLE_BTN_Y <= my <= TOGGLE_BTN_Y + TOGGLE_BTN_HEIGHT:
                    sidebar_open = False
                    dropdown_open = False
                    continue
            else:
                if TOGGLE_BTN_X <= mx <= TOGGLE_BTN_X + TOGGLE_BTN_WIDTH and TOGGLE_BTN_Y <= my <= TOGGLE_BTN_Y + TOGGLE_BTN_HEIGHT:
                    sidebar_open = True
                    dropdown_open = False
                    continue
            # Only handle sidebar controls if sidebar is open
            if sidebar_open:
                # Size slider
                if SLIDER_X <= mx <= SLIDER_X + SLIDER_WIDTH and 120 <= my <= 120 + SLIDER_HEIGHT:
                    slider_drag = 'size'
                # Speed slider
                elif SLIDER_X <= mx <= SLIDER_X + SLIDER_WIDTH and 220 <= my <= 220 + SLIDER_HEIGHT:
                    slider_drag = 'speed'
                # Dropdown
                elif PATTERN_DROPDOWN_X <= mx <= PATTERN_DROPDOWN_X + PATTERN_DROPDOWN_WIDTH and PATTERN_DROPDOWN_Y <= my <= PATTERN_DROPDOWN_Y + PATTERN_DROPDOWN_HEIGHT:
                    dropdown_open = not dropdown_open
                elif dropdown_open and PATTERN_DROPDOWN_X <= mx <= PATTERN_DROPDOWN_X + PATTERN_DROPDOWN_WIDTH and PATTERN_DROPDOWN_Y + PATTERN_DROPDOWN_HEIGHT < my <= PATTERN_DROPDOWN_Y + PATTERN_DROPDOWN_HEIGHT + len(PATTERNS) * PATTERN_OPTION_HEIGHT:
                    idx = (my - (PATTERN_DROPDOWN_Y + PATTERN_DROPDOWN_HEIGHT)) // PATTERN_OPTION_HEIGHT
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
                circle_radius = max(SIZE_MIN, min(SIZE_MAX, (mx - SLIDER_X) * (SIZE_MAX - SIZE_MIN) / SLIDER_WIDTH))
            elif slider_drag == 'speed':
                circle_speed = max(SPEED_MIN, min(SPEED_MAX, (mx - SLIDER_X) * (SPEED_MAX - SPEED_MIN) / SLIDER_WIDTH))

    # Draw background
    screen.fill(WHITE)

    # Draw moving circle
    x, y = get_position(t, PATTERNS[pattern_idx], circle_speed, circle_radius)
    pygame.draw.circle(screen, BLUE, (x, y), int(circle_radius))

    # Draw sidebar if open
    if sidebar_open:
        draw_sidebar()
    # Draw toggle button in top-left corner, with 'Settings' inside
    draw_toggle_button(TOGGLE_BTN_X, TOGGLE_BTN_Y, TOGGLE_BTN_WIDTH, TOGGLE_BTN_HEIGHT, sidebar_open)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()