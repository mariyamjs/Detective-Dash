import sys
from turtle import Screen
import pygame
import os
import random

from death import death_screen

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import CLOCK, draw_gradient

V_W, V_H = 1100, 600

SUSPECTS = [
    "Technician",
    "Graffiti Artist",
    "Skateboard Boy",
    "Tunnel Engineer",
    "Night Conductor",
    "Platform Inspector",
]

WEAPONS = [
    "Signal Wrench",
    "Broken Skateboard",
    "Hammer",
    "Electric Rod",
    "Train Coupler",
    "Brake Lever",
]

ROOMS = [
    "Platform A",
    "Control Room",
    "Train Yard",
    "Service Corridor",
    "Elevated Bridge",
    "Storage Depot",
]

TARGETED_SUSPECT_CLUES = {
    "Technician": [
        "A wrench marked with transit code was found.",
        "Boot prints match maintenance staff footwear.",
        "Grease stains lead toward the tunnel entrance.",
    ],
    "Graffiti Artist": [
        "Fresh paint smears were found on a wall.",
        "Spray can caps were scattered near Platform A.",
        "Tags matching a known symbol appear nearby.",
    ],
    "Skateboard Boy": [
        "Worn wheel tracks were found along the platform edge.",
        "A snapped skateboard deck was discovered.",
        "Scraped concrete suggests fast movement.",
    ],
    "Tunnel Engineer": [
        "Blueprint fragments were found in a toolbox.",
        "A hard hat was left near a control panel.",
        "Maintenance logs were altered recently.",
    ],
    "Night Conductor": [
        "Train schedule sheet was found in a pocket.",
        "Uniform buttons match staff clothing.",
        "A whistle was found near the tracks.",
    ],
    "Platform Inspector": [
        "Inspection clipboard was left open.",
        "Safety tag markings were recently updated.",
        "Flashlight battery was drained unusually fast.",
    ],
}

TARGETED_WEAPON_CLUES = {
    "Signal Wrench": [
        "Rail signal bolts were loosened recently.",
        "Metal scraping marks found on control panel.",
        "Tool imprints match railway equipment.",
    ],
    "Broken Skateboard": [
        "Wood splinters found near platform edge.",
        "Wheel bearings scattered across the floor.",
        "Impact marks suggest high-speed collision.",
    ],
    "Hammer": [
        "Heavy dent marks on metal railing.",
        "Rubber grip fragments found nearby.",
        "Tool bag was left open.",
    ],
    "Electric Rod": [
        "Sparks marks were found on wiring panel.",
        "Burn residue near a tunnel junction.",
        "Rod missing from maintenance rack.",
    ],
    "Train Coupler": [
        "Metal coupling piece found detached.",
        "Grease trail leads toward storage bay.",
        "Impact noise reported by witness.",
    ],
    "Brake Lever": [
        "Brake housing appears tampered with.",
        "Red handle was found detached.",
        "Emergency system was triggered unexpectedly.",
    ],
}

TARGETED_ROOM_CLUES = {
    "Platform A": [
        "Crowd movement marks near platform edge.",
        "Ticket stub trail leads here.",
    ],
    "Control Room": [
        "Screens flickered unexpectedly.",
        "Override keys were recently used.",
    ],
    "Train Yard": [
        "Rail switches were adjusted manually.",
        "Oil stains form a path across tracks.",
    ],
    "Service Corridor": [
        "Foot traffic is unusually heavy here.",
        "Emergency lights are malfunctioning.",
    ],
    "Elevated Bridge": [
        "Wind disturbed loose debris.",
        "Safety rail shows fresh scratches.",
    ],
    "Storage Depot": [
        "Crates were moved out of alignment.",
        "Inventory list is partially missing.",
    ],
}

LEVEL2_DATA = {
    "suspects": SUSPECTS,
    "weapons": WEAPONS,
    "rooms": ROOMS
}

def get_virtual_mouse_pos():
    display = pygame.display.get_surface()
    if display is None:
        return pygame.mouse.get_pos()

    sw, sh = display.get_size()
    mx, my = pygame.mouse.get_pos()

    scale = max(sw / V_W, sh / V_H)
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


