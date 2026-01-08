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
import constants as C

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
screen = pygame.display.set_mode((C.WIDTH, C.HEIGHT))
pygame.display.set_caption("Eye Pursuit")
clock = pygame.time.Clock()

# --- Control State ---
circle_radius = 10
circle_speed = 200
pattern_idx = 0
sidebar_open = True


# --- Slider/Dropdown UI ---
def draw_slider(x, y, w, h, min_val, max_val, value, label):
    pygame.draw.rect(screen, C.GRAY, (x, y, w, h), border_radius=6)
    # Slider bar
    bar_width = w - 2 * C.SL_BAR_OFFSET
    pos = int((value - min_val) / (max_val - min_val) * bar_width) + x + C.SL_BAR_OFFSET
    pygame.draw.rect(
        screen,
        C.BLUE,
        (
            x + C.SL_BAR_OFFSET,
            y + h // 2 - C.SL_BAR_HEIGHT // 2,
            bar_width,
            C.SL_BAR_HEIGHT,
        ),
        border_radius=C.SL_BAR_HEIGHT // 2,
    )
    # Slider knob
    pygame.draw.circle(
        screen, C.RED, (pos, y + h // 2), h // 2 - C.SL_KNOB_RADIUS_OFFSET
    )
    # Label
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"{label}: {value:.0f}", True, C.BLACK)
    screen.blit(text, (x, y - C.SL_LABEL_OFFSET_Y))
    return pos


