import pygame
import math

# --- Config ---
WIDTH, HEIGHT = 1400, 800
FPS = 120

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
LIGHT_GRAY = (220, 220, 220)
BLUE = (100, 180, 255)
RED = (255, 100, 100)

# --- Movement Patterns ---
PATTERNS = ["Circle", "Horizontal", "Vertical", "Diagonal", "Figure-Eight"]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Eye Pursuit")
clock = pygame.time.Clock()

# --- Control State ---
circle_radius = 40  # Object size
circle_orbit_radius = 200  # New: movement/orbit radius for 'Circle' pattern
circle_speed = 150
pattern_idx = 0

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
    screen.blit(text, (x, y-h//2-5))
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

# --- Movement Functions ---
def get_position(t, pattern, speed, radius):
    cx, cy = WIDTH // 2, HEIGHT // 2
    # Calculate max movement radii so the circle stays inside the screen
    max_rx = cx - radius - 10
    max_ry = cy - radius - 10
    # For 'Circle' pattern, use the user-controlled orbit radius, but clamp to fit screen
    orbit_r = min(circle_orbit_radius, max_ry, max_rx)
    if pattern == "Circle":
        angle = (speed/100) * t
        x = cx + orbit_r * math.cos(angle)
        y = cy + orbit_r * math.sin(angle)
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
    elif pattern == "Figure-Eight":
        angle = (speed/100) * t
        x = cx + max_rx * math.sin(angle) # check the math on this
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
            # Size slider
            if 50 <= mx <= 350 and 500 <= my <= 530:
                slider_drag = 'size'
            # Orbit radius slider (new)
            elif 50 <= mx <= 350 and 540 <= my <= 570:
                slider_drag = 'orbit_radius'
            # Speed slider
            elif 400 <= mx <= 700 and 500 <= my <= 530:
                slider_drag = 'speed'
            # Dropdown
            elif 750 <= mx <= 900 and 500 <= my <= 530:
                dropdown_open = not dropdown_open
            elif dropdown_open and 750 <= mx <= 900 and 530 < my <= 530+len(PATTERNS)*30:
                idx = (my-530)//30
                if 0 <= idx < len(PATTERNS):
                    pattern_idx = idx
                dropdown_open = False
            else:
                dropdown_open = False
        elif event.type == pygame.MOUSEBUTTONUP:
            slider_drag = None
        elif event.type == pygame.MOUSEMOTION and slider_drag:
            mx, my = event.pos
            if slider_drag == 'size':
                # Map mouse x to size
                circle_radius = max(10, min(100, (mx-50)/3))
            elif slider_drag == 'orbit_radius':
                # Map mouse x to orbit radius
                circle_orbit_radius = max(20, min(350, (mx-50)/2))
            elif slider_drag == 'speed':
                circle_speed = max(20, min(400, (mx-400)*1.2))

    # Draw background
    screen.fill(WHITE)

    # Draw moving circle
    x, y = get_position(t, PATTERNS[pattern_idx], circle_speed, circle_radius)
    pygame.draw.circle(screen, BLUE, (x, y), int(circle_radius))

    # Draw control panel
    # Size slider
    draw_slider(50, 500, 300, 30, 2, 50, circle_radius, "Size")
    # Orbit radius slider (new)
    draw_slider(50, 540, 300, 30, 20, 350, circle_orbit_radius, "Movement Radius")
    # Speed slider
    draw_slider(400, 500, 300, 30, 20, 400, circle_speed, "Speed")
    # Dropdown
    draw_dropdown(750, 500, 150, 30, PATTERNS, pattern_idx, dropdown_open)
    font = pygame.font.SysFont(None, 22)
    screen.blit(font.render("Pattern", True, BLACK), (750, 480))

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()