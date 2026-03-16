import math
import pygame
from game.constants import (W, H, GY, PANEL_W, SKY_TOP, SKY_BOT, GRASS, GRASS_DARK,
                             GRASS_MID, TREE_TRUNK, TREE_LEAF, SKIN, STEEL,
                             WHEEL, BARREL, GOLD, HP_GREEN, HP_ORANGE, HP_RED,
                             WHITE, UI_BG, DIVIDER)

BX = PANEL_W
BW = W - PANEL_W

FONT_SM: pygame.font.Font | None = None
FONT_MD: pygame.font.Font | None = None
FONT_LG: pygame.font.Font | None = None

def init_fonts() -> None:
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
        pygame.draw.line(surf, (r, g, b), (BX, y), (W, y))

    pygame.draw.rect(surf, GRASS,      (BX, GY,      BW, H - GY))
    pygame.draw.rect(surf, GRASS_DARK, (BX, GY,      BW, 8))
    pygame.draw.rect(surf, GRASS_MID,  (BX, GY + 20, BW, 4))

    for sx, sy in [(BX+80,40),(BX+200,20),(BX+480,55),(BX+520,30),
                   (BX+700,45),(BX+900,18),(BX+240,70),(BX+820,65)]:
        if sx < W:
            surf.set_at((sx, sy), (255, 255, 255))

    for tx in [BX+110, BX+300, BX+600, BX+850]:
        if tx < W:
            pygame.draw.rect(surf, TREE_TRUNK, (tx-5,  GY-36,  10, 36))
            pygame.draw.rect(surf, TREE_LEAF,  (tx-18, GY-62,  36, 28))
            pygame.draw.rect(surf, TREE_LEAF,  (tx-13, GY-84,  26, 24))
            pygame.draw.rect(surf, TREE_LEAF,  (tx-8,  GY-100, 16, 18))
            pygame.draw.rect(surf, (36,100,36),(tx-16, GY-58,  32,  6))

    dash_surf = pygame.Surface((3, H - GY), pygame.SRCALPHA)
    dash_surf.fill((0, 0, 0, 0))
    for dy in range(0, H - GY, 18):
        pygame.draw.rect(dash_surf, (255, 255, 0, 25), (0, dy, 3, 9))
    surf.blit(dash_surf, (BX + BW // 2, GY))


# ── HP bar ───────────────────────────────────────────────────
def draw_hp_bar(surf, x, y, hp, max_hp):
    bw, bh = 26, 4
    pygame.draw.rect(surf, (30, 30, 30),   (x - bw//2 - 1, y - 1, bw + 2, bh + 2))
    pygame.draw.rect(surf, (60, 60, 60),   (x - bw//2, y, bw, bh))
    ratio = hp / max_hp if max_hp else 0
    col   = HP_GREEN if ratio > 0.5 else HP_ORANGE if ratio > 0.25 else HP_RED
    pygame.draw.rect(surf, col, (x - bw//2, y, int(bw * ratio), bh))


# ── Shadow ───────────────────────────────────────────────────
def draw_shadow(surf, x, y, w=20):
    s = pygame.Surface((w, 4), pygame.SRCALPHA)
    s.fill((0, 0, 0, 50))
    surf.blit(s, (x - w//2, y))


# ── Soldier ──────────────────────────────────────────────────
def _draw_soldier(surf, px, py, c1, c2, team, anim_frame, state):
    bob  = int(math.sin(anim_frame * 0.18) * (2.5 if state == "walk" else 0))
    bob2 = int(math.sin(anim_frame * 0.18 + math.pi) * (2.5 if state == "walk" else 0))
    dark1 = tuple(max(0, v - 40) for v in c1)

    draw_shadow(surf, px, py + 14, 22)
    pygame.draw.rect(surf, (40, 30, 20), (px-5, py+10+bob,  5, 6))
    pygame.draw.rect(surf, (40, 30, 20), (px+1, py+10+bob2, 5, 6))
    pygame.draw.rect(surf, dark1,        (px-5, py+6+bob,   5, 6))
    pygame.draw.rect(surf, dark1,        (px+1, py+6+bob2,  5, 6))
    pygame.draw.rect(surf, (60, 40, 20), (px-6, py+4,  12, 3))
    pygame.draw.rect(surf, c2,           (px-6, py-4,  12, 9))
    pygame.draw.rect(surf, c1,           (px-4, py-3,   3, 4))
    pygame.draw.rect(surf, c1,           (px+1, py-3,   3, 4))
    pygame.draw.rect(surf, c1,           (px-8, py-3,   3, 7))
    pygame.draw.rect(surf, c1,           (px+5, py-3,   3, 7))
    pygame.draw.rect(surf, SKIN,         (px-2, py-9,   5, 5))
    pygame.draw.rect(surf, SKIN,         (px-4, py-14,  9, 7))
    pygame.draw.rect(surf, c1,           (px-5, py-17, 10, 5))
    pygame.draw.rect(surf, c1,           (px-4, py-19,  8, 3))
    pygame.draw.rect(surf, dark1,        (px-5, py-15, 10, 2))
    gd = 1 if team == "blue" else -1
    pygame.draw.rect(surf, STEEL,        (px + gd*5,  py-2, gd*12, 3))
    pygame.draw.rect(surf, (30,30,30),   (px + gd*14, py-3, gd*3,  5))


# ── Archer ───────────────────────────────────────────────────
def _draw_archer(surf, px, py, c1, c2, team, anim_frame, state):
    bob  = int(math.sin(anim_frame * 0.18) * (2 if state == "walk" else 0))
    bob2 = int(math.sin(anim_frame * 0.18 + math.pi) * (2 if state == "walk" else 0))
    dark1 = tuple(max(0, v - 40) for v in c1)

    draw_shadow(surf, px, py + 14, 18)
    pygame.draw.rect(surf, (50, 35, 20), (px-4, py+10+bob,  4, 5))
    pygame.draw.rect(surf, (50, 35, 20), (px+1, py+10+bob2, 4, 5))
    pygame.draw.rect(surf, dark1,        (px-4, py+6+bob,   4, 5))
    pygame.draw.rect(surf, dark1,        (px+1, py+6+bob2,  4, 5))
    pygame.draw.rect(surf, c2,           (px-5, py-4,  10, 9))
    pygame.draw.rect(surf, c1,           (px-3, py-2,   6, 5))
    pygame.draw.rect(surf, c1,           (px-7, py-3,   3, 6))
    pygame.draw.rect(surf, c1,           (px+4, py-3,   3, 6))
    qd = -1 if team == "blue" else 1
    pygame.draw.rect(surf, (80, 50, 20), (px + qd*5, py-8, 4, 10))
    for i in range(3):
        pygame.draw.rect(surf, GOLD, (px + qd*6, py-10+i*3, 2, 2))
    pygame.draw.rect(surf, SKIN, (px-3, py-9,  7, 5))
    pygame.draw.rect(surf, SKIN, (px-4, py-14, 8, 7))
    pygame.draw.rect(surf, c1,   (px-5, py-17, 10, 6))
    pygame.draw.rect(surf, dark1,(px-4, py-16,  8, 2))
    pygame.draw.rect(surf, c1,   (px-6, py-13,  4, 4))
    ad = 1 if team == "blue" else -1
    pygame.draw.arc(surf, (141, 110, 99),
                    pygame.Rect(px + ad*4, py-10, 12, 18), 0.4, 2.7, 3)
    pygame.draw.line(surf, (180,140,80),
                     (px + ad*10, py-10), (px + ad*10, py+8), 1)


# ── Cavalry ──────────────────────────────────────────────────
def _draw_cavalry(surf, px, py, c1, c2, team, anim_frame, state):
    bob      = int(math.sin(anim_frame * 0.22) * (3 if state == "walk" else 0))
    leg_bob  = int(math.sin(anim_frame * 0.22) * (4 if state == "walk" else 0))
    leg_bob2 = int(math.sin(anim_frame * 0.22 + math.pi) * (4 if state == "walk" else 0))
    dark1 = tuple(max(0, v - 40) for v in c1)

    draw_shadow(surf, px, py + 14, 34)
    pygame.draw.rect(surf, dark1, (px-14, py+6+leg_bob,  5, 10))
    pygame.draw.rect(surf, dark1, (px-7,  py+6+leg_bob2, 5, 10))
    pygame.draw.rect(surf, dark1, (px+2,  py+6+leg_bob,  5, 10))
    pygame.draw.rect(surf, dark1, (px+9,  py+6+leg_bob2, 5, 10))
    pygame.draw.rect(surf, (30,20,10), (px-14, py+14+leg_bob,  5, 3))
    pygame.draw.rect(surf, (30,20,10), (px-7,  py+14+leg_bob2, 5, 3))
    pygame.draw.rect(surf, (30,20,10), (px+2,  py+14+leg_bob,  5, 3))
    pygame.draw.rect(surf, (30,20,10), (px+9,  py+14+leg_bob2, 5, 3))
    pygame.draw.rect(surf, c1,   (px-16, py-4+bob,  32, 12))
    pygame.draw.rect(surf, dark1,(px-16, py-2+bob,  32,  3))
    pygame.draw.rect(surf, c1,   (px+10, py-12+bob,  8, 10))
    pygame.draw.rect(surf, c1,   (px+12, py-18+bob,  9,  8))
    pygame.draw.rect(surf, dark1,(px+10, py-14+bob,  3, 10))
    pygame.draw.rect(surf, dark1,(px+18, py-16+bob,  3,  4))
    pygame.draw.rect(surf, dark1,(px-18, py-2+bob,   3, 12))
    pygame.draw.rect(surf, (80,50,20),(px-4, py-7+bob, 10, 4))
    pygame.draw.rect(surf, c2,   (px-5, py-18+bob, 10, 12))
    pygame.draw.rect(surf, c1,   (px-7, py-16+bob,  3,  8))
    pygame.draw.rect(surf, c1,   (px+4, py-16+bob,  3,  8))
    pygame.draw.rect(surf, SKIN, (px-3, py-23+bob,  7,  6))
    pygame.draw.rect(surf, c1,   (px-4, py-27+bob,  9,  6))
    pygame.draw.rect(surf, dark1,(px-4, py-25+bob,  9,  2))
    sd = 1 if team == "blue" else -1
    pygame.draw.rect(surf, (200,200,200), (px+sd*5,  py-26+bob, sd*20, 2))
    pygame.draw.rect(surf, GOLD,          (px+sd*22, py-28+bob, sd*3,  6))


# ── Cannon ───────────────────────────────────────────────────
def _draw_cannon(surf, px, py, c1, c2, team, anim_frame):
    dark1 = tuple(max(0, v - 40) for v in c1)

    draw_shadow(surf, px, py + 16, 40)
    for wx in [px-14, px+14]:
        pygame.draw.circle(surf, WHEEL, (wx, py+12), 10)
        pygame.draw.circle(surf, dark1, (wx, py+12),  7)
        pygame.draw.circle(surf, WHEEL, (wx, py+12),  4)
        pygame.draw.line(surf, WHEEL, (wx-9, py+12), (wx+9, py+12), 2)
        pygame.draw.line(surf, WHEEL, (wx,   py+3),  (wx,   py+21), 2)
        pygame.draw.line(surf, WHEEL, (wx-6, py+6),  (wx+6, py+18), 2)
        pygame.draw.line(surf, WHEEL, (wx+6, py+6),  (wx-6, py+18), 2)
    pygame.draw.rect(surf, c1,   (px-14, py-4, 28, 16))
    pygame.draw.rect(surf, dark1,(px-14, py-1, 28,  3))
    cd = 1 if team == "blue" else -1
    pygame.draw.rect(surf, BARREL,     (px+cd*2,  py-5, cd*22, 8))
    pygame.draw.rect(surf, dark1,      (px+cd*2,  py-4, cd*20, 2))
    pygame.draw.rect(surf, (80,80,80), (px+cd*22, py-6, cd*4, 10))
    for bx in [cd*6, cd*12, cd*18]:
        pygame.draw.rect(surf, (100,100,100), (px+bx, py-5, cd*2, 8))
    crew_x = px - cd*10
    pygame.draw.rect(surf, (40,30,20), (crew_x-3, py+2,  3, 5))
    pygame.draw.rect(surf, (40,30,20), (crew_x+1, py+2,  3, 5))
    pygame.draw.rect(surf, c2,         (crew_x-4, py-10, 8,12))
    pygame.draw.rect(surf, c1,         (crew_x-6, py-8,  3, 7))
    pygame.draw.rect(surf, c1,         (crew_x+3, py-8,  3, 7))
    pygame.draw.rect(surf, SKIN,       (crew_x-3, py-15, 6, 6))
    pygame.draw.rect(surf, c1,         (crew_x-4, py-20, 8, 6))
    pygame.draw.rect(surf, dark1,      (crew_x-3, py-18, 6, 2))


# ── Engineer ──────────────────────────────────────────────────
def _draw_engineer(surf, px, py, c1, c2, team, anim_frame, state, eng_state):
    """
    Pixel-art engineer:
    - Overalls (c1), tool-belt (gold), hard hat (yellow)
    - Wrench in hand; raises it during BUILD / REPAIR states
    - Animated legs when walking
    """
    bob  = int(math.sin(anim_frame * 0.18) * (2 if state == "walk" else 0))
    bob2 = int(math.sin(anim_frame * 0.18 + math.pi) * (2 if state == "walk" else 0))
    dark1    = tuple(max(0, v - 40) for v in c1)
    GOLD_COL = (255, 200,  40)
    HAT_COL  = (230, 200,  30)
    HAT_DARK = (180, 155,  10)

    draw_shadow(surf, px, py + 14, 18)

    # Legs + boots
    pygame.draw.rect(surf, dark1,        (px-4, py+10+bob,  4, 5))
    pygame.draw.rect(surf, dark1,        (px+1, py+10+bob2, 4, 5))
    pygame.draw.rect(surf, (40, 30, 20), (px-4, py+14+bob,  4, 3))
    pygame.draw.rect(surf, (40, 30, 20), (px+1, py+14+bob2, 4, 3))

    # Body / overalls
    pygame.draw.rect(surf, c1,       (px-5, py-4,  10, 9))
    # Chest pocket detail
    pygame.draw.rect(surf, dark1,    (px-4, py-3,   4, 3))
    # Tool belt
    pygame.draw.rect(surf, GOLD_COL, (px-5, py+4,  10, 2))
    # Belt buckle
    pygame.draw.rect(surf, (200,170,20), (px-1, py+4, 2, 2))

    # Arms
    building = eng_state in ("BUILD", "REPAIR")
    arm_y_l  = py - 7 if building else py - 2
    pygame.draw.rect(surf, c1, (px-8, arm_y_l, 3, 6))
    pygame.draw.rect(surf, c1, (px+5, py - 2,  3, 6))

    # Wrench
    wd = -1 if team == "blue" else 1
    if building:
        # Raised wrench (hammer pose)
        pygame.draw.rect(surf, (160,160,160), (px - 9*wd, arm_y_l - 7, wd*2,  8))
        pygame.draw.rect(surf, (210,210,210), (px - 9*wd, arm_y_l - 9, wd*6,  3))
        pygame.draw.rect(surf, (120,120,120), (px - 9*wd, arm_y_l - 7, wd*2,  2))
    else:
        # Wrench at side
        pygame.draw.rect(surf, (160,160,160), (px + wd*7,  py - 1, wd*8, 2))
        pygame.draw.rect(surf, (210,210,210), (px + wd*13, py - 3, wd*3, 6))
        pygame.draw.rect(surf, (120,120,120), (px + wd*13, py - 3, wd*2, 2))

    # Head + neck
    pygame.draw.rect(surf, SKIN,     (px-3, py-9,   6, 5))
    # Hard hat body
    pygame.draw.rect(surf, HAT_COL,  (px-4, py-15,  8, 7))
    # Hard hat brim
    pygame.draw.rect(surf, HAT_COL,  (px-6, py-9,  12, 2))
    # Hat shadow line
    pygame.draw.rect(surf, HAT_DARK, (px-4, py-15,  8, 2))
    # Hat highlight
    pygame.draw.rect(surf, (255,230,80), (px-3, py-14, 3, 2))


# ── Dead unit ────────────────────────────────────────────────
def _draw_dead(surf, px, py, c1):
    pygame.draw.rect(surf, c1,   (px-10, py+4, 20, 6))
    pygame.draw.rect(surf, SKIN, (px+8,  py+3,  6, 6))
    pygame.draw.rect(surf, c1,   (px-12, py+6,  6, 3))


# ── Cover objects ─────────────────────────────────────────────
def draw_cover(surf: pygame.Surface, covers: list) -> None:
    """Draw all alive cover objects. Called after terrain, before units."""
    for c in covers:
        if c.alive:
            c.draw(surf)


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

    f, s = unit.anim_frame, unit.state

    if unit.unit_type == "cavalry":
        _draw_cavalry(surf, px, py, c1, c2, unit.team, f, s)
        draw_hp_bar(surf, px, py - 34, unit.hp, unit.max_hp)
    elif unit.unit_type == "cannon":
        _draw_cannon(surf, px, py, c1, c2, unit.team, f)
        draw_hp_bar(surf, px, py - 34, unit.hp, unit.max_hp)
    elif unit.unit_type == "archer":
        _draw_archer(surf, px, py, c1, c2, unit.team, f, s)
        draw_hp_bar(surf, px, py - 22, unit.hp, unit.max_hp)
    elif unit.unit_type == "engineer":
        eng_state = getattr(unit, "state", "IDLE")
        _draw_engineer(surf, px, py, c1, c2, unit.team, f, s, eng_state)
        draw_hp_bar(surf, px, py - 26, unit.hp, unit.max_hp)
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
        col = (206,147,216) if bullet.team == "blue" else (255,171,145)
        pygame.draw.line(surf, col,          (bx, by), end, 2)
        pygame.draw.line(surf, (180,140,80), (bx, by),
                         (bx + int(bullet.vx), by + int(bullet.vy)), 2)
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


# ── Wave timer ───────────────────────────────────────────────
def draw_wave_timer(surf, progress: float, wave_num: int) -> None:
    if wave_num == 0:
        return
    bw, bh = 180, 8
    bx = BX + BW // 2 - bw // 2
    by = 10
    pygame.draw.rect(surf, (20, 20, 20), (bx-1, by-1, bw+2, bh+2))
    pygame.draw.rect(surf, (50, 50, 50), (bx,   by,   bw,   bh))
    pygame.draw.rect(surf, GOLD,         (bx,   by,   int(bw * progress), bh))
    if FONT_SM is None:
        return
    lbl = FONT_SM.render("next wave", True, (180, 180, 180))
    surf.blit(lbl, (bx + bw//2 - lbl.get_width()//2, by - 16))


# ── HUD labels ───────────────────────────────────────────────
def draw_hud(surf, units, wave_num, label, msg) -> None:
    if FONT_MD is None or FONT_LG is None:
        return
    if label:
        lbl = FONT_MD.render(label, True, GOLD)
        surf.blit(lbl, (BX + BW//2 - lbl.get_width()//2, H//2 - 14))
    if msg:
        m = FONT_LG.render(msg, True, GOLD)
        surf.blit(m, (BX + BW//2 - m.get_width()//2, H//2 + 20))


# ── Controls hint (no-op — hints live in side panel) ─────────
def draw_controls_hint(surf) -> None:
    pass