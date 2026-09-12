import pygame
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import CLOCK

from death import death_screen

V_W, V_H = 1100, 600

FPS = 30
GAME_SPEED = 8

GRAVITY = 1
FLAP_STRENGTH = -12
MAX_FALL_SPEED = 12

PIPE_WIDTH = 90
PIPE_SPAWN_INTERVAL = 75
PIPE_GAP_MIN = 240
PIPE_GAP_MAX = 320

CLUE_SIZE = 25
REVERSE_INTERVAL = FPS * 10
LEVEL_LENGTH_SECONDS = 50
LEVEL_LENGTH_FRAMES = FPS * LEVEL_LENGTH_SECONDS
COUNTDOWN_MS = 3000

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
LEVEL3_DIR = os.path.join(ASSETS_DIR, "Level3")
LEVEL3_BG_DIR = os.path.join(LEVEL3_DIR, "Background")

SUSPECTS = [
    "Rogue Sparrow",
    "Captain Crow",
    "Agent Owl",
    "Scarlet Falcon",
    "Dr. Pigeon",
    "Phantom Parrot",
]

WEAPONS = [
    "Steel Pipe Trap",
    "Rotating Blade",
    "Security Drone",
    "Falling Crate",
    "Laser Barrier",
    "Engine Turbine",
]

ROOMS = [
    "Cloud Zone",
    "Storm Field",
    "Sky Bridge",
    "Wind Tunnel",
    "Fog Sector",
    "Sunset Ridge",
]

TARGETED_SUSPECT_CLUES = {
    "Rogue Sparrow": [
        "Small rapid wingbeats were heard nearby.",
        "Tiny feathers were scattered across the path.",
        "Something fast darted between obstacles."
    ],
    "Captain Crow": [
        "A loud caw echoed through the sky.",
        "Dark feathers drifted downward slowly.",
        "A shadow circled from above."
    ],
    "Agent Owl": [
        "Silent movement was detected in the air.",
        "Wide wingspan shadows passed overhead.",
        "Sharp talon marks were found on debris."
    ],
    "Scarlet Falcon": [
        "A red streak shot across the sky.",
        "Feathers with a crimson tint were found.",
        "Something dove at incredible speed."
    ],
    "Dr. Pigeon": [
        "Soft cooing echoed faintly.",
        "Grey feathers were found near a pipe.",
        "A clumsy flight pattern was observed."
    ],
    "Phantom Parrot": [
        "Colorful feathers shimmered strangely.",
        "A voice seemed to mimic sounds nearby.",
        "Movement appeared… then vanished."
    ]
}

TARGETED_WEAPON_CLUES = {
    "Steel Pipe Trap": [
        "Metal pipes were aligned too perfectly to be natural.",
        "The spacing suggests a constructed obstacle.",
        "The surfaces were smooth and artificially shaped."
    ],
    "Rotating Blade": [
        "Circular cut marks were found nearby.",
        "Something sharp spun at high speed.",
        "Air currents felt sliced and unstable."
    ],
    "Security Drone": [
        "A faint mechanical buzzing echoed overhead.",
        "Small metallic parts were found drifting.",
        "Something tracked movement from above."
    ],
    "Falling Crate": [
        "Wooden fragments fell from above.",
        "Heavy objects dropped without warning.",
        "Impact marks were scattered below."
    ],
    "Laser Barrier": [
        "Thin glowing lines flickered in the air.",
        "Burn marks appeared along invisible paths.",
        "The space felt restricted by unseen beams."
    ],
    "Engine Turbine": [
        "A deep mechanical roar filled the area.",
        "Strong suction pulled everything inward.",
        "Spinning machinery distorted the airflow."
    ]
}

TARGETED_ROOM_CLUES = {
    "Cloud Zone": [
        "Soft clouds reduced visibility.",
        "Everything felt light and hazy."
    ],
    "Storm Field": [
        "Dark clouds gathered rapidly.",
        "Thunder echoed in the distance."
    ],
    "Sky Bridge": [
        "A narrow path stretched across the air.",
        "Structures floated between gaps."
    ],
    "Wind Tunnel": [
        "Air rushed intensely through this area.",
        "Movement felt forced in one direction."
    ],
    "Fog Sector": [
        "Visibility dropped significantly.",
        "Shapes appeared and disappeared quickly."
    ],
    "Sunset Ridge": [
        "Golden light filled the sky.",
        "Long shadows stretched across clouds."
    ]
}


