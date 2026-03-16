import pygame
from collections import deque
from game.constants import W, H

# ── Config ───────────────────────────────────────────────────
MAX_LINES   = 20
PANEL_H     = 120         # height of each log panel
PANEL_W     = W // 2 - 4  # each panel = half screen width
FONT_SIZE   = 10
LINE_H      = 12
PAD         = 4
ALPHA       = 220
BOTTOM_Y    = H - PANEL_H - 1   # sits flush at the bottom

# Colours
COL_BG      = (8,   8,  18, ALPHA)
COL_BORDER  = (60,  60,  80)
COL_TITLE   = (255, 215,  0)
COL_OK      = (79,  195, 247)
COL_WARN    = (255, 152,  0)
COL_ERR     = (239,  83, 80)
COL_DEFAULT = (170, 170, 170)

LEVEL_COLORS = {
    "ok":   COL_OK,
    "warn": COL_WARN,
    "err":  COL_ERR,
    "info": COL_DEFAULT,
}

_font: pygame.font.Font | None = None

def _get_font() -> pygame.font.Font:
    global _font
    if _font is None:
        _font = pygame.font.SysFont("monospace", FONT_SIZE)
    return _font


# ── Log stores ───────────────────────────────────────────────
_game_log:  deque = deque(maxlen=MAX_LINES)
_debug_log: deque = deque(maxlen=MAX_LINES)

def log_game(msg: str, level: str = "info") -> None:
    _game_log.appendleft((msg, level))

def log_debug(msg: str, level: str = "info") -> None:
    _debug_log.appendleft((msg, level))

def clear() -> None:
    _game_log.clear()
    _debug_log.clear()


# ── Text wrap helper ─────────────────────────────────────────
def _wrap(font: pygame.font.Font, text: str, max_w: int) -> list[str]:
    """Break text into lines that fit within max_w pixels."""
    words = text.split(" ")
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if font.size(test)[0] <= max_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


# ── Panel renderer ───────────────────────────────────────────
def _draw_panel(surf: pygame.Surface, x: int, y: int,
                title: str, lines: deque) -> None:
    font     = _get_font()
    max_text = PANEL_W - PAD * 2

    # Background
    bg = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    bg.fill(COL_BG)
    surf.blit(bg, (x, y))
    pygame.draw.rect(surf, COL_BORDER, (x, y, PANEL_W, PANEL_H), 1)

    # Title bar
    title_h = LINE_H + PAD
    pygame.draw.rect(surf, (15, 15, 30), (x, y, PANEL_W, title_h))
    pygame.draw.line(surf, COL_BORDER,
                     (x, y + title_h), (x + PANEL_W, y + title_h))
    surf.blit(font.render(title, True, COL_TITLE), (x + PAD, y + PAD // 2))

    # Log lines — newest first, wrapped
    ty = y + title_h + PAD
    max_y = y + PANEL_H - PAD

    for msg, level in lines:
        color    = LEVEL_COLORS.get(level, COL_DEFAULT)
        wrapped  = _wrap(font, msg, max_text)
        for line in wrapped:
            if ty + LINE_H > max_y:
                # draw a scroll indicator and stop
                surf.blit(font.render("  ▲ more above", True, (100, 100, 100)),
                          (x + PAD, max_y - LINE_H))
                return
            surf.blit(font.render(line, True, color), (x + PAD, ty))
            ty += LINE_H


# ── Main draw call — always visible at bottom ────────────────
def draw(surf: pygame.Surface) -> None:
    """Call once per frame. Always rendered at the bottom of the screen."""
    _draw_panel(surf, 2,            BOTTOM_Y, " GAME EVENTS",    _game_log)
    _draw_panel(surf, PANEL_W + 4,  BOTTOM_Y, " DEBUG / SYSTEM", _debug_log)


# ── Keep toggle/is_visible as no-ops so existing calls don't break ──
def toggle() -> None:
    pass

def is_visible() -> bool:
    return True