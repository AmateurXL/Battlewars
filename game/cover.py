import pygame
from game import debug

# ── Cover type definitions ────────────────────────────────────
COVER_TYPES = {
    "sandbag": {
        "hp":       None,   # indestructible
        "w":        14,
        "h":        9,
        "color":    (180, 155, 100),
        "dark":     (130, 108,  65),
        "accent":   (210, 185, 130),
    },
    "wall": {
        "hp":       8,
        "w":        26,
        "h":        15,
        "color":    (120, 110, 100),
        "dark":     ( 80,  72,  65),
        "accent":   (160, 150, 138),
    },
}


class CoverObject:
    """
    A piece of cover placed by an Engineer.

    Attributes
    ----------
    team        : str   — which team owns / placed this cover
    cover_type  : str   — "sandbag" | "wall"
    x, y        : float — centre position on the battlefield
    hp          : int | None — current hp; None = indestructible
    max_hp      : int | None
    alive       : bool  — False once hp reaches 0
    """

    _id_counter = 0  # simple unique id for debug traces

    def __init__(self, team: str, cover_type: str, x: float, y: float):
        CoverObject._id_counter += 1
        self.uid        = CoverObject._id_counter
        self.team       = team
        self.cover_type = cover_type
        self.x          = x
        self.y          = y

        cfg             = COVER_TYPES[cover_type]
        self.w          = cfg["w"]
        self.h          = cfg["h"]
        self.max_hp     = cfg["hp"]
        self.hp         = cfg["hp"]   # None for indestructible
        self.alive      = True

        self._cfg       = cfg
        self.flash      = 0           # hit flash timer

        debug.log_debug(
            f"[COVER #{self.uid}] spawned {cover_type} "
            f"team={team} pos=({x:.0f},{y:.0f}) hp={self.hp}",
            "ok"
        )

    # ── Geometry ─────────────────────────────────────────────
    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.w // 2),
            int(self.y - self.h // 2),
            self.w,
            self.h,
        )

    def collides_point(self, px: float, py: float, radius: float = 4) -> bool:
        """True if a circle at (px, py) with given radius overlaps this cover."""
        r = self.rect.inflate(int(radius * 2), int(radius * 2))
        return r.collidepoint(int(px), int(py))

    # ── Damage ───────────────────────────────────────────────
    def take_damage(self, dmg: int) -> None:
        if self.hp is None:
            # indestructible — absorb silently
            debug.log_debug(
                f"[COVER #{self.uid}] bullet absorbed (indestructible)", "info"
            )
            return

        self.hp    = max(0, self.hp - dmg)
        self.flash = 5
        debug.log_game(
            f"[COVER #{self.uid}] {self.cover_type} hit "
            f"hp={self.hp}/{self.max_hp} team={self.team}",
            "warn"
        )

        if self.hp == 0:
            self.alive = False
            debug.log_game(
                f"[COVER #{self.uid}] {self.cover_type} DESTROYED team={self.team}",
                "err"
            )

    # ── Repair (called by Engineer) ───────────────────────────
    def repair(self, amount: int) -> None:
        if self.hp is None or self.hp >= self.max_hp:
            return
        before  = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        debug.log_debug(
            f"[COVER #{self.uid}] repaired {before}→{self.hp}/{self.max_hp}",
            "ok"
        )

    @property
    def needs_repair(self) -> bool:
        return self.hp is not None and self.alive and self.hp < self.max_hp

    # ── Draw ─────────────────────────────────────────────────
    def draw(self, surf: pygame.Surface) -> None:
        if not self.alive:
            return

        cfg  = self._cfg
        rx   = int(self.x - self.w // 2)
        ry   = int(self.y - self.h // 2)

        # Flash white on hit
        draw_col = (230, 230, 230) if (self.flash > 0 and self.flash % 2 == 0) else cfg["color"]
        dark_col = cfg["dark"]
        acc_col  = cfg["accent"]

        if self.cover_type == "sandbag":
            self._draw_sandbag(surf, rx, ry, draw_col, dark_col, acc_col)
        else:
            self._draw_wall(surf, rx, ry, draw_col, dark_col, acc_col)

        if self.flash > 0:
            self.flash -= 1

        # HP bar for destructible cover
        if self.hp is not None:
            self._draw_hp(surf, rx, ry)

    def _draw_sandbag(self, surf, rx, ry, col, dark, acc):
        """Three stacked sandbags, pixel-art style."""
        w, h = self.w, self.h
        # base bag
        pygame.draw.rect(surf, dark, (rx,       ry + h//2, w,     h//2))
        pygame.draw.rect(surf, col,  (rx + 1,   ry + h//2, w - 2, h//2 - 1))
        # top bag (slightly smaller, centred)
        pygame.draw.rect(surf, dark, (rx + 2,   ry + 1,    w - 4, h//2))
        pygame.draw.rect(surf, col,  (rx + 3,   ry + 2,    w - 6, h//2 - 2))
        # highlight seam
        pygame.draw.rect(surf, acc,  (rx + 2,   ry + h//2, w - 4, 1))

    def _draw_wall(self, surf, rx, ry, col, dark, acc):
        """Brick wall with damage cracks."""
        w, h = self.w, self.h
        pygame.draw.rect(surf, col,  (rx,     ry,     w,     h))
        pygame.draw.rect(surf, dark, (rx,     ry,     w,     2))       # top shadow
        pygame.draw.rect(surf, dark, (rx,     ry,     2,     h))       # left shadow
        pygame.draw.rect(surf, acc,  (rx + 2, ry + 2, w - 3, 1))      # highlight
        # brick lines
        for brow in range(0, h, 5):
            pygame.draw.line(surf, dark, (rx, ry + brow), (rx + w, ry + brow), 1)
        for bcol in [w // 3, w * 2 // 3]:
            pygame.draw.line(surf, dark, (rx + bcol, ry), (rx + bcol, ry + h), 1)

        # damage state — draw cracks as hp drops
        if self.hp is not None and self.max_hp:
            ratio = self.hp / self.max_hp
            if ratio < 0.75:
                pygame.draw.line(surf, dark, (rx + 4,  ry + 2),  (rx + 7,  ry + 8),  1)
            if ratio < 0.5:
                pygame.draw.line(surf, dark, (rx + 14, ry + 3),  (rx + 10, ry + 10), 1)
                pygame.draw.line(surf, dark, (rx + 10, ry + 10), (rx + 13, ry + 14), 1)
            if ratio < 0.25:
                pygame.draw.line(surf, dark, (rx + 18, ry + 1),  (rx + 20, ry + 7),  1)
                pygame.draw.line(surf, dark, (rx + 5,  ry + 8),  (rx + 2,  ry + 13), 1)

    def _draw_hp(self, surf, rx, ry):
        bw, bh = self.w, 3
        by     = ry - 5
        pygame.draw.rect(surf, (40, 40, 40), (rx, by, bw, bh))
        ratio  = self.hp / self.max_hp
        col    = (76,175,80) if ratio > 0.5 else (255,152,0) if ratio > 0.25 else (244,67,54)
        pygame.draw.rect(surf, col, (rx, by, int(bw * ratio), bh))