def get_virtual_mouse_pos():
    display = pygame.display.get_surface()
    if display is None:
        return pygame.mouse.get_pos()

    sw, sh = display.get_size()
    mx, my = pygame.mouse.get_pos()

    scale = min(sw / V_W, sh / V_H)
    dw, dh = int(V_W * scale), int(V_H * scale)
    x0 = (sw - dw) // 2
    y0 = (sh - dh) // 2

    mx = max(x0, min(x0 + dw - 1, mx))
    my = max(y0, min(y0 + dh - 1, my))

    vx = (mx - x0) / scale
    vy = (my - y0) / scale
    return int(vx), int(vy)


def generate_solution():
    return random.choice(SUSPECTS), random.choice(WEAPONS), random.choice(ROOMS)


def pick_tier(collected_count):
    if collected_count < 3:
        return 1
    elif collected_count < 6:
        return 2
    return 3


def get_targeted_clue(clue_type, collected_count, used_clues_for_type, solution):
    tier = pick_tier(collected_count)

    if clue_type == "suspect":
        pool = TARGETED_SUSPECT_CLUES[solution][:]
    elif clue_type == "weapon":
        pool = TARGETED_WEAPON_CLUES[solution][:]
    else:
        pool = TARGETED_ROOM_CLUES[solution][:]

    if tier == 1:
        pool = pool[:2]
    elif tier == 2:
        pool = pool[:3]

    random.shuffle(pool)
    for clue in pool:
        if clue not in used_clues_for_type:
            return clue
    return random.choice(pool) if pool else "No clue available."


def load_img(path, scale=None):
    img = pygame.image.load(path).convert_alpha()
    if scale:
        if isinstance(scale, tuple):
            img = pygame.transform.smoothscale(img, scale)
        else:
            w, h = img.get_size()
            img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
    return img


def safe_load(path, scale=None):
    try:
        return load_img(path, scale)
    except Exception:
        return None


def draw_clue_box(screen, clue_count):
    box_rect = pygame.Rect(8, 12, 210, 50)
    pygame.draw.rect(screen, (255, 255, 255), box_rect, border_radius=10)
    pygame.draw.rect(screen, (40, 40, 40), box_rect, 2, border_radius=10)

    font = pygame.font.Font("freesansbold.ttf", 16)
    text = font.render(f"Clues Collected = {clue_count}", True, (0, 0, 0))
    text_rect = text.get_rect(center=box_rect.center)
    screen.blit(text, text_rect)


