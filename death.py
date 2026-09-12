# death.py
import pygame

V_W, V_H = 1100, 600

def death_screen(screen, present):
    font_big = pygame.font.Font("freesansbold.ttf", 64)
    font = pygame.font.Font("freesansbold.ttf", 28)

    screen.fill((5, 5, 10))

    panel = pygame.Rect(V_W//2 - 260, 160, 520, 260)
    pygame.draw.rect(screen, (35, 10, 10), panel, border_radius=15)
    pygame.draw.rect(screen, (140, 40, 40), panel, 3, border_radius=15)

    title = font_big.render("YOU DIED", True, (255, 80, 80))
    screen.blit(title, title.get_rect(center=(V_W // 2, 240)))

    sub = font.render("The mystery remains unsolved...", True, (220, 220, 220))
    screen.blit(sub, sub.get_rect(center=(V_W // 2, 310)))

    hint = font.render("Returning to case board...", True, (180, 180, 180))
    screen.blit(hint, hint.get_rect(center=(V_W // 2, 360)))

    present()

    pygame.time.wait(2000)  # cinematic pause