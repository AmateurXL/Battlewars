import math
import pygame
from game.constants import (W, H, GY, SKY_TOP, SKY_BOT, GRASS, GRASS_DARK,
                             GRASS_MID, TREE_TRUNK, TREE_LEAF, SKIN, STEEL,
                             WHEEL, BARREL, GOLD, HP_GREEN, HP_ORANGE, HP_RED,
                             WHITE, UI_BG, DIVIDER)

FONT_SM = None
FONT_MD = None

def init_fonts():
    global FONT_SM, FONT_MD
    FONT_SM = pygame.font.SysFont("monospace", 11)
    FONT_MD = pygame.font.SysFont("monospace", 18)


# ── Terrain ──────────────────────────────────────────────────
def draw_terrain(surf: pygame.Surface) -> None:
    # Sky gradient (manual scanline)
    for y in range(GY):
        t = y / GY
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (W, y))

    # Ground layers
    pygame.draw.rect(surf, GRASS,      (0, GY,     W, H - GY))
    pygame.draw.rect(surf, GRASS_DARK, (0, GY,     W, 5))
    pygame.draw.rect(surf, GRASS_MID,  (0, GY + 14, W, 3))

    # Stars
    for sx, sy in [(50,30),(120,15),(300,40),(450,20),(600,35),(680,12),(150,55),(520,50)]:
        surf.set_at((sx, sy), (255, 255, 255))

    # Trees
    for tx in [70, 190, 530, 650]:
        pygame.draw.rect(surf, TREE_TRUNK, (tx-3, GY-22, 6, 22))
        pygame.draw.rect(surf, TREE_LEAF,  (tx-11, GY-38, 22, 18))
        pygame.draw.rect(surf, TREE_LEAF,  (tx-8,  GY-52, 16, 16))
        pygame.draw.rect(surf, TREE_LEAF,  (tx-5,  GY-62, 10, 12))

    # Dividing dashed line
    dash_surf = pygame.Surface((2, H - GY), pygame.SRCALPHA)
    dash_surf.fill((0, 0, 0, 0))
    for dy in range(0, H - GY, 12):
        pygame.draw.rect(dash_surf, (255, 255, 0, 30), (0, dy, 2, 6))
    surf.blit(dash_surf, (W // 2, GY))


# ── HP bar ───────────────────────────────────────────────────
def draw_hp_bar(surf, x, y, hp, max_hp):
    bw, bh = 16, 2
    pygame.draw.rect(surf, (50, 50, 50), (x - bw//2, y, bw, bh))
    ratio = hp / max_hp
    col   = HP_GREEN if ratio > 0.5 else HP_ORANGE if ratio > 0.25 else HP_RED
    pygame.draw.rect(surf, col, (x - bw//2, y, int(bw * ratio), bh))


# ── Unit drawers ─────────────────────────────────────────────
def _draw_cavalry(surf, px, py, c1, c2, team):
    pygame.draw.rect(surf, c1, (px-10, py-2,  20, 8))   # horse body
    pygame.draw.rect(surf, c1, (px-8,  py+6,   5, 6))   # legs
    pygame.draw.rect(surf, c1, (px+3,  py+6,   5, 6))
    pygame.draw.rect(surf, c1, (px+8,  py-4,   4, 4))   # head
    pygame.draw.rect(surf, c2, (px-3,  py-10,  7, 8))   # rider body
    pygame.draw.rect(surf, SKIN, (px-1, py-16, 5, 6))   # rider head
    sx = px + (5 if team == "blue" else -13)
    pygame.draw.rect(surf, (200, 200, 200), (sx, py-14, 8, 2))  # sword


def _draw_cannon(surf, px, py, c1, c2, team):
    pygame.draw.circle(surf, WHEEL, (px-8, py+8), 6)
    pygame.draw.circle(surf, WHEEL, (px+8, py+8), 6)
    pygame.draw.rect(surf, c1,    (px-9, py-2, 18, 10))
    cd = 1 if team == "blue" else -1
    pygame.draw.rect(surf, BARREL, (px + cd*6, py-1, cd*14, 5))
    pygame.draw.rect(surf, c2,    (px-4, py-10, 8,  8))
    pygame.draw.rect(surf, SKIN,  (px-2, py-16, 5,  5))


def _draw_infantry(surf, px, py, c1, c2, team, unit_type, anim_frame, state):
    bob = int(math.sin(anim_frame * 0.22) * (1.2 if state == "walk" else 0))
    pygame.draw.rect(surf, c1, (px-3, py+6+bob, 3, 5))
    pygame.draw.rect(surf, c1, (px+1, py+6-bob, 3, 5))
    pygame.draw.rect(surf, c2, (px-4, py+1,     8, 6))
    pygame.draw.rect(surf, SKIN, (px-2, py-4,   6, 5))

    if unit_type == "archer":
        pygame.draw.rect(surf, c1, (px-3, py-7, 7, 4))
        ad = 1 if team == "blue" else -1
        pygame.draw.arc(surf, (141, 110, 99),
                        pygame.Rect(px + ad*1, py-5, 10, 10), 0.5, 2.6, 2)
    else:
        hat = c1
        pygame.draw.rect(surf, hat,   (px-3, py-7, 7, 3))
        gd = 4 if team == "blue" else -10
        pygame.draw.rect(surf, STEEL, (px+gd, py,  6, 2))


def draw_unit(surf, unit) -> None:
    px, py = int(unit.x), int(unit.y)
    c1, c2 = unit.color1, unit.color2

    if unit.dead:
        pygame.draw.rect(surf, c1,   (px-7, py+2, 13, 4))
        pygame.draw.rect(surf, SKIN, (px+5, py+1,  4, 4))
        return

    if unit.flash > 0 and unit.flash % 2 == 0:
        flash_surf = pygame.Surface((20, 30), pygame.SRCALPHA)
        flash_surf.fill((255, 255, 255, 80))
        surf.blit(flash_surf, (px - 10, py - 20))

    if unit.unit_type == "cavalry":
        _draw_cavalry(surf, px, py, c1, c2, unit.team)
        draw_hp_bar(surf, px, py - 20, unit.hp, unit.max_hp)
    elif unit.unit_type == "cannon":
        _draw_cannon(surf, px, py, c1, c2, unit.team)
        draw_hp_bar(surf, px, py - 22, unit.hp, unit.max_hp)
    else:
        _draw_infantry(surf, px, py, c1, c2, unit.team, unit.unit_type, unit.anim_frame, unit.state)
        draw_hp_bar(surf, px, py - 12, unit.hp, unit.max_hp)


# ── Bullet ───────────────────────────────────────────────────
def draw_bullet(surf, bullet) -> None:
    bx, by = int(bullet.x), int(bullet.y)
    if bullet.aoe:
        pygame.draw.circle(surf, bullet.color, (bx, by), 4)
    elif bullet.is_arrow:
        end = (int(bullet.x - bullet.vx * 2), int(bullet.y - bullet.vy * 2))
        col = (206, 147, 216) if bullet.team == "blue" else (255, 171, 145)
        pygame.draw.line(surf, col, (bx, by), end, 2)
    else:
        pygame.draw.rect(surf, bullet.color, (bx - 3, by - 1, 5, 2))


# ── Particles ────────────────────────────────────────────────
def draw_particle(surf, p) -> None:
    alpha = int(255 * p.life / 35)
    if alpha <= 0:
        return
    s = pygame.Surface((3, 3), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))          # clear to transparent first
    pygame.draw.rect(s, (*p.color, alpha), (0, 0, 3, 3))
    surf.blit(s, (int(p.x) - 1, int(p.y) - 1))


# ── UI overlays ──────────────────────────────────────────────
def draw_wave_timer(surf, progress: float, wave_num: int) -> None:
    if wave_num == 0:
        return
    bw, bh = 120, 6
    bx, by = W // 2 - bw // 2, 8
    pygame.draw.rect(surf, (34, 34, 34),  (bx, by, bw, bh))
    pygame.draw.rect(surf, GOLD, (bx, by, int(bw * progress), bh))
    lbl = FONT_SM.render("next wave", True, (200, 200, 200))
    surf.blit(lbl, (bx + bw // 2 - lbl.get_width() // 2, by - 13))


def draw_hud(surf, units, wave_num, label, msg) -> None:
    blue = sum(1 for u in units if u.team == "blue" and not u.dead)
    red  = sum(1 for u in units if u.team == "red"  and not u.dead)

    pygame.draw.rect(surf, UI_BG, (0, 0, W, 22))

    b_txt = FONT_SM.render(f"BLUE  {blue}", True, (79, 195, 247))
    w_txt = FONT_SM.render(f"WAVE {wave_num}", True, GOLD)
    r_txt = FONT_SM.render(f"{red}  RED", True, (239, 83, 80))

    surf.blit(b_txt, (10, 5))
    surf.blit(w_txt, (W // 2 - w_txt.get_width() // 2, 5))
    surf.blit(r_txt, (W - r_txt.get_width() - 10, 5))

    if label:
        lbl = FONT_MD.render(label, True, GOLD)
        surf.blit(lbl, (W // 2 - lbl.get_width() // 2, H // 2 - 10))

    if msg:
        m = FONT_MD.render(msg, True, GOLD)
        surf.blit(m, (W // 2 - m.get_width() // 2, H // 2 + 20))


def draw_controls_hint(surf) -> None:
    hint = FONT_SM.render("SPACE pause   N new battle   W force wave", True, (120, 120, 120))
    surf.blit(hint, (W // 2 - hint.get_width() // 2, H - 138))