def draw_countdown(screen, countdown_start):
    elapsed = pygame.time.get_ticks() - countdown_start
    remaining = 3 - (elapsed // 1000)
    if remaining > 0:
        font = pygame.font.Font("freesansbold.ttf", 90)
        text = font.render(str(remaining), True, (20, 20, 20))
        rect = text.get_rect(center=(V_W // 2, V_H // 2))
        screen.blit(text, rect)


def show_level3_instructions(screen, present):
    title_font = pygame.font.Font("freesansbold.ttf", 38)
    text_font = pygame.font.Font("freesansbold.ttf", 22)
    button_font = pygame.font.Font("freesansbold.ttf", 24)

    start_button = pygame.Rect(V_W // 2 - 140, 500, 280, 55)

    lines = [
        "Fly through narrow gaps using UP arrow.",
        "Every 4 clue boxes reveals a clue.",
        "Avoid crashing into pipes and terrain.",
        "Fuel drains constantly while flying.",
        "Collect clues to restore a small amount of fuel.",
        "Controls reverse every 10 seconds."
    ]

    # 🌌 sky glow pulse (instead of subway flicker)
    pulse = 0
    pulse_dir = 1

    while True:
        mouse_pos = get_virtual_mouse_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "exit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(mouse_pos):
                    return True

        # 🌌 DARK SKY BASE
        screen.fill((6, 8, 18))

        # 🌙 soft glowing cloud/moon effect
        pulse += pulse_dir
        if pulse > 35 or pulse < 0:
            pulse_dir *= -1

        glow = pygame.Surface((V_W, V_H), pygame.SRCALPHA)
        pygame.draw.circle(glow, (80, 110, 180, 30 + pulse), (V_W // 2, 180), 320)
        screen.blit(glow, (0, 0))

        # ✈️ TITLE PANEL
        title_box = pygame.Rect(0, 40, 680, 85)
        title_box.centerx = V_W // 2

        pygame.draw.rect(screen, (10, 16, 40), title_box, border_radius=14)
        pygame.draw.rect(screen, (70, 110, 200), title_box, 2, border_radius=14)

        title = title_font.render("Level 3: Flight Protocol", True, (235, 235, 245))
        screen.blit(title, title.get_rect(center=title_box.center))

        # 📜 INSTRUCTION PANEL
        panel = pygame.Rect(0, 150, 780, 300)
        panel.centerx = V_W // 2

        pygame.draw.rect(screen, (8, 12, 28), panel, border_radius=16)
        pygame.draw.rect(screen, (70, 100, 160), panel, 2, border_radius=16)

        # header
        header = text_font.render("AERIAL INCIDENT BRIEFING", True, (180, 200, 240))
        screen.blit(header, (panel.left + 20, panel.top + 10))

        # text
        y = panel.top + 55
        for line in lines:
            txt = text_font.render("• " + line, True, (210, 210, 220))
            screen.blit(txt, (panel.left + 25, y))
            y += 38

        # 🌫️ footer hint (mysterious sky vibe)
        hint = text_font.render(
            "Something is watching from above...",
            True,
            (150, 160, 190)
        )
        screen.blit(hint, hint.get_rect(center=(V_W // 2, panel.bottom + 30)))

        # 🔘 START BUTTON
        color = (70, 120, 200) if start_button.collidepoint(mouse_pos) else (45, 80, 150)

        pygame.draw.rect(screen, color, start_button, border_radius=10)
        pygame.draw.rect(screen, (200, 220, 255), start_button, 2, border_radius=10)

        txt = button_font.render("TAKE OFF", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=start_button.center))

        present()


def guessing_screen(screen, present, collected_clues, solution_suspect, solution_weapon, solution_room):
    button_font = pygame.font.Font("freesansbold.ttf", 14)
    clue_font = pygame.font.Font("freesansbold.ttf", 12)
    title_font = pygame.font.Font("freesansbold.ttf", 24)
    label_font = pygame.font.Font("freesansbold.ttf", 16)
    sel_font = pygame.font.Font("freesansbold.ttf", 16)

    selected = {"suspect": None, "weapon": None, "room": None}
    correct = {"suspect": False, "weapon": False, "room": False}
    result_text = ""
    attempt = 0
    show_final_buttons = False

    def draw_buttons(options, start_x, start_y, category):
        x, y = start_x, start_y
        rects = []
        mouse_pos = get_virtual_mouse_pos()

        for option in options:
            rect = pygame.Rect(x, y, 140, 30)
            rects.append((rect, option))

            if correct[category] and selected[category] == option:
                color = (50, 200, 50)
            elif selected[category] == option:
                color = (200, 50, 50)
            else:
                color = (60, 60, 90)

            pygame.draw.rect(screen, color, rect, border_radius=6)

            if rect.collidepoint(mouse_pos):
                glow_rect = rect.inflate(6, 6)
                pygame.draw.rect(screen, (100, 100, 150), glow_rect, 2, border_radius=8)

            screen.blit(button_font.render(option, True, (220, 220, 220)), (x + 6, y + 6))

            x += 150
            if x + 140 > V_W:
                x = start_x
                y += 40
        return rects

    submit_rect = pygame.Rect(V_W // 2 - 70, 430, 140, 35)
    retry_rect = pygame.Rect(300, 500, 200, 50)
    exit_rect = pygame.Rect(600, 500, 200, 50)

    while True:
        mouse_pos = get_virtual_mouse_pos()
        screen.fill((25, 25, 35))

        screen.blit(title_font.render("Based on the clues collected below, help the Detective solve the mystery:", True, (220, 220, 220)), (20, 20))
        y_offset = 50
        for clue in collected_clues[-12:]:
            screen.blit(clue_font.render(clue, True, (200, 200, 200)), (20, y_offset))
            y_offset += 18

        screen.blit(label_font.render("Suspects:", True, (220, 220, 220)), (50, 180))
        screen.blit(label_font.render("Weapons:", True, (220, 220, 220)), (50, 240))
        screen.blit(label_font.render("Rooms:", True, (220, 220, 220)), (50, 300))

        suspect_rects = draw_buttons(SUSPECTS, 50, 200, "suspect")
        weapon_rects = draw_buttons(WEAPONS, 50, 260, "weapon")
        room_rects = draw_buttons(ROOMS, 50, 320, "room")

        pygame.draw.rect(screen, (80, 80, 140), submit_rect, border_radius=6)
        screen.blit(button_font.render("SUBMIT GUESS", True, (220, 220, 220)),
                    (submit_rect.x + 10, submit_rect.y + 8))

        if show_final_buttons:
            pygame.draw.rect(screen, (50, 180, 50), retry_rect, border_radius=6)
            screen.blit(button_font.render("Keep Guessing", True, (220, 220, 220)),
                        (retry_rect.x + 20, retry_rect.y + 15))

            pygame.draw.rect(screen, (180, 50, 50), exit_rect, border_radius=6)
            screen.blit(button_font.render("Exit to Menu", True, (220, 220, 220)),
                        (exit_rect.x + 35, exit_rect.y + 15))

        screen.blit(sel_font.render(f"Selected Suspect: {selected['suspect']}", True, (220, 220, 220)), (50, 460))
        screen.blit(sel_font.render(f"Selected Weapon: {selected['weapon']}", True, (220, 220, 220)), (50, 480))
        screen.blit(sel_font.render(f"Selected Room: {selected['room']}", True, (220, 220, 220)), (50, 500))
        screen.blit(sel_font.render(result_text, True, (255, 100, 100)), (50, 400))

        present()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "exit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, opt in suspect_rects:
                    if rect.collidepoint(mouse_pos) and not correct["suspect"]:
                        selected["suspect"] = opt
                for rect, opt in weapon_rects:
                    if rect.collidepoint(mouse_pos) and not correct["weapon"]:
                        selected["weapon"] = opt
                for rect, opt in room_rects:
                    if rect.collidepoint(mouse_pos) and not correct["room"]:
                        selected["room"] = opt

                if submit_rect.collidepoint(mouse_pos) and not show_final_buttons:
                    if not (selected["suspect"] and selected["weapon"] and selected["room"]):
                        result_text = "Please select one from each category."
                        continue

                    correct["suspect"] = (selected["suspect"] == solution_suspect) or correct["suspect"]
                    correct["weapon"] = (selected["weapon"] == solution_weapon) or correct["weapon"]
                    correct["room"] = (selected["room"] == solution_room) or correct["room"]

                    correct_count = sum([correct["suspect"], correct["weapon"], correct["room"]])

                    if correct_count == 3:
                        return True

                    if attempt == 0:
                        result_text = "Partially correct! Correct ones stay green. Try again."
                        attempt += 1
                    else:
                        result_text = "Still incorrect. Keep guessing or exit."
                        show_final_buttons = True

                if show_final_buttons:
                    if retry_rect.collidepoint(mouse_pos):
                        for cat in ["suspect", "weapon", "room"]:
                            if not correct[cat]:
                                selected[cat] = None
                        result_text = ""
                        show_final_buttons = False

                    if exit_rect.collidepoint(mouse_pos):
                        return False


class FlappyDetective:
    X_POS = 160

    def __init__(self, img):
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.y = V_H // 2
        self.vel_y = 0

        hitbox_scale = 0.75
        self.hitbox = self.rect.copy()
        self.hitbox.width = int(self.rect.width * hitbox_scale)
        self.hitbox.height = int(self.rect.height * hitbox_scale)

    def update(self, keys, reversed_controls):
        if reversed_controls:
            if keys[pygame.K_DOWN] or keys[pygame.K_SPACE]:
                self.vel_y = FLAP_STRENGTH
        else:
            if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
                self.vel_y = FLAP_STRENGTH

        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        self.rect.y += self.vel_y

        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0

        self.hitbox.center = self.rect.center

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def get_rect(self):
        return self.hitbox


class PipeWithGap:
    def __init__(self):
        self.x = V_W + 80
        self.gap = random.randint(PIPE_GAP_MIN, PIPE_GAP_MAX)
        self.top_h = random.randint(80, V_H - self.gap - 80)
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.top_h)
        self.bottom_rect = pygame.Rect(self.x, self.top_h + self.gap, PIPE_WIDTH, V_H - (self.top_h + self.gap))
        self.passed = False

    def update(self):
        self.x -= GAME_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, (34, 139, 34), self.top_rect)
        pygame.draw.rect(screen, (34, 139, 34), self.bottom_rect)

    def collides(self, rect):
        return rect.colliderect(self.top_rect) or rect.colliderect(self.bottom_rect)

    def off_screen(self):
        return self.x + PIPE_WIDTH < 0

def get_safe_y(pipes, clue_height=30):
    safe_zones = []

    for pipe in pipes:
        gap_top = pipe.top_h
        gap_bottom = pipe.top_h + pipe.gap

        # safe vertical center of gap
        safe_zones.append((gap_top + gap_bottom) // 2)

    if safe_zones:
        return random.choice(safe_zones)

    return random.randint(100, V_H - 100)


class WhiteSquare:
    def __init__(self, image, pipes):
        self.image = image
        self.rect = self.image.get_rect()

        self.rect.x = V_W + random.randint(150, 500)
        self.rect.y = get_safe_y(pipes) + random.randint(-20, 20)

        # spawn ONLY in pipe gaps
        self.rect.y = get_safe_y(pipes)

    def update(self):
        self.rect.x -= GAME_SPEED

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def off_screen(self):
        return self.rect.right < 0
    
def all_levels_complete_screen(screen, present):
    font_title = pygame.font.Font("freesansbold.ttf", 42)
    font_btn = pygame.font.Font("freesansbold.ttf", 24)

    restart_btn = pygame.Rect(V_W//2 - 160, 320, 320, 60)
    exit_btn = pygame.Rect(V_W//2 - 160, 410, 320, 60)

    while True:
        mouse = get_virtual_mouse_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "exit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_btn.collidepoint(mouse):
                    return "restart_all"
                if exit_btn.collidepoint(mouse):
                    return "exit"

        screen.fill((10, 10, 25))

        title = font_title.render("🎉 YOU COMPLETED ALL LEVELS 🎉", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(V_W//2, 180)))

        subtitle = font_btn.render("Great detective work in the skies!", True, (180, 180, 200))
        screen.blit(subtitle, subtitle.get_rect(center=(V_W//2, 240)))

        pygame.draw.rect(screen, (60, 160, 80), restart_btn, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), restart_btn, 2, border_radius=10)
        txt1 = font_btn.render("Play All Levels Again", True, (255, 255, 255))
        screen.blit(txt1, txt1.get_rect(center=restart_btn.center))

        pygame.draw.rect(screen, (180, 60, 60), exit_btn, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), exit_btn, 2, border_radius=10)
        txt2 = font_btn.render("Exit to Desktop", True, (255, 255, 255))
        screen.blit(txt2, txt2.get_rect(center=exit_btn.center))

        present()


def run_level3(screen, present):
    if not show_level3_instructions(screen, present):
        return False

    solution_suspect, solution_weapon, solution_room = generate_solution()
    collected_clues = []
    used_clues = {"suspect": set(), "weapon": set(), "room": set()}
    alive = True

    clock = pygame.time.Clock()
    countdown_start = pygame.time.get_ticks()

    detective_img = load_img(os.path.join(LEVEL3_DIR, "plane.png"), scale=0.10)
    clue_img = load_img(os.path.join(LEVEL3_DIR, "clue.png"), scale=0.06)
    bg_img = safe_load(os.path.join(LEVEL3_BG_DIR, "bg.png"), scale=(V_W, V_H))

    player = FlappyDetective(detective_img)

    pipes = []
    collectibles = []

    pipe_timer = 0
    squares_collected = 0
    points = 0
    fuel = 20.0

    reverse_timer = REVERSE_INTERVAL
    reversed_controls = False

    far_scroll = 0
    mid_scroll = 0
    near_scroll = 0

    game_over = False
    game_over_timer = 0
    finish_timer = 0
    frame_count = 0

    while True:
        frame_count += 1
        countdown_active = (pygame.time.get_ticks() - countdown_start) < COUNTDOWN_MS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "exit"

        keys = pygame.key.get_pressed()

        if not countdown_active:
            reverse_timer -= 1
            if reverse_timer <= 0 and not game_over:
                reversed_controls = not reversed_controls
                reverse_timer = REVERSE_INTERVAL

        if alive and not countdown_active:
            player.update(keys, reversed_controls)
        
        # ---------------- GROUND COLLISION ----------------
        if player.rect.bottom >= V_H:
            death_screen(screen, present)
            result = guessing_screen(
                screen,
                present,
                collected_clues,
                solution_suspect,
                solution_weapon,
                solution_room
            )

            if result == True:
                return "win"
            elif result == "exit":
                return "exit"
            else:
                return "restart"

        if not alive:
            pygame.time.delay(200)
            death_screen(screen, present)
            result = guessing_screen(
                screen,
                present,
                collected_clues,
                solution_suspect,
                solution_weapon,
                solution_room
            )

            if result == True:
                return "win"
            elif result == "exit":
                return "exit"
            else:
                return "restart"
        

        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill((135, 206, 235))

        far_scroll -= 0.3
        mid_scroll -= 0.6
        near_scroll -= 1
        if far_scroll < -V_W:
            far_scroll = 0
        if mid_scroll < -V_W:
            mid_scroll = 0
        if near_scroll < -V_W:
            near_scroll = 0

        for i in range(3):
            base_x = far_scroll + i * V_W
            pygame.draw.polygon(screen, (180, 180, 200), [(base_x + 0, 470), (base_x + 200, 300), (base_x + 400, 470)])
        for i in range(3):
            base_x = mid_scroll + i * V_W
            pygame.draw.polygon(screen, (140, 140, 160), [(base_x + 100, 480), (base_x + 300, 280), (base_x + 500, 480)])
        for i in range(3):
            base_x = near_scroll + i * V_W
            pygame.draw.polygon(screen, (100, 100, 120), [(base_x + 200, 500), (base_x + 420, 260), (base_x + 640, 500)])
            pygame.draw.polygon(screen, (150, 150, 160), [(base_x + 250, 450), (base_x + 430, 300), (base_x + 610, 450)])

        if not game_over and not countdown_active and frame_count < LEVEL_LENGTH_FRAMES:
            pipe_timer += 1
            if pipe_timer >= PIPE_SPAWN_INTERVAL:
                pipes.append(PipeWithGap())
                pipe_timer = 0

        player_rect = player.get_rect()

        for pipe in pipes[:]:
            pipe.update()
            pipe.draw(screen)

            if not game_over and not countdown_active and pipe.collides(player_rect):
                death_screen(screen, present)
                result = guessing_screen(
                    screen,
                    present,
                    collected_clues,
                    solution_suspect,
                    solution_weapon,
                    solution_room
                )

                if result == True:
                    return "win"
                elif result == "exit":
                    return "exit"
                else:
                    return "restart"

            if pipe.off_screen():
                pipes.remove(pipe)

        if not game_over and not countdown_active and frame_count < LEVEL_LENGTH_FRAMES:
            if random.randint(0, 100) < 6 and len(collectibles) < 4:
                collectibles.append(WhiteSquare(clue_img, pipes))

        for sq in collectibles[:]:
            sq.update()
            sq.draw(screen)

            if sq.off_screen():
                collectibles.remove(sq)
                continue

            if not game_over and not countdown_active and player_rect.colliderect(sq.rect):
                collectibles.remove(sq)
                squares_collected += 1
                points += 5
                fuel = min(30, fuel + 2)

                if squares_collected >= 4:
                    clue_type = random.choice(["suspect", "weapon", "room"])
                    collected_count = len(collected_clues)

                    if clue_type == "suspect":
                        clue_text = get_targeted_clue("suspect", collected_count, used_clues["suspect"], solution_suspect)
                        used_clues["suspect"].add(clue_text)
                    elif clue_type == "weapon":
                        clue_text = get_targeted_clue("weapon", collected_count, used_clues["weapon"], solution_weapon)
                        used_clues["weapon"].add(clue_text)
                    else:
                        clue_text = get_targeted_clue("room", collected_count, used_clues["room"], solution_room)
                        used_clues["room"].add(clue_text)

                    if clue_text not in collected_clues:
                        collected_clues.append(clue_text)

                    squares_collected = 0

        if not game_over and not countdown_active and frame_count < LEVEL_LENGTH_FRAMES:
            fuel = max(0, fuel - 1 / FPS)
            if fuel <= 0:
                game_over = True
                game_over_timer = FPS * 2

        if game_over and game_over_timer > 0:
            player.vel_y += GRAVITY *0.5
            player.rect.y += int(player.vel_y)
            game_over_timer -= 1
            if game_over_timer <= 0:
                death_screen(screen, present)
                result = guessing_screen(
                screen,
                present,
                collected_clues,
                solution_suspect,
                solution_weapon,
                solution_room
            )

            if result == True:
                return "win"
            elif result == "exit":
                return "exit"
            else:
                return "restart"

        player.draw(screen)

        pygame.draw.rect(screen, (0, 0, 0), (18, 548, 304, 24), 2)
        pygame.draw.rect(screen, (255, 0, 0), (20, 550, int(fuel * 10), 20))

        mode_font = pygame.font.Font("freesansbold.ttf", 18)
        big_font = pygame.font.Font("freesansbold.ttf", 34)

        draw_clue_box(screen, len(collected_clues))

        fuel_label = mode_font.render("Fuel", True, (0, 0, 0))
        screen.blit(fuel_label, (20, 522))

        # CONTROL MODE WARNING 
        warning_font = pygame.font.Font("freesansbold.ttf", 24)

        if reversed_controls:
            warning_text = "CONTROLS REVERSED: USE DOWN ARROW"
            color = (255, 80, 80)
        else:
            warning_text = "CONTROLS NORMAL: USE UP ARROW"
            color = (10, 30, 90)

        text_surface = warning_font.render(warning_text, True, color)
        text_rect = text_surface.get_rect(center=(V_W // 2, 30))
        screen.blit(text_surface, text_rect)

        if game_over:
            overlay = pygame.Surface((V_W, V_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            msg = big_font.render("Out of fuel! Plane crashes!", True, (255, 0, 0))
            screen.blit(msg, msg.get_rect(center=(V_W // 2, V_H // 2)))

        elif frame_count >= LEVEL_LENGTH_FRAMES:
            finish_timer += 1
            overlay = pygame.Surface((V_W, V_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            msg = big_font.render("LEVEL 3 COMPLETE", True, (255, 255, 255))
            screen.blit(msg, msg.get_rect(center=(V_W // 2, V_H // 2)))
            if finish_timer >= FPS * 2:
                death_screen(screen, present)
                result = guessing_screen(
                screen,
                present,
                collected_clues,
                solution_suspect,
                solution_weapon,
                solution_room
            )

            if result == True:
                return "win"
            elif result == "exit":
                return "exit"
            else:
                return "restart"

        if countdown_active:
            draw_countdown(screen, countdown_start)

        present()

        CLOCK.tick(FPS)


if __name__ == "__main__":
    pygame.init()
    SCREEN = pygame.display.set_mode((V_W, V_H))
    pygame.display.set_caption("Level 3 Test")

    def present_test():
        pygame.display.flip()

    run_level3(SCREEN, present_test)
    pygame.quit()