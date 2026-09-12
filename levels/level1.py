from turtle import Screen

import pygame
import random
import sys
import os

from death import death_screen

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import CLOCK, draw_gradient

V_W = 1100
V_H = 600
FPS = 30

GAME_SPEED = 16
DECOR_SPEED = 8
JUMP_DROP_VEL = 9

GROUND_Y = 370
GROUND_DRAW_Y = GROUND_Y + 20

LIVING_ROOM_DURATION_MS = 12000
KITCHEN_DURATION_MS = 10000
BEDROOM_DURATION_MS = 10000
BATHROOM_DURATION_MS = 10000
LEVEL_DURATION_MS = (
    LIVING_ROOM_DURATION_MS
    + KITCHEN_DURATION_MS
    + BEDROOM_DURATION_MS
    + BATHROOM_DURATION_MS
)

PLAYER_GROUND_OFFSET = 58
COUNTDOWN_MS = 3000
ROOM_MESSAGE_DURATION = 1500

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
DETECTIVE_DIR = os.path.join(ASSETS_DIR, "Detective")
LEVEL1_BG_DIR = os.path.join(ASSETS_DIR, "Level1", "Background")
LIVINGROOM_DIR = os.path.join(ASSETS_DIR, "Level1", "LivingRoom")


SUSPECTS = [
    "Mother",
    "Father",
    "Best Friend",
    "Uncle",
    "Aunt",
    "Maid"
]

WEAPONS = [
    "Kitchen Pan",
    "Glass Bottle",
    "Metal Lamp",
    "Wooden Chair Leg",
    "Iron Doorstop",
    "Thick Curtain Cord",
]

ROOMS = [
    "Hall",
    "Dining Room",
    "Kitchen",
    "Ballroom",
    "Billiard Room",
    "Library",
]

TARGETED_SUSPECT_CLUES = {
    "Mother": [
        "A neatly folded apron was found near the scene.",
        "Fresh flower scent lingered in the hallway.",
        "A set of house keys was missing from the kitchen hook."
    ],
    "Father": [
        "A torn newspaper with financial notes was found.",
        "Heavy boot prints led out of the study.",
        "A pipe-shaped ash mark was seen on a desk."
    ],
    "Best Friend": [
        "A phone with recent messages was left unlocked.",
        "Sneaker prints were found near the entryway.",
        "A gaming controller was left out mid-use."
    ],
    "Uncle": [
        "A strong cologne scent was detected in the room.",
        "A pocket watch was dropped near the stairs.",
        "A travel bag was found half-packed."
    ],
    "Aunt": [
        "A handbag with lipstick stains was found open.",
        "Perfume notes lingered in the lounge.",
        "A jewelry box was slightly ajar."
    ],
    "Maid": [
        "Cleaning gloves were found near a spill.",
        "A mop bucket was left unusually positioned.",
        "A uniform button was found on the floor."
    ]
}

TARGETED_WEAPON_CLUES = {
    "Kitchen Pan": [
        "A dented cookware item was missing from the kitchen rack.",
        "Grease marks were found near the impact area.",
        "The strike pattern suggests a heavy cooking utensil.",
        "A loud metallic clang was reported from nearby."
    ],

    "Glass Bottle": [
        "Shards were found scattered with a recent break pattern.",
        "A drink bottle was missing from a nearby table.",
        "Liquid residue was found on the floor.",
        "The fracture lines suggest a thrown object."
    ],

    "Metal Lamp": [
        "A lighting fixture appears to have been removed forcefully.",
        "Scratches were found near a power outlet.",
        "A heavy object with electrical components is missing.",
        "The impact zone suggests a solid household decor item."
    ],

    "Wooden Chair Leg": [
        "A broken piece of furniture was found nearby.",
        "Wood splinters were scattered across the floor.",
        "A chair appears to have been partially dismantled.",
        "The strike marks match a blunt wooden object."
    ],

    "Iron Doorstop": [
        "A heavy door fixture is missing from its usual place.",
        "Scrape marks were found near a doorway edge.",
        "The impact zone suggests a compact metal object.",
        "A door was left unusually ajar after the incident."
    ],

    "Thick Curtain Cord": [
        "Fabric tension marks were found near a window area.",
        "A curtain tie was missing from a nearby room.",
        "The fibers suggest pressure applied over time.",
        "A looping pattern was found inconsistent with normal use."
    ]
}

TARGETED_ROOM_CLUES = {
    "Hall": [
        "Footsteps echoed longer than expected in the corridor.",
        "Dust patterns show someone paced back and forth."
    ],

    "Dining Room": [
        "Chairs were shifted slightly away from the table.",
        "A plate was broken but recently cleaned up."
    ],
    "Kitchen": [
        "Water was spilled but not fully wiped.",
        "Cabinet doors were left slightly open."
    ],
    "Ballroom": [
        "Scratch marks suggest hurried movement.",
        "A curtain swayed as if recently brushed past."
    ], 
    "Billiard Room": [
        "Balls were not aligned as if recently used.",
        "Cue sticks were slightly out of place."
    ],
    "Library": [
        "Books were pulled out but not returned properly.",
        "A ladder was moved but not put back."
    ]
}

