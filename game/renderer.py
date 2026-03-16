import math
import pygame
from game.constants import (W, H, GY, SKY_TOP, SKY_BOT, GRASS, GRASS_DARK,
                             GRASS_MID, TREE_TRUNK, TREE_LEAF, SKIN, STEEL,
                             WHEEL, BARREL, GOLD, HP_GREEN, HP_ORANGE, HP_RED,
                             WHITE, UI_BG, DIVIDER)

FONT_SM = None
FONT_MD = None
FONT_LG = None

def init_fonts():
    global FONT_SM, FONT_MD, FONT_LG
    FONT_SM = pygame.font.SysFont("monospace", 14)
    FONT_MD = pygame.font.SysFont("monospace", 24)
    FONT_LG = pygame.font.SysFont("monospace", 36)


# ── Terrain ──────────────────────────────────────────────────
def draw_terrain(surf: pygame.Surface) -> None:
    for y in range(GY):
        t = y / GY
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (W, y))

    pygame.draw.rect(surf, GRASS,      (0, GY,      W, H - GY))
    pygame.draw.rect(surf, GRASS_DARK, (0, GY,      W, 8))
    pygame.draw.rect(surf, GRASS_MID,  (0, GY + 20, W, 4))

    for sx, sy in [(80,40),(200,20),(480,55),(720,30),(960,45),(1100,18),(240,70),(820,65)]:
        surf.set_at((sx, sy), (255, 255, 255))
        surf.set_at((sx+1, sy), (200, 200, 255))

    for tx in [110, 300, 820, 1050]:
        pygame.draw.rect(surf, TREE_TRUNK, (tx-5,  GY-36,  10, 36))
        pygame.draw.rect(surf, TREE_LEAF,  (tx-18, GY-62,  36, 28))
        pygame.draw.rect(surf, TREE_LEAF,  (tx-13, GY-84,  26, 24))
        pygame.draw.rect(surf, TREE_LEAF,  (tx-8,  GY-100, 16, 18))
        pygame.draw.rect(surf, (36,100,36),(tx-16, GY-58,  32, 6))

    dash_surf = pygame.Surface((3, H - GY), pygame.SRCALPHA)
    dash_surf.fill((0, 0, 0, 0))
    for dy in range(0, H - GY, 18):
        pygame.draw.rect(dash_surf, (255, 255, 0, 25), (0, dy, 3, 9))
    surf.blit(dash_surf, (W // 2, GY))


# ── HP bar ───────────────────────────────────────────────────
def draw_hp_bar(surf, x, y, hp, max_hp):
    bw, bh = 26, 4
    pygame.draw.rect(surf, (30, 30, 30),   (x - bw//2 - 1, y - 1, bw + 2, bh + 2))
    pygame.draw.rect(surf, (60, 60, 60),   (x - bw//2, y, bw, bh))
    ratio = hp / max_hp
    col   = HP_GREEN if ratio > 0.5 else HP_ORANGE if ratio > 0.25 else HP_RED
    pygame.draw.rect(surf, col, (x - bw//2, y, int(bw * ratio), bh))


# ── Shadow ───────────────────────────────────────────────────
def draw_shadow(surf, x, y, w=20):
    s = pygame.Surface((w, 4), pygame.SRCALPHA)
    s.fill((0, 0, 0, 50))
    surf.blit(s, (x - w//2, y))


# ── Soldier — helmet, belt, boots ───────────────────────────
def _draw_soldier(surf, px, py, c1, c2, team, anim_frame, state):
    bob  = int(math.sin(anim_frame * 0.18) * (2.5 if state == "walk" else 0))
    bob2 = int(math.sin(anim_frame * 0.18 + math.pi) * (2.5 if state == "walk" else 0))
    dark1 = tuple(max(0, v - 40) for v in c1)

    draw_shadow(surf, px, py + 14, 22)

    # Boots
    pygame.draw.rect(surf, (40, 30, 20), (px-5, py+10+bob,  5, 6))
    pygame.draw.rect(surf, (40, 30, 20), (px+1, py+10+bob2, 5, 6))

    # Legs
    pygame.draw.rect(surf, dark1, (px-5, py+6+bob,  5, 6))
    pygame.draw.rect(surf, dark1, (px+1, py+6+bob2, 5, 6))

    # Belt
    pygame.draw.rect(surf, (60, 40, 20), (px-6, py+4, 12, 3))

    # Body
    pygame.draw.rect(surf, c2,   (px-6, py-4, 12, 9))
    # Chest detail
    pygame.draw.rect(surf, c1,   (px-4, py-3, 3, 4))
    pygame.draw.rect(surf, c1,   (px+1, py-3, 3, 4))

    # Arms
    pygame.draw.rect(surf, c1, (px-8, py-3, 3, 7))
    pygame.draw.rect(surf, c1, (px+5, py-3, 3, 7))

    # Neck + head
    pygame.draw.rect(surf, SKIN, (px-2, py-9,  5, 5))
    pygame.draw.rect(surf, SKIN, (px-4, py-14, 9, 7))

    # Helmet
    pygame.draw.rect(surf, c1,   (px-5, py-17, 10, 5))
    pygame.draw.rect(surf, c1,   (px-4, py-19, 8,  3))
    pygame.draw.rect(surf, dark1,(px-5, py-15, 10, 2))

    # Gun
    gd = 1 if team == "blue" else -1
    pygame.draw.rect(surf, STEEL, (px + gd*5, py-2, gd*12, 3))
    pygame.draw.rect(surf, (30,30,30), (px + gd*14, py-3, gd*3, 5))


# ── Archer — hood, quiver ────────────────────────────────────
def _draw_archer(surf, px, py, c1, c2, team, anim_frame, state):
    bob  = int(math.sin(anim_frame * 0.18) * (2 if state == "walk" else 0))
    bob2 = int(math.sin(anim_frame * 0.18 + math.pi) * (2 if state == "walk" else 0))
    dark1 = tuple(max(0, v - 40) for v in c1)

    draw_shadow(surf, px, py + 14, 18)

    # Boots
    pygame.draw.rect(surf, (50, 35, 20), (px-4, py+10+bob,  4, 5))
    pygame.draw.rect(surf, (50, 35, 20), (px+1, py+10+bob2, 4, 5))

    # Legs (lighter, ranger style)
    pygame.draw.rect(surf, dark1, (px-4, py+6+bob,  4, 5))
    pygame.draw.rect(surf, dark1, (px+1, py+6+bob2, 4, 5))

    # Body / tunic
    pygame.draw.rect(surf, c2,   (px-5, py-4, 10, 9))
    pygame.draw.rect(surf, c1,   (px-3, py-2,  6, 5))

    # Arms
    pygame.draw.rect(surf, c1, (px-7, py-3, 3, 6))
    pygame.draw.rect(surf, c1, (px+4, py-3, 3, 6))

    # Quiver (back, opposite side to bow)
    qd = -1 if team == "blue" else 1
    pygame.draw.rect(surf, (80, 50, 20), (px + qd*5, py-8, 4, 10))
    for i in range(3):
        pygame.draw.rect(surf, GOLD, (px + qd*6, py-10+i*3, 2, 2))

    # Head
    pygame.draw.rect(surf, SKIN, (px-3, py-9,  7, 5))
    pygame.draw.rect(surf, SKIN, (px-4, py-14, 8, 7))

    # Hood
    pygame.draw.rect(surf, c1,   (px-5, py-17, 10, 6))
    pygame.draw.rect(surf, dark1,(px-4, py-16,  8, 2))
    pygame.draw.rect(surf, c1,   (px-6, py-13,  4, 4))

    # Bow
    ad = 1 if team == "blue" else -1
    pygame.draw.arc(surf, (141, 110, 99),
                    pygame.Rect(px + ad*4, py-10, 12, 18), 0.4, 2.7, 3)
    pygame.draw.line(surf, (180,140,80),
                     (px + ad*10, py-10), (px + ad*10, py+8), 1)


# ── Cavalry ──────────────────────────────────────────────────
def _draw_cavalry(surf, px, py, c1, c2, team, anim_frame, state):
    bob = int(math.sin(anim_frame * 0.22) * (3 if state == "walk" else 0))
    dark1 = tuple(max(0, v - 40) for v in c1)

    draw_shadow(surf, px, py + 14, 34)

    # Horse legs (4 legs animated in pairs)
    leg_bob  = int(math.sin(anim_frame * 0.22) * (4 if state == "walk" else 0))
    leg_bob2 = int(math.sin(anim_frame * 0.22 + math.pi) * (4 if state == "walk" else 0))
    pygame.draw.rect(surf, dark1, (px-14, py+6+leg_bob,  5, 10))
    pygame.draw.rect(surf, dark1, (px-7,  py+6+leg_bob2, 5, 10))
    pygame.draw.rect(surf, dark1, (px+2,  py+6+leg_bob,  5, 10))
    pygame.draw.rect(surf, dark1, (px+9,  py+6+leg_bob2, 5, 10))
    # Hooves
    pygame.draw.rect(surf, (30,20,10), (px-14, py+14+leg_bob,  5, 3))
    pygame.draw.rect(surf, (30,20,10), (px-7,  py+14+leg_bob2, 5, 3))
    pygame.draw.rect(surf, (30,20,10), (px+2,  py+14+leg_bob,  5, 3))
    pygame.draw.rect(surf, (30,20,10), (px+9,  py+14+leg_bob2, 5, 3))

    # Horse body
    pygame.draw.rect(surf, c1,   (px-16, py-4+bob, 32, 12))
    pygame.draw.rect(surf, dark1,(px-16, py-2+bob,  32,  3))
    # Horse neck + head
    pygame.draw.rect(surf, c1,   (px+10, py-12+bob,  8, 10))
    pygame.draw.rect(surf, c1,   (px+12, py-18+bob,  9,  8))
    # Mane
    pygame.draw.rect(surf, dark1,(px+10, py-14+bob,  3, 10))
    # Nose
    pygame.draw.rect(surf, dark1,(px+18, py-16+bob,  3,  4))
    # Tail
    pygame.draw.rect(surf, dark1,(px-18, py-2+bob,   3, 12))

    # Saddle
    pygame.draw.rect(surf, (80,50,20),(px-4, py-7+bob, 10, 4))

    # Rider body
    pygame.draw.rect(surf, c2,   (px-5, py-18+bob, 10, 12))
    pygame.draw.rect(surf, c1,   (px-7, py-16+bob,  3,  8))
    pygame.draw.rect(surf, c1,   (px+4, py-16+bob,  3,  8))

    # Rider head + helmet
    pygame.draw.rect(surf, SKIN, (px-3, py-23+bob,  7,  6))
    pygame.draw.rect(surf, c1,   (px-4, py-27+bob,  9,  6))
    pygame.draw.rect(surf, dark1,(px-4, py-25+bob,  9,  2))

    # Lance / sword
    sd = 1 if team == "blue" else -1
    pygame.draw.rect(surf, (200,200,200), (px+sd*5, py-26+bob, sd*20, 2))
    pygame.draw.rect(surf, GOLD,          (px+sd*22, py-28+bob, sd*3,  6))


# ── Cannon + crew ────────────────────────────────────────────
def _draw_cannon(surf, px, py, c1, c2, team, anim_frame):
    dark1 = tuple(max(0, v - 40) for v in c1)

    draw_shadow(surf, px, py + 16, 40)

    # Wheels (spoked)
    for wx in [px-14, px+14]:
        pygame.draw.circle(surf, WHEEL,      (wx, py+12), 10)
        pygame.draw.circle(surf, dark1,      (wx, py+12),  7)
        pygame.draw.circle(surf, WHEEL,      (wx, py+12),  4)
        pygame.draw.line(surf, WHEEL, (wx-9, py+12), (wx+9, py+12), 2)
        pygame.draw.line(surf, WHEEL, (wx, py+3),    (wx, py+21),   2)
        pygame.draw.line(surf, WHEEL, (wx-6, py+6),  (wx+6, py+18), 2)
        pygame.draw.line(surf, WHEEL, (wx+6, py+6),  (wx-6, py+18), 2)

    # Carriage body
    pygame.draw.rect(surf, c1,   (px-14, py-4, 28, 16))
    pygame.draw.rect(surf, dark1,(px-14, py-1, 28,  3))

    # Barrel
    cd = 1 if team == "blue" else -1
    pygame.draw.rect(surf, BARREL,      (px+cd*2,  py-5, cd*22, 8))
    pygame.draw.rect(surf, dark1,       (px+cd*2,  py-4, cd*20, 2))
    pygame.draw.rect(surf, (80,80,80),  (px+cd*22, py-6, cd*4, 10))
    # Barrel bands
    for bx in [cd*6, cd*12, cd*18]:
        pygame.draw.rect(surf, (100,100,100), (px+bx, py-5, cd*2, 8))

    # Crew member
    crew_x = px - cd*10
    # Crew boots
    pygame.draw.rect(surf, (40,30,20), (crew_x-3, py+2, 3, 5))
    pygame.draw.rect(surf, (40,30,20), (crew_x+1, py+2, 3, 5))
    # Crew body
    pygame.draw.rect(surf, c2,  (crew_x-4, py-10, 8, 12))
    pygame.draw.rect(surf, c1,  (crew_x-6, py-8,  3,  7))
    pygame.draw.rect(surf, c1,  (crew_x+3, py-8,  3,  7))
    # Crew head
    pygame.draw.rect(surf, SKIN,(crew_x-3, py-15, 6, 6))
    # Crew hat
    pygame.draw.rect(surf, c1,  (crew_x-4, py-20, 8, 6))
    pygame.draw.rect(surf, dark1,(crew_x-3,py-18, 6, 2))

    draw_hp_bar(surf, px, py - 34, 0, 1)  # placeholder spacing


# ── Dead unit ────────────────────────────────────────────────
def _draw_dead(surf, px, py, c1):
    pygame.draw.rect(surf, c1,   (px-10, py+4, 20, 6))
    pygame.draw.rect(surf, SKIN, (px+8,  py+3,  6, 6))
    pygame.draw.rect(surf, c1,   (px-12, py+6,  6, 3))


# ── Dispatch ─────────────────────────────────────────────────
def draw_unit(surf, unit) -> None:
    px, py = int(unit.x), int(unit.y)
    c1, c2 = unit.color1, unit.color2

    if unit.dead:
        _draw_dead(surf, px, py, c1)
        return

    if unit.flash > 0 and unit.flash % 2 == 0:
        flash_surf = pygame.Surface((32, 44), pygame.SRCALPHA)
        flash_surf.fill((255, 255, 255, 70))
        surf.blit(flash_surf, (px - 16, py - 30))

    f = unit.anim_frame
    s = unit.state

    if unit.unit_type == "cavalry":
        _draw_cavalry(surf, px, py, c1, c2, unit.team, f, s)
        draw_hp_bar(surf, px, py - 34, unit.hp, unit.max_hp)
    elif unit.unit_type == "cannon":
        _draw_cannon(surf, px, py, c1, c2, unit.team, f)
        draw_hp_bar(surf, px, py - 34, unit.hp, unit.max_hp)
    elif unit.unit_type == "archer":
        _draw_archer(surf, px, py, c1, c2, unit.team, f, s)
        draw_hp_bar(surf, px, py - 22, unit.hp, unit.max_hp)
    else:
        _draw_soldier(surf, px, py, c1, c2, unit.team, f, s)
        draw_hp_bar(surf, px, py - 24, unit.hp, unit.max_hp)


# ── Bullet ───────────────────────────────────────────────────
def draw_bullet(surf, bullet) -> None:
    bx, by = int(bullet.x), int(bullet.y)
    if bullet.aoe:
        pygame.draw.circle(surf, bullet.color, (bx, by), 6)
        pygame.draw.circle(surf, WHITE,        (bx, by), 3)
    elif bullet.is_arrow:
        end = (int(bullet.x - bullet.vx*3), int(bullet.y - bullet.vy*3))
        col = (206, 147, 216) if bullet.team == "blue" else (255, 171, 145)
        pygame.draw.line(surf, col,           (bx, by), end, 2)
        pygame.draw.line(surf, (180,140,80),  (bx, by), (bx + int(bullet.vx), by + int(bullet.vy)), 2)
    else:
        pygame.draw.rect(surf, bullet.color, (bx-4, by-2, 7, 3))
        pygame.draw.rect(surf, WHITE,        (bx-2, by-1, 3, 1))


# ── Particles ────────────────────────────────────────────────
def draw_particle(surf, p) -> None:
    alpha = int(255 * p.life / 35)
    if alpha <= 0:
        return
    s = pygame.Surface((4, 4), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    pygame.draw.rect(s, (*p.color, alpha), (0, 0, 4, 4))
    surf.blit(s, (int(p.x) - 2, int(p.y) - 2))


# ── HUD ──────────────────────────────────────────────────────
def draw_wave_timer(surf, progress: float, wave_num: int) -> None:
    if wave_num == 0:
        return
    bw, bh = 180, 8
    bx, by = W // 2 - bw // 2, 10
    pygame.draw.rect(surf, (20, 20, 20),   (bx-1, by-1, bw+2, bh+2))
    pygame.draw.rect(surf, (50, 50, 50),   (bx,   by,   bw,   bh))
    pygame.draw.rect(surf, GOLD, (bx, by, int(bw * progress), bh))
    lbl = FONT_SM.render("next wave", True, (180, 180, 180))
    surf.blit(lbl, (bx + bw//2 - lbl.get_width()//2, by - 16))


def draw_hud(surf, units, wave_num, label, msg) -> None:
    blue = sum(1 for u in units if u.team == "blue" and not u.dead)
    red  = sum(1 for u in units if u.team == "red"  and not u.dead)

    pygame.draw.rect(surf, UI_BG, (0, 0, W, 30))
    pygame.draw.line(surf, (60,60,80), (0, 30), (W, 30), 1)

    b_txt = FONT_SM.render(f"BLUE  {blue}", True, (79, 195, 247))
    w_txt = FONT_SM.render(f"WAVE {wave_num}", True, GOLD)
    r_txt = FONT_SM.render(f"{red}  RED",  True, (239, 83,  80))

    surf.blit(b_txt, (14, 8))
    surf.blit(w_txt, (W//2 - w_txt.get_width()//2, 8))
    surf.blit(r_txt, (W - r_txt.get_width() - 14, 8))

    if label:
        lbl = FONT_MD.render(label, True, GOLD)
        surf.blit(lbl, (W//2 - lbl.get_width()//2, H//2 - 14))

    if msg:
        m = FONT_LG.render(msg, True, GOLD)
        surf.blit(m, (W//2 - m.get_width()//2, H//2 + 20))


def draw_controls_hint(surf) -> None:
    hint = FONT_SM.render("SPACE pause   N new battle   W force wave", True, (100, 100, 100))
    surf.blit(hint, (W//2 - hint.get_width()//2, H - 155))