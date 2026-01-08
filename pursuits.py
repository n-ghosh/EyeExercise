"""
Eye Pursuit Game (Part of Eye Exercise Series)

A simple interactive game for visual tracking practice. The user controls:
- Object size (slider)
- Movement speed (slider)
- Movement pattern (dropdown: circle, horizontal, vertical, diagonal, figure-eight)

The object moves smoothly along the selected path. Designed for visual/oculomotor training.

Important constants are defined in constants.py for easy adjustments.
"""

import pygame
import math
import constants

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
screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
pygame.display.set_caption("Eye Pursuit")
clock = pygame.time.Clock()

# --- Control State ---
circle_radius = 10
circle_speed = 200
pattern_idx = 0
sidebar_open = True

# --- Slider/Dropdown UI ---
def draw_slider(x, y, w, h, min_val, max_val, value, label):
    pygame.draw.rect(screen, constants.GRAY, (x, y, w, h), border_radius=6)
    # Slider bar
    bar_width = w - 2 * constants.SLIDER_BAR_OFFSET
    pos = int((value - min_val) / (max_val - min_val) * bar_width) + x + constants.SLIDER_BAR_OFFSET
    pygame.draw.rect(screen, constants.BLUE, (x+constants.SLIDER_BAR_OFFSET, y+h//2-constants.SLIDER_BAR_HEIGHT//2, bar_width, constants.SLIDER_BAR_HEIGHT), border_radius=constants.SLIDER_BAR_HEIGHT//2)
    # Slider knob
    pygame.draw.circle(screen, constants.RED, (pos, y+h//2), h//2-constants.SLIDER_KNOB_RADIUS_OFFSET)
    # Label
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"{label}: {value:.0f}", True, constants.BLACK)
    screen.blit(text, (x, y-constants.SLIDER_LABEL_OFFSET_Y))
    return pos

def draw_dropdown(x, y, w, h, options, selected_idx, open_):
    font = pygame.font.SysFont(None, 24)
    pygame.draw.rect(screen, constants.GRAY, (x, y, w, h), border_radius=6)
    text = font.render(options[selected_idx], True, constants.BLACK)
    screen.blit(text, (x+constants.SLIDER_BAR_OFFSET, y+5))
    pygame.draw.polygon(screen, constants.BLACK, [(x+w-20, y+h//2-5), (x+w-10, y+h//2-5), (x+w-15, y+h//2+5)])
    if open_:
        for i, opt in enumerate(options):
            rect = pygame.Rect(x, y+(i+1)*h, w, h)
            pygame.draw.rect(screen, constants.LIGHT_GRAY if i==selected_idx else constants.GRAY, rect, border_radius=6)
            t = font.render(opt, True, constants.BLACK)
            screen.blit(t, (x+constants.SLIDER_BAR_OFFSET, y+(i+1)*h+5))
    return

def draw_toggle_button(x, y, w, h, is_open):
    pygame.draw.rect(screen, constants.DARK_GRAY, (x, y, w, h), border_radius=8)
    font_icon = pygame.font.SysFont(None, 28)
    font_label = pygame.font.SysFont(None, 22, bold=True)
    # Icon
    icon = font_icon.render("\u25C0" if is_open else "\u25B6", True, constants.WHITE)
    icon_rect = icon.get_rect(left=x+constants.TOGGLE_BTN_ICON_LEFT, centery=y+h//2)
    screen.blit(icon, icon_rect)
    # Label
    label = font_label.render("Settings", True, constants.WHITE)
    label_rect = label.get_rect(left=icon_rect.right+constants.TOGGLE_BTN_LABEL_LEFT, centery=y+h//2)
    screen.blit(label, label_rect)

def draw_sidebar():
    # Sidebar background
    pygame.draw.rect(screen, constants.SIDEBAR_BG, (0, 0, constants.SIDEBAR_WIDTH, constants.HEIGHT))
    pygame.draw.line(screen, constants.GRAY, (constants.SIDEBAR_WIDTH, 0), (constants.SIDEBAR_WIDTH, constants.HEIGHT), 2)
    # Size slider
    draw_slider(constants.SLIDER_X, 120, constants.SLIDER_WIDTH, constants.SLIDER_HEIGHT, constants.SIZE_MIN, constants.SIZE_MAX, circle_radius, "Size")
    # Speed slider
    draw_slider(constants.SLIDER_X, 220, constants.SLIDER_WIDTH, constants.SLIDER_HEIGHT, constants.SPEED_MIN, constants.SPEED_MAX, circle_speed, "Speed")
    # Pattern dropdown
    font = pygame.font.SysFont(None, 22)
    screen.blit(font.render("Pattern", True, constants.BLACK), (constants.PATTERN_LABEL_X, constants.PATTERN_LABEL_Y))
    draw_dropdown(constants.PATTERN_DROPDOWN_X, constants.PATTERN_DROPDOWN_Y, constants.PATTERN_DROPDOWN_WIDTH, constants.PATTERN_DROPDOWN_HEIGHT, PATTERNS, pattern_idx, dropdown_open)

# --- Movement Functions ---
def get_position(t, pattern, speed, radius):
    # Calculate center based on whether sidebar is open
    offset = constants.SIDEBAR_WIDTH if sidebar_open else 0
    available_width = constants.WIDTH - offset
    cx = offset + available_width // 2
    cy = constants.HEIGHT // 2

    # Calculate max movement radii so the circle stays inside the screen
    max_rx = available_width // 2 - circle_radius - constants.MOVEMENT_PADDING
    max_ry = cy - circle_radius - constants.MOVEMENT_PADDING

    angle = (speed / constants.ANGLE_DIVISOR) * t
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
    dt = clock.tick(constants.FPS) / 10000
    t = (pygame.time.get_ticks() - start_ticks) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Toggle button (in top-left corner)
            if sidebar_open:
                if constants.TOGGLE_BTN_X <= mx <= constants.TOGGLE_BTN_X + constants.TOGGLE_BTN_WIDTH and constants.TOGGLE_BTN_Y <= my <= constants.TOGGLE_BTN_Y + constants.TOGGLE_BTN_HEIGHT:
                    sidebar_open = False
                    dropdown_open = False
                    continue
            else:
                if constants.TOGGLE_BTN_X <= mx <= constants.TOGGLE_BTN_X + constants.TOGGLE_BTN_WIDTH and constants.TOGGLE_BTN_Y <= my <= constants.TOGGLE_BTN_Y + constants.TOGGLE_BTN_HEIGHT:
                    sidebar_open = True
                    dropdown_open = False
                    continue
            # Only handle sidebar controls if sidebar is open
            if sidebar_open:
                # Size slider
                if constants.SLIDER_X <= mx <= constants.SLIDER_X + constants.SLIDER_WIDTH and 120 <= my <= 120 + constants.SLIDER_HEIGHT:
                    slider_drag = 'size'
                # Speed slider
                elif constants.SLIDER_X <= mx <= constants.SLIDER_X + constants.SLIDER_WIDTH and 220 <= my <= 220 + constants.SLIDER_HEIGHT:
                    slider_drag = 'speed'
                # Dropdown
                elif constants.PATTERN_DROPDOWN_X <= mx <= constants.PATTERN_DROPDOWN_X + constants.PATTERN_DROPDOWN_WIDTH and constants.PATTERN_DROPDOWN_Y <= my <= constants.PATTERN_DROPDOWN_Y + constants.PATTERN_DROPDOWN_HEIGHT:
                    dropdown_open = not dropdown_open
                elif dropdown_open and constants.PATTERN_DROPDOWN_X <= mx <= constants.PATTERN_DROPDOWN_X + constants.PATTERN_DROPDOWN_WIDTH and constants.PATTERN_DROPDOWN_Y + constants.PATTERN_DROPDOWN_HEIGHT < my <= constants.PATTERN_DROPDOWN_Y + constants.PATTERN_DROPDOWN_HEIGHT + len(PATTERNS) * constants.PATTERN_OPTION_HEIGHT:
                    idx = (my - (constants.PATTERN_DROPDOWN_Y + constants.PATTERN_DROPDOWN_HEIGHT)) // constants.PATTERN_OPTION_HEIGHT
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
                circle_radius = max(constants.SIZE_MIN, min(constants.SIZE_MAX, (mx - constants.SLIDER_X) * (constants.SIZE_MAX - constants.SIZE_MIN) / constants.SLIDER_WIDTH))
            elif slider_drag == 'speed':
                circle_speed = max(constants.SPEED_MIN, min(constants.SPEED_MAX, (mx - constants.SLIDER_X) * (constants.SPEED_MAX - constants.SPEED_MIN) / constants.SLIDER_WIDTH))

    # Draw background
    screen.fill(constants.WHITE)

    # Draw moving circle
    x, y = get_position(t, PATTERNS[pattern_idx], circle_speed, circle_radius)
    pygame.draw.circle(screen, constants.BLUE, (x, y), int(circle_radius))
    # Draw sidebar if open
    if sidebar_open:
        draw_sidebar()
    # Draw toggle button in top-left corner, with 'Settings' inside
    draw_toggle_button(constants.TOGGLE_BTN_X, constants.TOGGLE_BTN_Y, constants.TOGGLE_BTN_WIDTH, constants.TOGGLE_BTN_HEIGHT, sidebar_open)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()