def draw_dropdown(x, y, w, h, options, selected_idx, open_):
    font = pygame.font.SysFont(None, 24)
    pygame.draw.rect(screen, C.GRAY, (x, y, w, h), border_radius=6)
    text = font.render(options[selected_idx], True, C.BLACK)
    screen.blit(text, (x + C.SL_BAR_OFFSET, y + 5))
    pygame.draw.polygon(
        screen,
        C.BLACK,
        [
            (x + w - 20, y + h // 2 - 5),
            (x + w - 10, y + h // 2 - 5),
            (x + w - 15, y + h // 2 + 5),
        ],
    )
    if open_:
        for i, opt in enumerate(options):
            rect = pygame.Rect(x, y + (i + 1) * h, w, h)
            pygame.draw.rect(
                screen,
                C.LIGHT_GRAY if i == selected_idx else C.GRAY,
                rect,
                border_radius=6,
            )
            t = font.render(opt, True, C.BLACK)
            screen.blit(t, (x + C.SL_BAR_OFFSET, y + (i + 1) * h + 5))
    return


def draw_toggle_button(x, y, w, h, is_open):
    pygame.draw.rect(screen, C.DARK_GRAY, (x, y, w, h), border_radius=8)
    font_icon = pygame.font.SysFont(None, 28)
    font_label = pygame.font.SysFont(None, 22, bold=True)
    # Icon
    icon = font_icon.render("\u25c0" if is_open else "\u25b6", True, C.WHITE)
    icon_rect = icon.get_rect(left=x + C.TG_ICON_LEFT, centery=y + h // 2)
    screen.blit(icon, icon_rect)
    # Label
    label = font_label.render("Settings", True, C.WHITE)
    label_rect = label.get_rect(
        left=icon_rect.right + C.TG_LABEL_LEFT, centery=y + h // 2
    )
    screen.blit(label, label_rect)


def draw_sidebar():
    # Sidebar background
    pygame.draw.rect(screen, C.SIDEBAR_BG, (0, 0, C.SIDEBAR_WIDTH, C.HEIGHT))
    pygame.draw.line(
        screen, C.GRAY, (C.SIDEBAR_WIDTH, 0), (C.SIDEBAR_WIDTH, C.HEIGHT), 2
    )
    # Size slider
    draw_slider(
        C.SL_X, 120, C.SL_W, C.SL_H, C.SIZE_MIN, C.SIZE_MAX, circle_radius, "Size"
    )
    # Speed slider
    draw_slider(
        C.SL_X, 220, C.SL_W, C.SL_H, C.SPEED_MIN, C.SPEED_MAX, circle_speed, "Speed"
    )
    # Pattern dropdown
    font = pygame.font.SysFont(None, 22)
    screen.blit(font.render("Pattern", True, C.BLACK), (C.PT_LABEL_X, C.PT_LABEL_Y))
    draw_dropdown(C.PT_X, C.PT_Y, C.PT_W, C.PT_H, PATTERNS, pattern_idx, dropdown_open)


# --- Movement Functions ---
def get_position(t, pattern, speed, radius):
    # Calculate center based on whether sidebar is open
    offset = C.SIDEBAR_WIDTH if sidebar_open else 0
    available_width = C.WIDTH - offset
    cx = offset + available_width // 2
    cy = C.HEIGHT // 2

    # Calculate max movement radii so the circle stays inside the screen
    max_rx = available_width // 2 - circle_radius - C.MOVEMENT_PADDING
    max_ry = cy - circle_radius - C.MOVEMENT_PADDING

    angle = (speed / C.ANGLE_DIVISOR) * t
    if pattern == "Circle":
        # Using max_ry to keep circle within vertical bounds
        x = cx + max_ry * math.cos(angle)
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
    dt = clock.tick(C.FPS) / 10000
    t = (pygame.time.get_ticks() - start_ticks) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Toggle button (in top-left corner)
            if sidebar_open:
                if C.TG_X <= mx <= C.TG_X + C.TG_W and C.TG_Y <= my <= C.TG_Y + C.TG_H:
                    sidebar_open = False
                    dropdown_open = False
                    continue
            else:
                if C.TG_X <= mx <= C.TG_X + C.TG_W and C.TG_Y <= my <= C.TG_Y + C.TG_H:
                    sidebar_open = True
                    dropdown_open = False
                    continue
            # Only handle sidebar controls if sidebar is open
            if sidebar_open:
                # Size slider
                if C.SL_X <= mx <= C.SL_X + C.SL_W and 120 <= my <= 120 + C.SL_H:
                    slider_drag = "size"
                # Speed slider
                elif C.SL_X <= mx <= C.SL_X + C.SL_W and 220 <= my <= 220 + C.SL_H:
                    slider_drag = "speed"
                # Dropdown
                elif (
                    C.PT_X <= mx <= C.PT_X + C.PT_W and C.PT_Y <= my <= C.PT_Y + C.PT_H
                ):
                    dropdown_open = not dropdown_open
                elif (
                    dropdown_open
                    and C.PT_X <= mx <= C.PT_X + C.PT_W
                    and C.PT_Y + C.PT_H < my <= C.PT_Y + C.PT_H + len(PATTERNS) * C.PT_H
                ):
                    idx = (my - (C.PT_Y + C.PT_H)) // C.PT_H
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
            if slider_drag == "size":
                # Map mouse x to size
                circle_radius = max(
                    C.SIZE_MIN,
                    min(C.SIZE_MAX, (mx - C.SL_X) * (C.SIZE_MAX - C.SIZE_MIN) / C.SL_W),
                )
            elif slider_drag == "speed":
                circle_speed = max(
                    C.SPEED_MIN,
                    min(
                        C.SPEED_MAX,
                        (mx - C.SL_X) * (C.SPEED_MAX - C.SPEED_MIN) / C.SL_W,
                    ),
                )

    # Draw background
    screen.fill(C.WHITE)

    # Draw moving circle
    x, y = get_position(t, PATTERNS[pattern_idx], circle_speed, circle_radius)
    pygame.draw.circle(screen, C.BLUE, (x, y), int(circle_radius))
    # Draw sidebar if open
    if sidebar_open:
        draw_sidebar()
    # Draw toggle button in top-left corner, with 'Settings' inside
    draw_toggle_button(C.TG_X, C.TG_Y, C.TG_W, C.TG_H, sidebar_open)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()
