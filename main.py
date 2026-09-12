import pygame
import random
import os

pygame.init()

# -------------------- VIRTUAL (base) RESOLUTION --------------------
V_W, V_H = 1100, 600
VSCREEN = pygame.Surface((V_W, V_H))

# -------------------- WINDOWED DISPLAY --------------------
SCREEN = pygame.display.set_mode((V_W, V_H), pygame.RESIZABLE)
pygame.display.set_caption("Detective Dash")
CLOCK = pygame.time.Clock()

#---------------------Clues---------------------
collected_clues = []

def present():
    sw, sh = SCREEN.get_size()
    scale = min(sw / V_W, sh / V_H)
    dw, dh = int(V_W * scale), int(V_H * scale)

    scaled = pygame.transform.smoothscale(VSCREEN, (dw, dh))
    x = (sw - dw) // 2
    y = (sh - dh) // 2

    SCREEN.fill((0, 0, 0))
    SCREEN.blit(scaled, (x, y))
    pygame.display.flip()


def virtual_mouse_pos():
    mx, my = pygame.mouse.get_pos()
    sw, sh = SCREEN.get_size()
    scale = min(sw / V_W, sh / V_H)
    dw, dh = int(V_W * scale), int(V_H * scale)
    x0 = (sw - dw) // 2
    y0 = (sh - dh) // 2

    mx = max(x0, min(x0 + dw - 1, mx))
    my = max(y0, min(y0 + dh - 1, my))

    vx = (mx - x0) / scale
    vy = (my - y0) / scale
    return int(vx), int(vy)


from levels.level1 import run_level1
from levels.level2 import guessing_screen, run_level2
from levels.level3 import run_level3


# =================== ASSETS ===================
BASE_DIR = os.path.dirname(__file__)
DETECTIVE_DIR = os.path.join(BASE_DIR, "Assets", "Detective")
STARTPAGE_DIR = os.path.join(BASE_DIR, "Assets", "StartPage")


def load_scaled_image(path, size):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, size)


def load_image(path):
    return pygame.image.load(path).convert_alpha()


try:
    RUN1 = load_scaled_image(os.path.join(DETECTIVE_DIR, "run1.png"), (140, 140))
    RUN2 = load_scaled_image(os.path.join(DETECTIVE_DIR, "run2.png"), (140, 140))
    RUN_FRAMES = [RUN1, RUN2]
except Exception:
    RUN_FRAMES = []

try:
    CLOUD_IMG = load_image(os.path.join(STARTPAGE_DIR, "Cloud.png"))
except Exception:
    CLOUD_IMG = None

try:
    TRACK_IMG = load_image(os.path.join(STARTPAGE_DIR, "Track.png"))
except Exception:
    TRACK_IMG = None

try:
    raw_lock = pygame.image.load(os.path.join(STARTPAGE_DIR, "lock.png")).convert_alpha()
    raw_lock = pygame.transform.smoothscale(raw_lock, (24, 24))

    for x in range(raw_lock.get_width()):
        for y in range(raw_lock.get_height()):
            r, g, b, a = raw_lock.get_at((x, y))
            if r > 235 and g > 235 and b > 235:
                raw_lock.set_at((x, y), (255, 255, 255, 0))

    LOCK_IMG = raw_lock
except Exception:
    LOCK_IMG = None


# =================== HELPER ===================
def draw_gradient(surface, top_color, bottom_color):
    for y in range(V_H):
        ratio = y / V_H
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (V_W, y))