def show_level2_instructions(screen, present):
    title_font = pygame.font.Font("freesansbold.ttf", 38)
    text_font = pygame.font.Font("freesansbold.ttf", 22)
    button_font = pygame.font.Font("freesansbold.ttf", 24)

    start_button = pygame.Rect(V_W // 2 - 140, 500, 280, 55)

    lines = [
        "Run across moving trains and collect clues.",
        "Every 4 boxes collected reveals a deduction clue.",
        "Jump between train cars and avoid falling into gaps.",
        "Watch out for birds and tunnel hazards.",
        "Press UP or SPACE to jump.",
        "Press DOWN to duck under obstacles.",
    ]

    # 🌫️ subway ambience variables
    flicker = 0
    flicker_on = True

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

        # 🚇 DARK SUBWAY BASE BACKGROUND
        screen.fill((8, 10, 18))

        # 🌫️ flickering tunnel light effect
        flicker += 1
        if flicker % 20 == 0:
            flicker_on = not flicker_on

        if flicker_on:
            glow = pygame.Surface((V_W, V_H), pygame.SRCALPHA)
            pygame.draw.circle(glow, (40, 70, 120, 40), (V_W // 2, 200), 350)
            screen.blit(glow, (0, 0))

        # 🚇 TITLE PANEL
        title_box = pygame.Rect(0, 40, 680, 85)
        title_box.centerx = V_W // 2

        pygame.draw.rect(screen, (12, 18, 40), title_box, border_radius=14)
        pygame.draw.rect(screen, (60, 100, 180), title_box, 2, border_radius=14)

        title = title_font.render("Level 2: Subway Protocol", True, (235, 235, 245))
        screen.blit(title, title.get_rect(center=title_box.center))

        # 📜 INSTRUCTION PANEL (darker, tighter, cleaner)
        panel = pygame.Rect(0, 150, 780, 280)
        panel.centerx = V_W // 2

        pygame.draw.rect(screen, (10, 12, 22), panel, border_radius=16)
        pygame.draw.rect(screen, (70, 90, 140), panel, 2, border_radius=16)

        # header
        header = text_font.render("SUBWAY INCIDENT BRIEFING", True, (180, 200, 230))
        screen.blit(header, (panel.left + 20, panel.top + 10))

        # text
        y = panel.top + 55
        for line in lines:
            txt = text_font.render("• " + line, True, (210, 210, 220))
            screen.blit(txt, (panel.left + 25, y))
            y += 38

        # 🕯️ footer hint
        hint = text_font.render(
            "Something moves beneath the rails... stay alert.",
            True,
            (150, 160, 180)
        )
        screen.blit(hint, hint.get_rect(center=(V_W // 2, panel.bottom + 30)))

        # 🔘 START BUTTON
        color = (60, 110, 180) if start_button.collidepoint(mouse_pos) else (40, 70, 130)

        pygame.draw.rect(screen, color, start_button, border_radius=10)
        pygame.draw.rect(screen, (200, 220, 255), start_button, 2, border_radius=10)

        txt = button_font.render("ENTER TUNNELS", True, (255, 255, 255))
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
                        result = show_level_complete(screen, present)

                        if result == "exit":
                            return "exit"

                        if result == "next":
                            return "solved"

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

def reset_level():
    solution_suspect, solution_weapon, solution_room = generate_solution()

    return {
        "solution": (solution_suspect, solution_weapon, solution_room),
        "used_clues": {"suspect": set(), "weapon": set(), "room": set()},
        "collectibles": [],
        "birds": [],
        "ramps": [],
        "trains": [],
        "squares_collected": 0,
        "collected_clues": []
    }

def run_level2(SCREEN, present):
    if not show_level2_instructions(SCREEN, present):
        return False

    state = reset_level()

    solution_suspect, solution_weapon, solution_room = state["solution"]
    collected_clues = []
    used_clues = state["used_clues"]
    collectibles = state["collectibles"]
    birds = state["birds"]
    ramps = state["ramps"]
    trains = state["trains"]
    squares_collected = state["squares_collected"]
    collected_clues.clear()


    GAME_SPEED = 16
    FPS = 30
    COUNTDOWN_MS = 3000

    GROUND_DRAW_Y = 470
    GRAVITY = 1.3
    JUMP_VEL = -18
    TRAIN_HEIGHT = 220

    BASE_DIR = os.path.dirname(__file__)
    ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
    ASSETS_DIR = os.path.join(ROOT_DIR, "Assets")
    DETECTIVE_DIR = os.path.join(ASSETS_DIR, "Detective")

    def load_img(path, scale=None):
        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img

    RUN_SCALE = (140, 140)
    DUCK_SCALE = (140, 100)

    RUNNING = [
        load_img(os.path.join(DETECTIVE_DIR, "run1.png"), RUN_SCALE),
        load_img(os.path.join(DETECTIVE_DIR, "run2.png"), RUN_SCALE),
    ]
    JUMPING = load_img(os.path.join(DETECTIVE_DIR, "jump.png"), RUN_SCALE)

    duck1 = os.path.join(DETECTIVE_DIR, "duck1.png")
    duck2 = os.path.join(DETECTIVE_DIR, "duck2.png")
    duck_single = os.path.join(DETECTIVE_DIR, "duck.png")

    if os.path.exists(duck1) and os.path.exists(duck2):
        DUCKING = [
            load_img(duck1, DUCK_SCALE),
            load_img(duck2, DUCK_SCALE),
        ]
    else:
        duck_img = load_img(duck_single, DUCK_SCALE)
        DUCKING = [duck_img, duck_img]

    font_big = pygame.font.Font("freesansbold.ttf", 34)

    CLUE_IMG_PATH = os.path.join("Assets", "Level3", "clue.png")
    CLUE_IMG = pygame.image.load(CLUE_IMG_PATH).convert_alpha()
    CLUE_IMG = pygame.transform.scale(CLUE_IMG, (55, 55))

    SUS_IMG_PATH = os.path.join("Assets", "Level3", "board.png")
    SUS_IMG_RAW = pygame.image.load(SUS_IMG_PATH).convert_alpha()
    SUS_IMG_RAW = pygame.transform.scale(SUS_IMG_RAW, (66, 66))

    bg_track_rows = [GROUND_DRAW_Y - 210, GROUND_DRAW_Y - 150]
    bg_trains = []

    bg_env_scroll = 0
    BG_ENV_SPEED = 1
    front_track_scroll = 0
    FRONT_TRACK_SPEED = GAME_SPEED
    lamp_scroll = 0
    LAMP_SPEED = 10

    clouds = []
    for _ in range(7):
        clouds.append({
            "x": random.randint(0, V_W),
            "y": random.randint(25, 140),
            "w": random.randint(70, 140),
            "h": random.randint(28, 50),
            "speed": random.uniform(0.2, 0.6),
        })

    for row_index, row_y in enumerate(bg_track_rows):
        train_h = 52 if row_index == 0 else 60
        positions = [40, 430] if row_index == 0 else [180, 620]

        for px in positions:
            bg_trains.append({
                "x": px,
                "y": row_y,
                "w": random.randint(150, 210) if row_index == 0 else random.randint(170, 230),
                "h": train_h,
                "row_index": row_index,
                "color": random.choice([(70, 70, 90), (65, 75, 95), (75, 65, 85)]),
            })

    def update_clouds():
        for cloud in clouds:
            cloud["x"] -= cloud["speed"]
            if cloud["x"] + cloud["w"] < -20:
                cloud["x"] = V_W + random.randint(20, 120)
                cloud["y"] = random.randint(25, 140)
                cloud["w"] = random.randint(70, 140)
                cloud["h"] = random.randint(28, 50)
                cloud["speed"] = random.uniform(0.2, 0.6)

    def draw_subway_background():
        for y in range(230):
            color = (135, max(150, 206 - y // 3), max(120, 235 - y // 2))
            pygame.draw.line(SCREEN, color, (0, y), (V_W, y))

        pygame.draw.rect(SCREEN, (70, 70, 80), (0, 230, V_W, V_H - 230))

        for i in range(0, V_W, 140):
            h = [70, 90, 120, 150][(i // 140) % 4]
            pygame.draw.rect(SCREEN, (150, 170, 200), (i, 230 - h, 90, h))

        for cloud in clouds:
            x = int(cloud["x"])
            y = int(cloud["y"])
            w = int(cloud["w"])
            h = int(cloud["h"])
            pygame.draw.ellipse(SCREEN, (245, 248, 255), (x, y, w, h))
            pygame.draw.ellipse(SCREEN, (245, 248, 255), (x + w // 5, y - h // 3, w // 2, h))
            pygame.draw.ellipse(SCREEN, (245, 248, 255), (x + w // 2, y - h // 4, w // 2, h))

        for row_y in bg_track_rows:
            rail1 = row_y + 40
            rail2 = row_y + 56

            pygame.draw.line(SCREEN, (120, 120, 135), (0, rail1), (V_W, rail1), 2)
            pygame.draw.line(SCREEN, (120, 120, 135), (0, rail2), (V_W, rail2), 2)

            for x in range(-64, V_W + 64, 64):
                sx = x - bg_env_scroll
                pygame.draw.rect(SCREEN, (85, 62, 48), (sx, rail1 - 3, 22, rail2 - rail1 + 8), border_radius=2)

        for tr in bg_trains:
            body = pygame.Rect(int(tr["x"]), int(tr["y"]), tr["w"], tr["h"])
            pygame.draw.rect(SCREEN, tr["color"], body, border_radius=5)
            pygame.draw.rect(SCREEN, (40, 40, 50), body, 2, border_radius=5)

            roof = pygame.Rect(body.x + 4, body.y + 4, body.w - 8, 8)
            pygame.draw.rect(SCREEN, (50, 50, 60), roof, border_radius=4)

            wx = body.x + 12
            window_w = 20 if tr["row_index"] == 0 else 22
            window_h = 12 if tr["row_index"] == 0 else 14
            gap = 12
            while wx + window_w < body.right - 16:
                pygame.draw.rect(SCREEN, (110, 150, 190), (wx, body.y + 18, window_w, window_h), border_radius=3)
                wx += window_w + gap

        pygame.draw.rect(SCREEN, (68, 68, 78), (0, GROUND_DRAW_Y - 5, V_W, V_H - GROUND_DRAW_Y + 5))

        rail_y1 = GROUND_DRAW_Y - 6
        rail_y2 = GROUND_DRAW_Y + 28

        pygame.draw.line(SCREEN, (180, 180, 195), (0, rail_y1), (V_W, rail_y1), 4)
        pygame.draw.line(SCREEN, (180, 180, 195), (0, rail_y2), (V_W, rail_y2), 4)
        pygame.draw.line(SCREEN, (90, 90, 100), (0, rail_y1 + 4), (V_W, rail_y1 + 4), 2)
        pygame.draw.line(SCREEN, (90, 90, 100), (0, rail_y2 + 4), (V_W, rail_y2 + 4), 2)

        for x in range(-90, V_W + 90, 90):
            sx = x - front_track_scroll
            pygame.draw.rect(SCREEN, (95, 70, 52), (sx, rail_y1 - 6, 42, rail_y2 - rail_y1 + 18), border_radius=2)

        for x in range(-500, V_W + 500, 500):
            px = x - lamp_scroll
            pygame.draw.line(SCREEN, (90, 90, 110), (px, 110), (px, GROUND_DRAW_Y), 6)
            pygame.draw.line(SCREEN, (90, 90, 110), (px, 110), (px + 75, 110), 6)

    class Detective:
        X_POS = 80

        def __init__(self):
            self.duck_img = DUCKING
            self.run_img = RUNNING
            self.jump_img = JUMPING
            self.ducking = False
            self.running = True
            self.jumping = False
            self.step_index = 0
            self.vel_y = 0
            self.y = float(GROUND_DRAW_Y - RUN_SCALE[1])
            self.image = self.run_img[0]
            self.rect = self.image.get_rect(topleft=(self.X_POS, int(self.y)))

        def start_jump(self):
            if not self.jumping:
                self.jumping = True
                self.running = False
                self.ducking = False
                self.vel_y = JUMP_VEL

        def update(self, keys):
            if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and not self.jumping:
                self.start_jump()

            self.ducking = keys[pygame.K_DOWN] and not self.jumping
            self.running = not self.ducking and not self.jumping

            if self.jumping:
                self.y += self.vel_y
                self.vel_y += GRAVITY

            if self.running or self.ducking:
                self.step_index += 1
                if self.step_index >= 10:
                    self.step_index = 0

            old_x = self.rect.x
            old_bottom = self.rect.bottom

            if self.jumping:
                self.image = self.jump_img
                self.rect = self.image.get_rect()
                self.rect.x = old_x
                self.rect.y = int(self.y)
            elif self.ducking:
                self.image = self.duck_img[self.step_index // 5]
                self.rect = self.image.get_rect()
                self.rect.x = old_x
                self.rect.bottom = old_bottom
                self.y = self.rect.y
            else:
                self.image = self.run_img[self.step_index // 5]
                self.rect = self.image.get_rect()
                self.rect.x = old_x
                self.rect.bottom = old_bottom
                self.y = self.rect.y

        def land_on(self, surface_y):
            self.jumping = False
            self.vel_y = 0
            self.rect.bottom = int(surface_y)
            self.y = self.rect.y

        def stick_to_surface(self, surface_y):
            if not self.jumping:
                self.rect.bottom = int(surface_y)
                self.y = self.rect.y

        def draw(self):
            SCREEN.blit(self.image, (self.rect.x, self.rect.y))

    class Ramp:
        def __init__(self, x, width, height, direction="up"):
            self.x = x
            self.width = width
            self.height = height
            self.direction = direction

        def update(self):
            self.x -= GAME_SPEED

        def offscreen(self):
            return self.x + self.width < 0

        def contains_x(self, x):
            return self.x <= x <= self.x + self.width

        def surface_y_at(self, x):
            t = (x - self.x) / self.width
            t = max(0, min(1, t))
            if self.direction == "up":
                return GROUND_DRAW_Y - (t * self.height)
            return (GROUND_DRAW_Y - self.height) + (t * self.height)

        def draw(self):
            if self.direction == "up":
                pts = [(self.x, GROUND_DRAW_Y), (self.x + self.width, GROUND_DRAW_Y), (self.x + self.width, GROUND_DRAW_Y - self.height)]
            else:
                pts = [(self.x, GROUND_DRAW_Y), (self.x, GROUND_DRAW_Y - self.height), (self.x + self.width, GROUND_DRAW_Y)]
            pygame.draw.polygon(SCREEN, (145, 145, 160), pts)
            pygame.draw.polygon(SCREEN, (60, 60, 70), pts, 3)

    class Train:
        def __init__(self, x, width, height, color, allow_birds=True):
            self.x = x
            self.width = width
            self.height = height
            self.color = color
            self.allow_birds = allow_birds

        def update(self):
            self.x -= GAME_SPEED

        def offscreen(self):
            return self.x + self.width < 0

        def contains_x(self, x):
            return self.x <= x <= self.x + self.width

        def surface_y_at(self, _x):
            return GROUND_DRAW_Y - self.height

        def draw(self):
            rect = pygame.Rect(self.x, GROUND_DRAW_Y - self.height + 8, self.width, self.height)
            pygame.draw.rect(SCREEN, self.color, rect, border_radius=8)
            pygame.draw.rect(SCREEN, (40, 40, 50), rect, 3, border_radius=8)
            pygame.draw.rect(SCREEN, (55, 55, 68), (rect.x + 4, rect.y + 4, rect.width - 8, 14), border_radius=6)

            window_w = 115
            window_h = 80
            gap = 14
            wx = rect.x + 20
            wy = rect.y + 42
            while wx + window_w < rect.right - 20:
                pygame.draw.rect(SCREEN, (140, 220, 255), (wx, wy, window_w, window_h), border_radius=4)
                pygame.draw.rect(SCREEN, (40, 40, 50), (wx, wy, window_w, window_h), 2, border_radius=4)
                wx += window_w + gap

            pygame.draw.line(SCREEN, (55, 55, 65), (rect.x + 6, rect.bottom - 14), (rect.right - 6, rect.bottom - 14), 4)

            for cx in [rect.x + 40, rect.centerx, rect.right - 40]:
                pygame.draw.circle(SCREEN, (30, 30, 35), (cx, rect.bottom - 6), 10)

            pygame.draw.circle(SCREEN, (255, 245, 180), (rect.x + 14, rect.y + rect.height // 2), 5)
            pygame.draw.circle(SCREEN, (255, 245, 180), (rect.x + 14, rect.y + rect.height // 2 + 20), 5)

    class WhiteSquare:
        def __init__(self, image, x, y):
            self.image = image
            self.rect = self.image.get_rect(
                topleft=(
                    V_W + random.randint(150, 500),
                    random.randint(120, 240)
                )
            )

        def update(self):
            self.rect.x -= GAME_SPEED

        def draw(self, screen):
            screen.blit(self.image, self.rect)

    class SusObstacle:
        def __init__(self, x):
            self.x = x
            self.width = 55
            self.height = 55

            self.y = GROUND_DRAW_Y - self.height  # ✅ always on ground

            self.image = pygame.transform.scale(SUS_IMG_RAW, (self.width, self.height))
            self.rect = self.image.get_rect(topleft=(self.x, self.y))

        def update(self):
            self.x -= GAME_SPEED
            self.rect.x = int(self.x)

        def draw(self, screen, player_x):
            distance = self.x - player_x  # only care when ahead

            fade_start = 500 # when it STARTS appearing
            fade_end = 170     # when it's fully visible

            if distance > fade_start:
                visibility = 0  # completely invisible
            elif distance > fade_end:
                # smooth fade between start and end
                t = (fade_start - distance) / (fade_start - fade_end)
                visibility = int(255 * t)
            else:
                visibility = 255  # fully visible

            img = self.image.copy()
            img.set_alpha(visibility)

            screen.blit(img, (self.x, self.y))

        def offscreen(self):
            return self.x + self.width < 0

    class Bird:
        def __init__(self, x, y):
            self.rect = pygame.Rect(x, y, 80, 55)
            self.step = 0
            self.frame = 0

        def update(self):
            self.rect.x -= GAME_SPEED + 3
            self.step += 1
            if self.step >= 6:
                self.frame = (self.frame + 1) % 2
                self.step = 0

        def draw(self):
            x = self.rect.x
            y = self.rect.y
            body_color = (20, 20, 20)
            wing_color = (0, 0, 0)
            eye_color = (220, 220, 220)
            beak_color = (210, 170, 60)

            body_rect = pygame.Rect(x + 20, y + 18, 34, 20)
            pygame.draw.ellipse(SCREEN, body_color, body_rect)
            pygame.draw.circle(SCREEN, body_color, (x + 24, y + 22), 9)
            pygame.draw.polygon(SCREEN, beak_color, [(x + 17, y + 21), (x + 6, y + 24), (x + 17, y + 27)])
            pygame.draw.circle(SCREEN, eye_color, (x + 21, y + 20), 2)

            if self.frame == 0:
                left_wing = [(x + 42, y + 24), (x + 60, y + 8), (x + 50, y + 26)]
                right_wing = [(x + 30, y + 24), (x + 44, y + 6), (x + 22, y + 22)]
            else:
                left_wing = [(x + 42, y + 26), (x + 60, y + 38), (x + 50, y + 28)]
                right_wing = [(x + 30, y + 26), (x + 44, y + 40), (x + 22, y + 28)]

            pygame.draw.polygon(SCREEN, wing_color, left_wing)
            pygame.draw.polygon(SCREEN, wing_color, right_wing)
            pygame.draw.polygon(SCREEN, body_color, [(x + 54, y + 24), (x + 68, y + 20), (x + 66, y + 30)])

    def get_surface_y_at(x_pos, ramps, trains):
        candidates = [GROUND_DRAW_Y]
        for tr in trains:
            if tr.contains_x(x_pos):
                candidates.append(tr.surface_y_at(x_pos))
        for r in ramps:
            if r.contains_x(x_pos):
                candidates.append(r.surface_y_at(x_pos))
        return min(candidates)

    def get_train_surface_y_at(x_pos, trains):
        candidates = []
        for tr in trains:
            if tr.contains_x(x_pos):
                candidates.append(tr.surface_y_at(x_pos))
        return min(candidates) if candidates else None
    
    def is_on_ground_only(x_pos, ramps, trains):
        # block ramps
        for r in ramps:
            if r.contains_x(x_pos):
                return False

        # block ALL train influence zones
        for tr in trains:
            margin = 80  # stronger safety buffer
            if (tr.x - margin) <= x_pos <= (tr.x + tr.width + margin):
                return False

        return True

    def get_safe_train_at(x_pos, trains, margin=170):
        for tr in trains:
            if tr.allow_birds and (tr.x + margin) <= x_pos <= (tr.x + tr.width - margin):
                return tr
        return None

    def is_over_any_train_gap(x_pos, trains, max_gap=140):
        trains_sorted = sorted(trains, key=lambda t: t.x)
        for i in range(len(trains_sorted) - 1):
            left_train = trains_sorted[i]
            right_train = trains_sorted[i + 1]
            gap_start = left_train.x + left_train.width
            gap_end = right_train.x
            gap_width = gap_end - gap_start
            if 0 < gap_width <= max_gap and gap_start <= x_pos <= gap_end:
                return True
        return False

    def spawn_course_segment(start_x):
        ramps_new = []
        trains_new = []

        section_type = random.choice(["ground_section", "jump_section"])
        color_choices = [(190, 55, 55), (55, 100, 185), (55, 145, 95)]

        if section_type == "ground_section":
            ramp_w = random.randint(220, 280)
            ramp_h = TRAIN_HEIGHT
            train_w = random.randint(850, 1150)
            ground_gap_before = random.randint(180, 320)
            ground_gap_after = random.randint(GAME_SPEED * FPS * 2, GAME_SPEED * FPS * 3)

            x = start_x + ground_gap_before
            ramps_new.append(Ramp(x, ramp_w, ramp_h, "up"))
            x += ramp_w
            trains_new.append(Train(x, train_w, TRAIN_HEIGHT, random.choice(color_choices), allow_birds=True))
            x += train_w
            ramps_new.append(Ramp(x, ramp_w, ramp_h, "down"))
            x += ramp_w
            end_x = x + ground_gap_after

        else:
            ramp_w = random.randint(220, 280)
            ramp_h = TRAIN_HEIGHT
            num_trains = random.randint(2, 3)
            ground_gap_before = random.randint(180, 320)
            ground_gap_after = random.randint(GAME_SPEED * FPS * 2, GAME_SPEED * FPS * 3)

            current_x = start_x + ground_gap_before
            ramps_new.append(Ramp(current_x, ramp_w, ramp_h, "up"))
            current_x += ramp_w

            for i in range(num_trains):
                train_w = random.randint(600, 850)
                trains_new.append(Train(current_x, train_w, TRAIN_HEIGHT, random.choice(color_choices), allow_birds=False))
                current_x += train_w

                if i < num_trains - 1:
                    jump_gap = random.randint(95, 125)
                    current_x += jump_gap

            ramps_new.append(Ramp(current_x, ramp_w, ramp_h, "down"))
            current_x += ramp_w
            end_x = current_x + ground_gap_after

        return ramps_new, trains_new, end_x

    clock = pygame.time.Clock()
    player = Detective()


    countdown_start = pygame.time.get_ticks()

    collectibles = []
    birds = []
    sus_obstacles = []
    sus_timer = 0
    ramps = []
    trains = []
    squares_collected = 0

    next_course_x = V_W + 200
    for _ in range(4):
        r_new, tr_new, next_course_x = spawn_course_segment(next_course_x)
        ramps.extend(r_new)
        trains.extend(tr_new)

    collectible_timer = 0
    bird_timer = 0
    finish_timer = 0

    while True:
        bg_env_scroll = (bg_env_scroll + BG_ENV_SPEED) % 64
        front_track_scroll = (front_track_scroll + FRONT_TRACK_SPEED) % 90
        lamp_scroll = (lamp_scroll + LAMP_SPEED) % 500
        update_clouds()

        countdown_active = (pygame.time.get_ticks() - countdown_start) < COUNTDOWN_MS
        next_course_x -= GAME_SPEED

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "exit"

        keys = pygame.key.get_pressed()
        draw_subway_background()

        while next_course_x < V_W + 1600:
            r_new, tr_new, next_course_x = spawn_course_segment(next_course_x)
            ramps.extend(r_new)
            trains.extend(tr_new)

        for r in ramps[:]:
            r.update()
            r.draw()
            if r.offscreen():
                ramps.remove(r)

        for tr in trains[:]:
            tr.update()
            tr.draw()
            if tr.offscreen():
                trains.remove(tr)

        collectible_timer += 1
        if not countdown_active and collectible_timer >= 55 and len(collectibles) < 2:
            collectible_timer = 0
            spawn_x = V_W + random.randint(150, 500)

            if not is_on_ground_only(spawn_x, ramps, trains):
                continue

            y = GROUND_DRAW_Y - 55

            collectibles.append(WhiteSquare(CLUE_IMG, spawn_x, y))

        for sq in collectibles[:]:
            sq.update()
            sq.draw(SCREEN)

            if sq.rect.right < 0:
                collectibles.remove(sq)
                continue

            if not countdown_active and player.rect.colliderect(sq.rect):
                collectibles.remove(sq)
                squares_collected += 1

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

        bird_timer += 1

        if not countdown_active and bird_timer >= 20:
            bird_timer = 0
            spawn_x = V_W + random.randint(140, 260)
            safe_train = get_safe_train_at(spawn_x, trains, margin=130)

            if safe_train is not None:
                train_surface = safe_train.surface_y_at(spawn_x)
                bird_y = int(train_surface - random.randint(160, 175))
                birds.append(Bird(spawn_x, bird_y))

        for bird in birds[:]:
            bird.update()
            bird.draw()

            if bird.rect.right < 0:
                birds.remove(bird)
                continue

            if not countdown_active and player.rect.colliderect(bird.rect):
                death_screen(SCREEN, present)
                result = guessing_screen(
                    SCREEN,
                    present,
                    collected_clues,
                    solution_suspect,
                    solution_weapon,
                    solution_room
                )
                if result == "solved":
                    return "win"

                if result == "exit":
                    return "exit"
                
                if result is False:
                    return False 

        sus_timer += 1
        if not countdown_active and sus_timer >= 180:
            sus_timer = 0

            # try multiple times to find a valid ground spot
            for _ in range(5):
                spawn_x = V_W + random.randint(150, 1200)

                if is_on_ground_only(spawn_x, ramps, trains):
                    sus_obstacles.append(SusObstacle(spawn_x))
                    break

        for s in sus_obstacles[:]:
            s.update()
            s.draw(SCREEN, player.rect.x)

            if s.offscreen():
                sus_obstacles.remove(s)

            if not countdown_active and player.rect.colliderect(s.rect):
                death_screen(SCREEN, present)
                result = guessing_screen(
                    SCREEN,
                    present,
                    collected_clues,
                    solution_suspect,
                    solution_weapon,
                    solution_room
                )

                if result == "solved":
                    return "win"
                if result == "exit":
                    return "exit"
                if result is False:
                    return False 
            
        if not countdown_active:
            player.update(keys)

        previous_on_train = player.rect.bottom < GROUND_DRAW_Y - 5
        player_surface_y = get_surface_y_at(player.rect.centerx, ramps, trains)

        if (
            previous_on_train
            and not player.jumping
            and player_surface_y == GROUND_DRAW_Y
            and is_over_any_train_gap(player.rect.centerx, trains, max_gap=140)
        ):
            death_screen(SCREEN, present)
            result = guessing_screen(
                    SCREEN,
                    present,
                    collected_clues,
                    solution_suspect,
                    solution_weapon,
                    solution_room
                )
            if result == "solved":
                return "win"

            if result == "exit":
                return "exit"

            if result is False:
                return False 
            

        if not player.jumping:
            player.stick_to_surface(player_surface_y)
        else:
            if player.vel_y >= 0 and player.rect.bottom >= player_surface_y:
                if (
                player_surface_y == GROUND_DRAW_Y
                and is_over_any_train_gap(player.rect.centerx, trains, max_gap=140)
            ):
                 death_screen(SCREEN, present)
                 result = guessing_screen(
                    SCREEN,
                    present,
                    collected_clues,
                    solution_suspect,
                    solution_weapon,
                    solution_room
                 )

                 if result == "solved":
                     return "win"

                 if result == "exit":
                     return "exit"
                 
                 if result is False:
                     return False 

                player.land_on(player_surface_y)

        player.draw()
        draw_clue_box(SCREEN, len(collected_clues))

        if countdown_active:
            draw_countdown(SCREEN, countdown_start)

        present()
        clock.tick(FPS)


def show_level_complete(screen, present):
    font_big = pygame.font.Font("freesansbold.ttf", 64)
    font = pygame.font.Font("freesansbold.ttf", 28)

    button = pygame.Rect(V_W // 2 - 120, V_H // 2 + 80, 240, 60)

    while True:
        mouse = get_virtual_mouse_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.collidepoint(mouse):
                    return "next"

        # 🌑 FULL SCREEN CLEAN WIN PAGE
        draw_gradient(screen, (5, 5, 10), (0, 0, 0))

        # 🕯️ subtle glow center
        glow = pygame.Surface((V_W, V_H), pygame.SRCALPHA)
        pygame.draw.circle(glow, (80, 120, 200, 40), (V_W//2, V_H//2), 260)
        screen.blit(glow, (0, 0))

        title = font_big.render("CASE SOLVED", True, (240, 240, 240))
        screen.blit(title, title.get_rect(center=(V_W // 2, V_H // 2 - 60)))

        sub = font.render(
            "The truth has been uncovered.",
            True,
            (180, 180, 200)
        )
        screen.blit(sub, sub.get_rect(center=(V_W // 2, V_H // 2)))

        pygame.draw.rect(screen, (70, 140, 90), button, border_radius=12)
        txt = font.render("CONTINUE", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=button.center))

        present()




if __name__ == "__main__":
    pygame.init()
    SCREEN = pygame.display.set_mode((V_W, V_H))
    pygame.display.set_caption("Level 2 Test")

    def present():
        pygame.display.flip()

    running = True
    game_state = "level2"

    # store these so they persist properly
    collected_clues = []
    solution_suspect, solution_weapon, solution_room = generate_solution()

    while running:

        if game_state == "level2":
            result = run_level2(SCREEN, present)

            if result == "exit":
                running = False

            elif result == "level_complete":
                print("Level completed 🚀")
                game_state = "level2"  # or go to guessing if needed

    pygame.quit()