LEVEL1_DATA = {
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


def guessing_screen(screen, present, collected_clues,
                    solution_suspect, solution_weapon, solution_room,
                    suspects, weapons, rooms):
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

        suspect_rects = draw_buttons(suspects, 50, 200, "suspect")
        weapon_rects = draw_buttons(weapons, 50, 260, "weapon")
        room_rects = draw_buttons(rooms, 50, 320, "room")

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
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

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
                        if (selected["suspect"] == solution_suspect and
                            selected["weapon"] == solution_weapon and
                            selected["room"] == solution_room):
                            return "win"
                        else:
                            return "wrong"

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


def trim_transparent(img):
    rect = img.get_bounding_rect()
    if rect.width == 0 or rect.height == 0:
        return img
    return img.subsurface(rect).copy()


def load_img(path, scale=None, trim_alpha=True):
    img = pygame.image.load(path).convert_alpha()
    if trim_alpha:
        img = trim_transparent(img)
    if scale:
        img = pygame.transform.smoothscale(img, scale)
    return img


def safe_load(path, scale=None, trim_alpha=True):
    try:
        return load_img(path, scale, trim_alpha=trim_alpha)
    except Exception:
        return None


def draw_room_background(screen, room_name):
    if room_name == "Living Room":
        wall_color = (245, 240, 235)
        floor_color = (92, 64, 51)
        floor_line_color = (70, 45, 30)
    elif room_name == "Kitchen":
        wall_color = (236, 241, 235)
        floor_color = (180, 180, 180)
        floor_line_color = (150, 150, 150)
    elif room_name == "Bedroom":
        wall_color = (235, 228, 242)
        floor_color = (120, 85, 70)
        floor_line_color = (95, 65, 55)
    else:
        wall_color = (222, 236, 242)
        floor_color = (198, 208, 214)
        floor_line_color = (170, 180, 188)

    screen.fill(wall_color)
    pygame.draw.rect(screen, (255, 255, 255), (0, GROUND_DRAW_Y - 10, V_W, 10))
    pygame.draw.rect(screen, floor_color, (0, GROUND_DRAW_Y, V_W, V_H - GROUND_DRAW_Y))

    if room_name in ["Kitchen", "Bathroom"]:
        for x in range(0, V_W, 40):
            pygame.draw.line(screen, floor_line_color, (x, GROUND_DRAW_Y), (x, V_H), 1)
        for y in range(GROUND_DRAW_Y, V_H, 40):
            pygame.draw.line(screen, floor_line_color, (0, y), (V_W, y), 1)
    else:
        for y in range(GROUND_DRAW_Y, V_H, 18):
            pygame.draw.line(screen, floor_line_color, (0, y), (V_W, y), 1)


def draw_countdown(screen, countdown_start):
    elapsed = pygame.time.get_ticks() - countdown_start
    remaining = 3 - (elapsed // 1000)
    if remaining > 0:
        font = pygame.font.Font("freesansbold.ttf", 90)
        text = font.render(str(remaining), True, (20, 20, 20))
        rect = text.get_rect(center=(V_W // 2, V_H // 2))
        screen.blit(text, rect)



def draw_room_transition(screen, message, start_time):
    elapsed = pygame.time.get_ticks() - start_time
    if elapsed < ROOM_MESSAGE_DURATION:
        font = pygame.font.Font("freesansbold.ttf", 32)
        text = font.render(message, True, (30, 30, 30))
        rect = text.get_rect(center=(V_W // 2, V_H // 2))
        screen.blit(text, rect)


def show_level1_instructions(screen, present):
    title_font = pygame.font.Font("freesansbold.ttf", 40)
    text_font = pygame.font.Font("freesansbold.ttf", 20)
    small_font = pygame.font.Font("freesansbold.ttf", 16)
    button_font = pygame.font.Font("freesansbold.ttf", 22)

    start_button = pygame.Rect(V_W // 2 - 130, 520, 260, 50)

    lines = [
        "Collect clues hidden throughout the house.",
        "Every 4 magnifying glasses reveal a clue.",
        "Avoid furniture and roaming pets.",
        "Watch ceiling hazards like hanging lamps.",
        "UP jump",
        "DOWN duck",
        "Think like a detective, not a runner."
    ]

    # ================= INIT =================
    light_timer = 0
    light_alpha = 40

    wall_x = 0
    wall_speed = 0.4

    # ================= LOOP =================
    while True:
        mouse_pos = get_virtual_mouse_pos()

        # ---------------- EVENTS ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(mouse_pos):
                    return True

        # 🌑 MUCH DARKER BACKGROUND
        draw_gradient(screen, (10, 10, 18), (2, 2, 6))

        # 🧱 MOVING WALL DEPTH (kept but subtle)
        wall_x -= wall_speed
        if wall_x <= -V_W:
            wall_x = 0

        pygame.draw.rect(screen, (12, 12, 20), (wall_x, 0, V_W, V_H))
        pygame.draw.rect(screen, (16, 16, 26), (wall_x + V_W, 0, V_W, V_H))

        for i in range(0, V_W, 90):
            pygame.draw.line(screen, (22, 22, 35), (i + wall_x, 0), (i + wall_x, V_H))

        # 🕯️ FLICKERING CANDLE LIGHT (ONLY EFFECT NOW)
        light_timer += 1
        if light_timer % 6 == 0:
            light_alpha = random.randint(18, 50)

        light = pygame.Surface((V_W, V_H), pygame.SRCALPHA)
        pygame.draw.circle(
            light,
            (255, 240, 200, light_alpha),
            (V_W // 2, 180),
            280
        )
        screen.blit(light, (0, 0))

        # 🪵 TITLE BOX
        title_box = pygame.Rect(0, 50, 620, 75)
        title_box.centerx = V_W // 2

        pygame.draw.rect(screen, (35, 35, 50), title_box, border_radius=14)
        pygame.draw.rect(screen, (110, 110, 140), title_box, 2, border_radius=14)

        title = title_font.render("Level 1: Case Briefing", True, (230, 230, 230))
        screen.blit(title, title.get_rect(center=title_box.center))

        # 📦 PANEL (slightly darker too)
        panel = pygame.Rect(0, 150, 760, 260)
        panel.centerx = V_W // 2

        pygame.draw.rect(screen, (12, 12, 18), panel, border_radius=16)
        pygame.draw.rect(screen, (80, 80, 110), panel, 2, border_radius=16)

        header = small_font.render("DETECTIVE NOTES", True, (160, 160, 180))
        screen.blit(header, (panel.left + 20, panel.top + 12))

        y = panel.top + 45
        for line in lines:
            text = text_font.render("• " + line, True, (210, 210, 210))
            screen.blit(text, (panel.left + 25, y))
            y += 30

        # 🧠 FOOTER
        hint = small_font.render(
            "The house feels... too quiet.",
            True,
            (140, 140, 160)
        )
        screen.blit(hint, hint.get_rect(center=(V_W // 2, panel.bottom + 25)))

        # 🔘 BUTTON
        color = (90, 130, 210) if start_button.collidepoint(mouse_pos) else (60, 90, 160)

        pygame.draw.rect(screen, color, start_button, border_radius=10)
        pygame.draw.rect(screen, (220, 220, 220), start_button, 2, border_radius=10)

        txt = button_font.render("ENTER HOUSE", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=start_button.center))

        present()
        CLOCK.tick(30)
        
class Decor:
    def __init__(self, kind, x, room_name, assets=None):
        self.kind = kind
        self.room_name = room_name
        self.x = float(x)
        self.assets = assets or {}
        self.image = None
        self.use_bottom_anchor = False

        if room_name == "Living Room":
            if kind == "couch":
                self.w, self.h = 320, 185
                self.use_bottom_anchor = True
                self.floor_bottom = GROUND_DRAW_Y + 2
                self.rect = pygame.Rect(int(self.x), int(self.floor_bottom - self.h), self.w, self.h)
            elif kind == "frame1":
                self.image = self.assets.get("frame1")
                self.w, self.h = self.image.get_size() if self.image else (190, 130)
                self.y = 170
                self.rect = pygame.Rect(int(self.x), int(self.y - self.h), self.w, self.h)
            elif kind == "frame2":
                self.image = self.assets.get("frame2")
                self.w, self.h = self.image.get_size() if self.image else (350, 200)
                self.y = 200
                self.rect = pygame.Rect(int(self.x), int(self.y - self.h), self.w, self.h)
            else:
                self.w, self.h = 85, 205
                self.use_bottom_anchor = True
                self.floor_bottom = GROUND_DRAW_Y + 2
                self.rect = pygame.Rect(int(self.x), int(self.floor_bottom - self.h), self.w, self.h)

        elif room_name == "Kitchen":
            if kind == "fridge":
                self.w, self.h = 95, 190
                self.y = GROUND_DRAW_Y - 8
            else:
                self.w, self.h = 220, 120
                self.y = GROUND_DRAW_Y - 8
            self.rect = pygame.Rect(int(self.x), int(self.y - self.h), self.w, self.h)

        elif room_name == "Bedroom":
            if kind == "couch":
                self.w, self.h = 320, 185
                self.use_bottom_anchor = True
                self.floor_bottom = GROUND_DRAW_Y + 2
                self.rect = pygame.Rect(int(self.x), int(self.floor_bottom - self.h), self.w, self.h)
            elif kind == "bed":
                self.w, self.h = 290, 130
                self.use_bottom_anchor = True
                self.floor_bottom = GROUND_DRAW_Y + 2
                self.rect = pygame.Rect(int(self.x), int(self.floor_bottom - self.h), self.w, self.h)
            elif kind == "frame1":
                self.image = self.assets.get("frame1")
                self.w, self.h = self.image.get_size() if self.image else (190, 130)
                self.y = 170
                self.rect = pygame.Rect(int(self.x), int(self.y - self.h), self.w, self.h)
            elif kind == "frame2":
                self.image = self.assets.get("frame2")
                self.w, self.h = self.image.get_size() if self.image else (230, 130)
                self.y = 170
                self.rect = pygame.Rect(int(self.x), int(self.y - self.h), self.w, self.h)
            else:
                self.w, self.h = 85, 205
                self.use_bottom_anchor = True
                self.floor_bottom = GROUND_DRAW_Y + 2
                self.rect = pygame.Rect(int(self.x), int(self.floor_bottom - self.h), self.w, self.h)
        else:
            if kind == "toilet":
                self.w, self.h = 95, 120
                self.y = GROUND_DRAW_Y - 8
            else:
                self.w, self.h = 210, 110
                self.y = GROUND_DRAW_Y - 8
            self.rect = pygame.Rect(int(self.x), int(self.y - self.h), self.w, self.h)

    def update(self):
        self.x -= DECOR_SPEED
        self.rect.x = int(self.x)
        if self.use_bottom_anchor:
            self.rect.bottom = int(self.floor_bottom)

    def off_screen(self):
        return self.rect.right < 0

    def draw(self, screen):
        if self.room_name in ["Living Room", "Bedroom"] and self.image is not None and self.kind in ["frame1", "frame2"]:
            screen.blit(self.image, self.rect)
            return

        if self.kind == "floor_lamp":
            x = self.rect.x
            bottom = self.rect.bottom
            pygame.draw.ellipse(screen, (90, 70, 55), (x + 18, bottom - 10, 50, 12))
            pygame.draw.rect(screen, (115, 95, 78), (x + 39, bottom - 165, 8, 155))
            pygame.draw.polygon(screen, (235, 220, 175), [
                (x + 10, bottom - 165),
                (x + 76, bottom - 165),
                (x + 60, bottom - 205),
                (x + 26, bottom - 205)
            ])
            pygame.draw.rect(screen, (165, 145, 120), (x + 31, bottom - 170, 24, 8), border_radius=3)
            return

        if self.room_name in ["Living Room", "Bedroom"]:
            if self.kind == "couch":
                x = self.rect.x
                bottom = self.rect.bottom
                pygame.draw.rect(screen, (132, 94, 74), (x + 18, bottom - 92, 284, 74), border_radius=18)
                pygame.draw.rect(screen, (153, 110, 88), (x + 28, bottom - 100, 124, 34), border_radius=10)
                pygame.draw.rect(screen, (153, 110, 88), (x + 168, bottom - 100, 124, 34), border_radius=10)
                pygame.draw.rect(screen, (164, 120, 97), (x + 36, bottom - 148, 248, 58), border_radius=18)
                pygame.draw.ellipse(screen, (140, 100, 80), (x + 2, bottom - 104, 42, 62))
                pygame.draw.ellipse(screen, (140, 100, 80), (x + 276, bottom - 104, 42, 62))
                pygame.draw.rect(screen, (118, 82, 64), (x + 24, bottom - 32, 272, 16), border_radius=6)
                pygame.draw.rect(screen, (92, 62, 48), (x + 42, bottom - 2, 16, 22), border_radius=2)
                pygame.draw.rect(screen, (92, 62, 48), (x + 262, bottom - 2, 16, 22), border_radius=2)
            elif self.kind == "bed":
                x = self.rect.x
                bottom = self.rect.bottom
                pygame.draw.rect(screen, (120, 82, 64), (x + 8, bottom - 82, 274, 70), border_radius=10)
                pygame.draw.rect(screen, (98, 66, 52), (x + 8, bottom - 118, 24, 106), border_radius=4)
                pygame.draw.rect(screen, (98, 66, 52), (x + 258, bottom - 118, 24, 106), border_radius=4)
                pygame.draw.rect(screen, (214, 211, 226), (x + 24, bottom - 110, 240, 40), border_radius=12)
                pygame.draw.rect(screen, (236, 236, 242), (x + 34, bottom - 122, 56, 26), border_radius=8)
                pygame.draw.rect(screen, (236, 236, 242), (x + 98, bottom - 122, 56, 26), border_radius=8)
                pygame.draw.rect(screen, (190, 170, 198), (x + 28, bottom - 72, 232, 46), border_radius=10)
                pygame.draw.rect(screen, (92, 62, 48), (x + 24, bottom - 4, 16, 18), border_radius=2)
                pygame.draw.rect(screen, (92, 62, 48), (x + 250, bottom - 4, 16, 18), border_radius=2)
            elif self.kind == "frame1":
                pygame.draw.rect(screen, (170, 130, 90), (self.rect.x, self.y - 80, 110, 80), 6)
                pygame.draw.rect(screen, (220, 200, 180), (self.rect.x + 8, self.y - 72, 94, 64))
                pygame.draw.circle(screen, (180, 120, 100), (self.rect.x + 55, self.y - 40), 16)
            elif self.kind == "frame2":
                pygame.draw.rect(screen, (140, 100, 70), (self.rect.x, self.y - 82, 135, 82), 6)
                pygame.draw.rect(screen, (215, 190, 165), (self.rect.x + 8, self.y - 74, 119, 66))
                pygame.draw.rect(screen, (170, 120, 85), (self.rect.x + 15, self.y - 55, 28, 28))
                pygame.draw.rect(screen, (170, 120, 85), (self.rect.x + 54, self.y - 62, 28, 35))
                pygame.draw.rect(screen, (170, 120, 85), (self.rect.x + 93, self.y - 50, 26, 23))

        elif self.room_name == "Kitchen":
            if self.kind == "fridge":
                pygame.draw.rect(screen, (210, 210, 215), (self.rect.x, self.y - 190, 95, 190), border_radius=8)
                pygame.draw.line(screen, (170, 170, 175), (self.rect.x, self.y - 95), (self.rect.x + 95, self.y - 95), 2)
                pygame.draw.rect(screen, (160, 160, 165), (self.rect.x + 76, self.y - 145, 6, 28))
                pygame.draw.rect(screen, (160, 160, 165), (self.rect.x + 76, self.y - 70, 6, 28))
            else:
                pygame.draw.rect(screen, (155, 110, 70), (self.rect.x, self.y - 90, 220, 90))
                pygame.draw.rect(screen, (120, 120, 120), (self.rect.x - 5, self.y - 105, 230, 15))
                pygame.draw.rect(screen, (130, 90, 60), (self.rect.x + 25, self.y - 65, 40, 65))
                pygame.draw.rect(screen, (130, 90, 60), (self.rect.x + 155, self.y - 65, 40, 65))
        else:
            if self.kind == "toilet":
                pygame.draw.rect(screen, (245, 245, 245), (self.rect.x + 18, self.y - 55, 46, 55), border_radius=10)
                pygame.draw.rect(screen, (235, 235, 235), (self.rect.x + 12, self.y - 98, 55, 38), border_radius=6)
                pygame.draw.rect(screen, (220, 220, 220), (self.rect.x + 26, self.y - 115, 28, 18), border_radius=4)
            else:
                pygame.draw.rect(screen, (250, 250, 250), (self.rect.x, self.y - 72, 210, 72), border_radius=20)
                pygame.draw.rect(screen, (205, 205, 205), (self.rect.x + 175, self.y - 120, 8, 48))
                pygame.draw.rect(screen, (180, 180, 180), (self.rect.x + 162, self.y - 126, 28, 8))
                pygame.draw.rect(screen, (190, 190, 190), (self.rect.x + 20, self.y - 8, 18, 8))
                pygame.draw.rect(screen, (190, 190, 190), (self.rect.x + 170, self.y - 8, 18, 8))


class FloorObstacle:
    def __init__(self, room_name, kind, x):
        self.room_name = room_name
        self.kind = kind
        self.x = float(x)
        self.bottom = GROUND_DRAW_Y + 34

        if room_name == "Living Room":
            if kind == "cat":
                self.w, self.h = 110, 48
            elif kind == "books":
                self.w, self.h = 82, 34
            else:
                self.w, self.h = 96, 38
        elif room_name == "Kitchen":
            if kind == "pot":
                self.w, self.h = 72, 52
            elif kind == "pan":
                self.w, self.h = 110, 34
            else:
                self.w, self.h = 86, 56
        elif room_name == "Bedroom":
            if kind == "slippers":
                self.w, self.h = 96, 28
            elif kind == "books":
                self.w, self.h = 82, 34
            else:
                self.w, self.h = 96, 42
        else:
            if kind == "bucket":
                self.w, self.h = 70, 64
            elif kind == "soap_box":
                self.w, self.h = 80, 34
            else:
                self.w, self.h = 90, 32

        self.rect = pygame.Rect(int(self.x), int(self.bottom - self.h), self.w, self.h)
       

    def update(self):
        self.x -= GAME_SPEED
        self.rect.x = int(self.x)
        self.rect.bottom = int(self.bottom)

    def off_screen(self):
        return self.rect.right < 0

    def draw(self, screen):

        x = self.rect.x
        bottom = self.rect.bottom

        if self.room_name == "Living Room":
            if self.kind == "cat":
                pygame.draw.ellipse(screen, (110, 96, 88), (x + 14, bottom - 38, 62, 28))
                pygame.draw.circle(screen, (110, 96, 88), (x + 82, bottom - 26), 14)
                pygame.draw.polygon(screen, (110, 96, 88), [(x + 74, bottom - 40), (x + 79, bottom - 52), (x + 86, bottom - 40)])
                pygame.draw.polygon(screen, (110, 96, 88), [(x + 86, bottom - 40), (x + 92, bottom - 52), (x + 98, bottom - 40)])
                pygame.draw.arc(screen, (110, 96, 88), (x + 4, bottom - 34, 28, 30), 1.7, 5.2, 4)
            elif self.kind == "books":
                pygame.draw.rect(screen, (142, 92, 72), (x + 8, bottom - 16, 52, 12), border_radius=2)
                pygame.draw.rect(screen, (86, 116, 164), (x + 20, bottom - 28, 48, 12), border_radius=2)
                pygame.draw.rect(screen, (174, 154, 84), (x + 2, bottom - 34, 42, 8), border_radius=2)
            else:
                pygame.draw.ellipse(screen, (188, 150, 132), (x + 6, bottom - 30, 42, 24))
                pygame.draw.ellipse(screen, (162, 126, 170), (x + 40, bottom - 34, 50, 28))
        elif self.room_name == "Kitchen":
            if self.kind == "pot":
                pygame.draw.ellipse(screen, (126, 126, 132), (x + 10, bottom - 30, 48, 20))
                pygame.draw.rect(screen, (146, 146, 152), (x + 14, bottom - 30, 40, 18), border_radius=4)
                pygame.draw.rect(screen, (100, 100, 106), (x + 26, bottom - 42, 16, 8), border_radius=3)
                pygame.draw.rect(screen, (110, 110, 116), (x + 6, bottom - 26, 8, 6), border_radius=2)
                pygame.draw.rect(screen, (110, 110, 116), (x + 54, bottom - 26, 8, 6), border_radius=2)
            elif self.kind == "pan":
                pygame.draw.ellipse(screen, (98, 98, 104), (x + 2, bottom - 22, 56, 18))
                pygame.draw.rect(screen, (86, 66, 50), (x + 48, bottom - 16, 44, 6), border_radius=3)
            else:
                pygame.draw.ellipse(screen, (118, 118, 124), (x + 8, bottom - 20, 42, 16))
                pygame.draw.ellipse(screen, (98, 98, 104), (x + 24, bottom - 34, 44, 18))
                pygame.draw.rect(screen, (86, 66, 50), (x + 58, bottom - 28, 24, 5), border_radius=2)
        elif self.room_name == "Bedroom":
            if self.kind == "slippers":
                pygame.draw.ellipse(screen, (128, 94, 122), (x + 6, bottom - 18, 34, 14))
                pygame.draw.ellipse(screen, (128, 94, 122), (x + 44, bottom - 22, 38, 16))
            elif self.kind == "books":
                pygame.draw.rect(screen, (142, 92, 72), (x + 8, bottom - 16, 52, 12), border_radius=2)
                pygame.draw.rect(screen, (86, 116, 164), (x + 20, bottom - 28, 48, 12), border_radius=2)
                pygame.draw.rect(screen, (174, 154, 84), (x + 2, bottom - 34, 42, 8), border_radius=2)
            else:
                pygame.draw.ellipse(screen, (180, 158, 196), (x + 4, bottom - 30, 44, 24))
                pygame.draw.ellipse(screen, (164, 132, 154), (x + 34, bottom - 34, 44, 26))
                pygame.draw.ellipse(screen, (204, 188, 214), (x + 56, bottom - 26, 28, 18))
        else:
            if self.kind == "bucket":
                pygame.draw.rect(screen, (120, 160, 210), (x + 12, bottom - 40, 36, 32), border_radius=6)
                pygame.draw.arc(screen, (92, 122, 164), (x + 10, bottom - 50, 40, 24), 3.3, 6.1, 3)
            elif self.kind == "soap_box":
                pygame.draw.rect(screen, (196, 224, 242), (x + 10, bottom - 20, 52, 16), border_radius=4)
                pygame.draw.rect(screen, (170, 202, 226), (x + 18, bottom - 30, 36, 10), border_radius=4)
            else:
                pygame.draw.ellipse(screen, (194, 214, 228), (x + 10, bottom - 20, 58, 16))
                pygame.draw.circle(screen, (220, 232, 240), (x + 18, bottom - 12), 8)


class CeilingLampObstacle:
    def __init__(self, x):
        self.x = float(x)
        self.cord_height = 225
        self.shade_width = 126
        self.shade_height = 82
        self.rect = pygame.Rect(int(self.x), self.cord_height + 4, self.shade_width, self.shade_height - 6)

    def update(self):
        self.x -= GAME_SPEED
        self.rect.x = int(self.x)

    def off_screen(self):
        return self.rect.right < 0

    def draw(self, screen):
        center_x = int(self.x) + self.shade_width // 2
        pygame.draw.rect(screen, (90, 96, 110), (center_x - 4, 0, 8, self.cord_height))
        pygame.draw.rect(screen, (126, 134, 150), (center_x - 18, self.cord_height - 8, 36, 8), border_radius=3)
        pygame.draw.ellipse(screen, (176, 198, 232), (int(self.x), self.cord_height, self.shade_width, self.shade_height))
        pygame.draw.ellipse(screen, (126, 152, 194), (int(self.x) + 8, self.cord_height + self.shade_height - 12, self.shade_width - 16, 12))


class Detective:
    X_POS = 80
    DROP_VEL = JUMP_DROP_VEL

    def __init__(self, RUNNING, DUCKING, JUMPING):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.dino_duck = False
        self.dino_run = True
        self.dino_drop = False
        self.step_index = 0
        self.drop_vel = self.DROP_VEL
        self.image = self.run_img[0]
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.bottom = GROUND_DRAW_Y + PLAYER_GROUND_OFFSET

    def update(self, user_input):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_drop:
            self.drop()

        if self.step_index >= 10:
            self.step_index = 0

        if user_input[pygame.K_UP] and not self.dino_drop:
            self.dino_duck = False
            self.dino_run = False
            self.dino_drop = True
        elif user_input[pygame.K_DOWN] and not self.dino_drop:
            self.dino_duck = True
            self.dino_run = False
            self.dino_drop = False
        else:
            if not self.dino_drop:
                self.dino_duck = False
                self.dino_run = True
                self.dino_drop = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        bottom = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.bottom = bottom
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        bottom = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.bottom = bottom
        self.step_index += 1

    def drop(self):
        self.image = self.jump_img
        self.rect.y -= self.drop_vel * 4
        self.drop_vel -= 0.8
        if self.drop_vel < -self.DROP_VEL:
            self.dino_drop = False
            self.drop_vel = self.DROP_VEL
            self.rect.bottom = GROUND_DRAW_Y + PLAYER_GROUND_OFFSET

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Cloud:
    def __init__(self, cloud_img):
        self.image = cloud_img
        self.enabled = self.image is not None
        self.x = V_W + random.randint(300, 800)
        self.y = random.randint(120, 240)

    def update(self):
        if not self.enabled:
            return
        self.x -= 2
        if self.x < -self.image.get_width():
            self.x = V_W + random.randint(300, 800)
            self.y = random.randint(120, 240)

    def draw(self, screen):
        if self.enabled:
            screen.blit(self.image, (self.x, self.y))


class WhiteSquare:
    def __init__(self, image):
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


def score(screen, points):
    font = pygame.font.Font("freesansbold.ttf", 20)
    text = font.render(f"Points: {points}", True, (0, 0, 0))
    screen.blit(text, (950, 20))


def draw_clue_box(screen, clue_count):
    box_rect = pygame.Rect(8, 12, 210, 50)
    pygame.draw.rect(screen, (255, 255, 255), box_rect, border_radius=10)
    pygame.draw.rect(screen, (40, 40, 40), box_rect, 2, border_radius=10)

    font = pygame.font.Font("freesansbold.ttf", 16)
    text = font.render(f"Clues Collected = {clue_count}", True, (0, 0, 0))
    text_rect = text.get_rect(center=box_rect.center)
    screen.blit(text, text_rect)


def run_level1(VSCREEN, present):
    if not show_level1_instructions(VSCREEN, present):
        return False

    solution_suspect, solution_weapon, solution_room = generate_solution()
    collected_clues = []
    clue_set = set()
    used_clues = {"suspect": set(), "weapon": set(), "room": set()}

    RUN_SCALE = (175, 175)
    DUCK_SCALE = (175, 130)

    RUNNING = [
        load_img(os.path.join(DETECTIVE_DIR, "run1.png"), RUN_SCALE),
        load_img(os.path.join(DETECTIVE_DIR, "run2.png"), RUN_SCALE),
    ]
    JUMPING = load_img(os.path.join(DETECTIVE_DIR, "jump.png"), RUN_SCALE)
    DUCKING = [
        load_img(os.path.join(DETECTIVE_DIR, "duck1.png"), DUCK_SCALE),
        load_img(os.path.join(DETECTIVE_DIR, "duck2.png"), DUCK_SCALE),
    ]

    CLUE_IMG_PATH = os.path.join("Assets", "Level3", "clue.png")
    CLUE_IMG = pygame.image.load(CLUE_IMG_PATH).convert_alpha()
    CLUE_IMG = pygame.transform.scale(CLUE_IMG, (55, 55))
    CLOUD = safe_load(os.path.join(LEVEL1_BG_DIR, "Cloud.png"))

    shared_frame_assets = {
        "frame1": safe_load(os.path.join(LIVINGROOM_DIR, "frame1.png"), (190, 130), trim_alpha=True),
        "frame2": safe_load(os.path.join(LIVINGROOM_DIR, "frame2.png"), (320, 190), trim_alpha=True),
    }

    clock = pygame.time.Clock()
    player = Detective(RUNNING, DUCKING, JUMPING)
    cloud = Cloud(CLOUD)

    collectibles = []
    decor_items = []
    danger_obstacles = []

    squares_collected = 0
    points = 0

    level_start_time = pygame.time.get_ticks()
    countdown_start = pygame.time.get_ticks()
    last_room = None

    room_message = ""
    room_message_start = 0
    room_message_pending = False

    obstacle_spawn_timer = 0
    obstacle_spawn_gap = 95

    def get_current_room():
        elapsed = pygame.time.get_ticks() - level_start_time
        if elapsed < LIVING_ROOM_DURATION_MS:
            return "Living Room"
        elif elapsed < LIVING_ROOM_DURATION_MS + KITCHEN_DURATION_MS:
            return "Kitchen"
        elif elapsed < LIVING_ROOM_DURATION_MS + KITCHEN_DURATION_MS + BEDROOM_DURATION_MS:
            return "Bedroom"
        else:
            return "Bathroom"

    def spawn_room_set(room_name):
        decor_items.clear()
        danger_obstacles.clear()

        if room_name == "Living Room":
            decor_items.append(Decor("frame1", V_W + 80, room_name, shared_frame_assets))
            decor_items.append(Decor("frame2", V_W + 430, room_name, shared_frame_assets))
            decor_items.append(Decor("couch", V_W + 820, room_name, shared_frame_assets))
            decor_items.append(Decor("floor_lamp", V_W + 1140, room_name, shared_frame_assets))
        elif room_name == "Bedroom":
            decor_items.append(Decor("frame1", V_W + 80, room_name, shared_frame_assets))
            decor_items.append(Decor("frame2", V_W + 430, room_name, shared_frame_assets))
            decor_items.append(Decor("bed", V_W + 760, room_name, shared_frame_assets))
            decor_items.append(Decor("couch", V_W + 1120, room_name, shared_frame_assets))
            decor_items.append(Decor("floor_lamp", V_W + 1460, room_name, shared_frame_assets))
        elif room_name == "Kitchen":
            decor_items.append(Decor("fridge", V_W + 180, room_name))
            decor_items.append(Decor("counter", V_W + 560, room_name))
        else:
            decor_items.append(Decor("toilet", V_W + 180, room_name))
            decor_items.append(Decor("bathtub", V_W + 520, room_name))

    def spawn_danger_obstacle(room_name):
        x = V_W + random.randint(220, 380)

        if room_name == "Living Room":
            if random.random() < 0.45:
                danger_obstacles.append(CeilingLampObstacle(x))
            else:
                danger_obstacles.append(FloorObstacle(room_name, random.choice(["cat", "books", "cushions"]), x))
        elif room_name == "Kitchen":
            danger_obstacles.append(FloorObstacle(room_name, random.choice(["pot", "pan", "pans"]), x))
        elif room_name == "Bedroom":
            if random.random() < 0.45:
                danger_obstacles.append(CeilingLampObstacle(x))
            else:
                danger_obstacles.append(FloorObstacle(room_name, random.choice(["slippers", "books", "laundry"]), x))
        else:
            danger_obstacles.append(FloorObstacle(room_name, random.choice(["bucket", "soap_box", "towel_roll"]), x))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

        keys = pygame.key.get_pressed()
        current_room = get_current_room()
        elapsed_ms = pygame.time.get_ticks() - level_start_time
        countdown_active = (pygame.time.get_ticks() - countdown_start) < COUNTDOWN_MS

        if not countdown_active and room_message_pending:
            room_message_start = pygame.time.get_ticks()
            room_message_pending = False

        if current_room != last_room:
            spawn_room_set(current_room)
            last_room = current_room
            obstacle_spawn_timer = 0
            obstacle_spawn_gap = 95
            room_message = f"Entering {current_room} ..."
            room_message_pending = True

        if not countdown_active:
            obstacle_spawn_timer += 1
            can_spawn = (len(danger_obstacles) == 0 or danger_obstacles[-1].rect.x < V_W - 360)
            if obstacle_spawn_timer >= obstacle_spawn_gap and can_spawn:
                spawn_danger_obstacle(current_room)
                obstacle_spawn_timer = 0
                obstacle_spawn_gap = random.randint(78, 110)

        draw_room_background(VSCREEN, current_room)

        cloud.update()
        cloud.draw(VSCREEN)

        for decor in decor_items[:]:
            decor.update()
            if decor.off_screen():
                decor_items.remove(decor)

        for obs in danger_obstacles[:]:
            obs.update()
            if obs.off_screen():
                danger_obstacles.remove(obs)

        for decor in decor_items:
            decor.draw(VSCREEN)

        player_died = False

        for obs in danger_obstacles:
            obs.draw(VSCREEN)

            if not countdown_active and player.rect.colliderect(obs.rect):
                pygame.time.delay(250)
                player_died = True
                break

        if player_died:
            death_screen(VSCREEN, present)
            result = guessing_screen(
                VSCREEN,
                present,
                collected_clues,
                solution_suspect,
                solution_weapon,
                solution_room,
                LEVEL1_DATA["suspects"],
                LEVEL1_DATA["weapons"],
                LEVEL1_DATA["rooms"]
            )

            if result == "win":
                show_level_complete(VSCREEN, present)
                return "win"

            if result == "wrong":
                return "restart"

        if not countdown_active:
            if random.randint(0, 100) < 2 and len(collectibles) < 3:
                collectibles.append(WhiteSquare(CLUE_IMG))

        for sq in collectibles[:]:
            sq.update()
            sq.draw(VSCREEN)
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

                    if clue_text not in clue_set:
                        collected_clues.append(clue_text)
                        clue_set.add(clue_text)

                    squares_collected = 0

        player.update(keys)
        player.draw(VSCREEN)


        draw_clue_box(VSCREEN, len(collected_clues))

        if room_message and not room_message_pending:
            draw_room_transition(VSCREEN, room_message, room_message_start)

        score(VSCREEN, points)

        if countdown_active:
            draw_countdown(VSCREEN, countdown_start)

        if not countdown_active:
            points += 1

        if elapsed_ms >= LEVEL_DURATION_MS:
            result = guessing_screen(
                VSCREEN,
                present,
                collected_clues,
                solution_suspect,
                solution_weapon,
                solution_room,
                LEVEL1_DATA["suspects"],
                LEVEL1_DATA["weapons"],
                LEVEL1_DATA["rooms"]
            )

            if result == "win":
                return "next_level"
            else:
                return "restart"

        

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


def show_hub_screen(screen, present, level1_done, level2_unlocked):

    font = pygame.font.Font("freesansbold.ttf", 40)
    small = pygame.font.Font("freesansbold.ttf", 22)

    level2_button = pygame.Rect(250, 300, 300, 70)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if level2_unlocked and level2_button.collidepoint(get_virtual_mouse_pos()):
                    return "level2"

        # 🌫️ background
        screen.fill((10, 10, 20))

        title = font.render("Detective Case Hub", True, (230, 230, 230))
        screen.blit(title, (200, 100))

        # 🔓 Level 1 status
        status1 = small.render(
            "Case 1: Mansion Mystery - COMPLETED ✔",
            True,
            (120, 255, 120)
        )
        screen.blit(status1, (180, 200))

        # 🔒 Level 2 button
        if level2_unlocked:
            pygame.draw.rect(screen, (80, 120, 200), level2_button)
            text = small.render("Enter Case 2", True, (255, 255, 255))
        else:
            pygame.draw.rect(screen, (80, 80, 80), level2_button)
            text = small.render("LOCKED 🔒", True, (180, 180, 180))

        screen.blit(text, text.get_rect(center=level2_button.center))

        present()


if __name__ == "__main__":
    pygame.init()
    SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Detective Game")

    def present():
        pygame.display.flip()

    game_state = "level1"
    level1_complete = False
    level2_unlocked = False

    running = True

    while running:

        if game_state == "level1":
            result = run_level1(SCREEN, present)

            if result == False:
                running = False

            elif result == "win":
                level1_complete = True
                level2_unlocked = True
                game_state = "hub"

        elif game_state == "hub":
            next_state = show_hub_screen(
                SCREEN,
                present,
                level1_complete,
                level2_unlocked
            )

            if next_state == "quit":
                running = False

            elif next_state == "level2":
                game_state = "level2"

        elif game_state == "level2":
            # TEMP placeholder
            print("Level 2 starting...")
            running = False

    pygame.quit()