# =================== START SCREEN ===================
def start_screen():
    title_font = pygame.font.SysFont("arialblack", 64)
    sub_font = pygame.font.Font("freesansbold.ttf", 20)
    button_font = pygame.font.Font("freesansbold.ttf", 24)

    center_x = V_W // 2
    start_rect = pygame.Rect(0, 0, 220, 60)
    start_rect.center = (center_x, 470)

    frame_index = 0
    frame_timer = 0
    ground_y = 395
    cloud_x = V_W + 100
    cloud_y = 85
    track_x = 0
    track_y = 395
    track_speed = 6

    while True:
        mouse_pos = virtual_mouse_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(mouse_pos):
                    return True

        frame_timer += 1
        if frame_timer >= 8:
            frame_timer = 0
            if RUN_FRAMES:
                frame_index = (frame_index + 1) % len(RUN_FRAMES)

        cloud_x -= 1
        if CLOUD_IMG and cloud_x < -CLOUD_IMG.get_width():
            cloud_x = V_W + random.randint(220, 420)
            cloud_y = random.randint(60, 110)

        track_x -= track_speed
        if TRACK_IMG:
            track_width = TRACK_IMG.get_width()
            if track_x <= -track_width:
                track_x = 0

        VSCREEN.fill((25, 25, 35))  # deep detective night base

        # vignette 
        vignette = pygame.Surface((V_W, V_H), pygame.SRCALPHA)
        pygame.draw.circle(vignette, (0, 0, 0, 0), (V_W//2, V_H//2), 180)
        pygame.draw.circle(vignette, (0, 0, 0, 90), (V_W//2, V_H//2), 700)
        VSCREEN.blit(vignette, (0, 0))

        if CLOUD_IMG:
            fog_img = pygame.transform.smoothscale(CLOUD_IMG, (220, 120))
            fog_img.set_alpha(140)  # ghost-like
            VSCREEN.blit(fog_img, (cloud_x, cloud_y))

        if TRACK_IMG:
            track_width = TRACK_IMG.get_width()
            VSCREEN.blit(TRACK_IMG, (track_x, track_y))
            VSCREEN.blit(TRACK_IMG, (track_x + track_width, track_y))
        else:
            pygame.draw.line(VSCREEN, (0, 0, 0), (0, ground_y), (V_W, ground_y), 3)

        title_box = pygame.Rect(0, 35, 650, 100)
        title_box.centerx = center_x

        pygame.draw.rect(VSCREEN, (25, 25, 40), title_box, border_radius=16)
        pygame.draw.rect(VSCREEN, (90, 90, 130), title_box, 2, border_radius=16)

        title_shadow = title_font.render("Detective Dash", True, (0, 0, 0))
        title_glow = title_font.render("Detective Dash", True, (90, 120, 180))
        title_main = title_font.render("Detective Dash", True, (235, 235, 245))

        title_rect = title_main.get_rect(center=title_box.center)
        shadow_rect = title_shadow.get_rect(center=(title_box.centerx + 3, title_box.centery + 3))
        VSCREEN.blit(title_glow, title_rect.move(0, 0))
        VSCREEN.blit(title_shadow, shadow_rect)
        VSCREEN.blit(title_main, title_rect)

        sub = sub_font.render(
            "Each level brings a new location, a new mystery, and new clues.",
            True,
            (170, 170, 180)
        )
        VSCREEN.blit(sub, sub.get_rect(center=(center_x, 165)))

        if RUN_FRAMES:
            detective = RUN_FRAMES[frame_index]
            detective_rect = detective.get_rect(midbottom=(center_x, ground_y))
            VSCREEN.blit(detective, detective_rect)
        else:
            ghost_color = (80, 80, 95)
            pygame.draw.rect(VSCREEN, ghost_color, (center_x - 35, 240, 70, 110), border_radius=10)

            # subtle shadow under feet
            pygame.draw.ellipse(VSCREEN, (0, 0, 0, 120), (center_x - 45, 335, 90, 20))

        color = (70, 90, 140) if start_rect.collidepoint(mouse_pos) else (40, 50, 80)
        pygame.draw.rect(VSCREEN, (0, 0, 0), start_rect.move(3, 3), border_radius=10)

        txt = button_font.render("START", True, (255, 255, 255))
        VSCREEN.blit(txt, txt.get_rect(center=start_rect.center))

        present()
        CLOCK.tick(30)


# =================== LEVEL SELECT ===================
def level_select_screen(level1_unlocked, level2_unlocked, level3_unlocked):
    title_font = pygame.font.Font("freesansbold.ttf", 36)
    button_font = pygame.font.Font("freesansbold.ttf", 22)
    subtitle_font = pygame.font.Font("freesansbold.ttf", 20)

    buttons = [
        {"text": "Level 1: Living Room Run", "level": 1, "unlocked": level1_unlocked},
        {"text": "Level 2: Subway Surfers", "level": 2, "unlocked": level2_unlocked},
        {"text": "Level 3: Flappy Flight", "level": 3, "unlocked": level3_unlocked},
    ]

    start_y = 260
    for i, btn in enumerate(buttons):
        btn["rect"] = pygame.Rect(V_W // 2 - 220, start_y + i * 80, 440, 55)

    while True:
        VSCREEN.fill((25, 25, 35))
        mouse_pos = virtual_mouse_pos()

        title = title_font.render("Choose Your Level", True, (220, 220, 220))
        VSCREEN.blit(title, title.get_rect(center=(V_W // 2, 140)))

        sub = subtitle_font.render(
            "Help the detective solve each mystery to unlock the next level.",
            True,
            (180, 180, 180)
        )
        VSCREEN.blit(sub, sub.get_rect(center=(V_W // 2, 190)))

        for btn in buttons:
            rect = btn["rect"]
            unlocked = btn["unlocked"]

            if unlocked:
                if rect.collidepoint(mouse_pos):
                    glow_rect = rect.inflate(10, 10)
                    pygame.draw.rect(VSCREEN, (120, 120, 200), glow_rect, border_radius=12)
                    color = (90, 90, 140)
                else:
                    color = (50, 50, 90)
            else:
                color = (90, 90, 90)

            pygame.draw.rect(VSCREEN, color, rect, border_radius=8)

            text_surf = button_font.render(btn["text"], True, (220, 220, 220))

            if not unlocked and LOCK_IMG:
                total_width = text_surf.get_width() + 12 + LOCK_IMG.get_width()
                start_x = rect.centerx - total_width // 2
                VSCREEN.blit(text_surf, (start_x, rect.centery - text_surf.get_height() // 2))
                lock_x = start_x + text_surf.get_width() + 12
                lock_y = rect.centery - LOCK_IMG.get_height() // 2
                VSCREEN.blit(LOCK_IMG, (lock_x, lock_y))
            else:
                VSCREEN.blit(text_surf, text_surf.get_rect(center=rect.center))

        present()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in buttons:
                    if btn["unlocked"] and btn["rect"].collidepoint(mouse_pos):
                        return btn["level"]

        CLOCK.tick(30)


# =================== WIN SCREEN ===================
def win_screen(screen, present):
    font_big = pygame.font.Font("freesansbold.ttf", 64)
    font = pygame.font.Font("freesansbold.ttf", 28)

    while True:
        screen.fill((10, 10, 25))

        # glowing panel
        panel = pygame.Rect(V_W//2 - 260, 160, 520, 260)
        pygame.draw.rect(screen, (10, 18, 45), panel, border_radius=15)
        pygame.draw.rect(screen, (40, 70, 140), panel, 3, border_radius=15)

        title = font_big.render("CASE CLOSED", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(V_W // 2, 240)))

        sub = font.render("You solved the mystery!!.", True, (220, 220, 220))
        screen.blit(sub, sub.get_rect(center=(V_W // 2, 310)))

        hint = font.render("Returning to case board...", True, (180, 180, 180))
        screen.blit(hint, hint.get_rect(center=(V_W // 2, 360)))

        present()

        pygame.time.wait(2000)  # cinematic pause
        return


# =================== MAIN FLOW ===================
def main():
    if not start_screen():
        return

    level1_unlocked = True
    level2_unlocked = False
    level3_unlocked = False

    while True:
        selected_level = level_select_screen(level1_unlocked, level2_unlocked, level3_unlocked)

        if selected_level is None:
            pygame.quit()
            return

        if selected_level == 1:
            result = run_level1(VSCREEN, present)

            if result == "win":
                level2_unlocked = True

            elif result == "restart":
                # send player back into Level 1 again
                continue

            elif result == "exit":
                pygame.quit()
                return

        elif selected_level == 2 and level2_unlocked:

            result = run_level2(VSCREEN, present)

            if result == "win":
                level3_unlocked = True

            elif result == "restart":
                # send player back into Level 2 again
                continue

            elif result == "exit":
                pygame.quit()
                return
            
        elif selected_level == 3 and level3_unlocked:

            result = run_level3(VSCREEN, present)

            if result == "win":
                win_screen(VSCREEN, present)

            elif result == "restart":
                continue

            elif result == "restart_all":
                # full game reset loop
                level1_unlocked = True
                level2_unlocked = False
                level3_unlocked = False
                continue  # goes back to level select screen

            elif result == "exit":
                pygame.quit()
                return

if __name__ == "__main__":
    main()