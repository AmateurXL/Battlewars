import math
import random
from game import debug
from game.constants import GY, PANEL_W, W
from game.cover import CoverObject
from units.base_unit import Unit

# ── Engineer tuning constants ─────────────────────────────────
BUILD_ZONE_OFFSET   = 180    # px from own spawn edge toward centre
ENEMY_FLEE_RANGE    = 90     # if enemy closer than this, engineer flees
DAMAGE_WINDOW       = 180    # frames to look back for ally damage events
DAMAGE_THRESHOLD    = 2      # ≥ N allies hurt in window → trigger build
BUILD_TIME          = 90     # frames spent "building" before cover appears
REPAIR_TIME         = 60     # frames spent "repairing" per repair tick
REPAIR_AMOUNT       = 2      # hp restored per repair tick
REPAIR_RANGE        = 20     # px — must be this close to repair cover
BUILD_COOLDOWN      = 400    # frames between successive builds
MAX_COVER_PER_ENG   = 4      # engineer won't place more than this many objects
PISTOL_RANGE        = 130
PISTOL_RATE         = 90
PISTOL_DMG          = 1

# Build positions: (dx_from_build_zone, dy) — relative offsets for cover cluster
COVER_OFFSETS = [
    (0,   0),
    (18,  0),
    (-18, 0),
    (0,  -14),
]


class Engineer(Unit):
    """
    Engineer unit — extends Unit with a build / repair AI state machine.

    States
    ------
    ADVANCE  → walk toward build zone
    BUILD    → stand still, "hammer" animation, place cover after BUILD_TIME
    REPAIR   → walk to a damaged cover object, repair it
    FLEE     → enemy too close, fall back
    IDLE     → no task; follow ally cluster, fire pistol if in range
    """

    def __init__(self, team: str, x: int, covers: list):
        super().__init__(team, "engineer", x)
        self.covers_ref    = covers          # shared list owned by World
        self.own_covers: list[CoverObject] = []

        # AI state
        self.state         = "ADVANCE"
        self.build_timer   = 0
        self.repair_timer  = 0
        self.build_cd      = 0
        self.repair_target: CoverObject | None = None

        # Damage-monitoring window: stores frame numbers when an ally was hit
        self._ally_hit_log: list[int] = []
        self._frame        = 0

        # Build zone x — midfield, biased toward enemy side
        if team == "blue":
            self.build_x = PANEL_W + BUILD_ZONE_OFFSET + random.randint(-20, 20)
        else:
            self.build_x = W - BUILD_ZONE_OFFSET + random.randint(-20, 20)
        self.build_y = GY - 10 + random.randint(-8, 8)

        debug.log_debug(
            f"[ENG {team}] spawned at ({self.x:.0f},{self.y:.0f}) "
            f"build_zone=({self.build_x:.0f},{self.build_y:.0f})",
            "ok"
        )

    # ── Public: called by World each frame when an ally is hit ───
    def notify_ally_hit(self, frame: int) -> None:
        self._ally_hit_log.append(frame)

    # ── Helpers ──────────────────────────────────────────────────
    def _dist(self, ox: float, oy: float) -> float:
        return math.hypot(self.x - ox, self.y - oy)

    def _at_build_zone(self) -> bool:
        return self._dist(self.build_x, self.build_y) < 12

    def _nearest_enemy(self, all_units) -> "Unit | None":
        enemies = [u for u in all_units if u.team != self.team and not u.dead]
        if not enemies:
            return None
        return min(enemies, key=lambda u: self._dist(u.x, u.y))

    def _nearest_ally(self, all_units) -> "Unit | None":
        allies = [u for u in all_units
                  if u.team == self.team and not u.dead and u is not self]
        if not allies:
            return None
        return min(allies, key=lambda u: self._dist(u.x, u.y))

    def _damage_event_count(self) -> int:
        """Count ally-hit events in the last DAMAGE_WINDOW frames."""
        cutoff = self._frame - DAMAGE_WINDOW
        self._ally_hit_log = [f for f in self._ally_hit_log if f >= cutoff]
        return len(self._ally_hit_log)

    def _enemy_too_close(self, all_units) -> bool:
        ne = self._nearest_enemy(all_units)
        return ne is not None and self._dist(ne.x, ne.y) < ENEMY_FLEE_RANGE

    def _find_repair_target(self) -> "CoverObject | None":
        candidates = [c for c in self.own_covers if c.alive and c.needs_repair]
        if not candidates:
            return None
        return min(candidates, key=lambda c: self._dist(c.x, c.y))

    def _move_toward(self, tx: float, ty: float) -> None:
        dx = tx - self.x
        dy = ty - self.y
        d  = math.hypot(dx, dy)
        if d < 1:
            return
        self.x += (dx / d) * self.speed
        self.y += (dy / d) * self.speed * 0.3
        self.x = max(PANEL_W + 12, min(W - 12, self.x))
        self.y = max(GY - 48, min(GY + 30, self.y))

    def _place_cover(self) -> None:
        if len(self.own_covers) >= MAX_COVER_PER_ENG:
            debug.log_debug(
                f"[ENG {self.team}] max cover reached ({MAX_COVER_PER_ENG}), skipping build",
                "warn"
            )
            return

        # Alternate between sandbag and wall based on count
        ctype = "wall" if len(self.own_covers) % 2 == 0 else "sandbag"
        idx   = len(self.own_covers) % len(COVER_OFFSETS)
        dx, dy = COVER_OFFSETS[idx]

        # Offset slightly toward enemy so cover is in front
        direction = 1 if self.team == "blue" else -1
        cx = self.build_x + direction * dx
        cy = self.build_y + dy

        obj = CoverObject(self.team, ctype, cx, cy)
        self.own_covers.append(obj)
        self.covers_ref.append(obj)

        debug.log_game(
            f"[ENG {self.team}] built {ctype} #{obj.uid} at ({cx:.0f},{cy:.0f})",
            "ok"
        )

    # ── Main update — overrides Unit.update() ────────────────────
    def update(self, all_units: list, bullets: list) -> None:
        if self.dead:
            self.death_timer += 1
            return

        self._frame      += 1
        self.anim_frame  += 1
        if self.flash > 0:
            self.flash   -= 1
        if self.build_cd > 0:
            self.build_cd -= 1
        if self.shoot_cd > 0:
            self.shoot_cd -= 1

        # ── Flee override (highest priority) ─────────────────
        if self._enemy_too_close(all_units):
            if self.state != "FLEE":
                debug.log_debug(f"[ENG {self.team}] → FLEE (enemy close)", "warn")
                self.state = "FLEE"

        # ── State machine ─────────────────────────────────────
        if self.state == "FLEE":
            self._do_flee(all_units)

        elif self.state == "ADVANCE":
            self._do_advance(all_units, bullets)

        elif self.state == "BUILD":
            self._do_build(all_units)

        elif self.state == "REPAIR":
            self._do_repair(all_units)

        elif self.state == "IDLE":
            self._do_idle(all_units, bullets)

    # ── State handlers ────────────────────────────────────────────

    def _do_flee(self, all_units) -> None:
        self.state_label = "FLEE"
        # Move away from nearest enemy
        ne = self._nearest_enemy(all_units)
        if ne:
            dx = self.x - ne.x
            dy = self.y - ne.y
            d  = math.hypot(dx, dy) or 1
            self.x += (dx / d) * self.speed * 1.4
            self.y += (dy / d) * self.speed * 0.3 * 1.4
            self.x = max(PANEL_W + 12, min(W - 12, self.x))
            self.y = max(GY - 48, min(GY + 30, self.y))
        self.state_ = "walk"
        # Re-evaluate once enemy is far enough
        if not self._enemy_too_close(all_units):
            debug.log_debug(f"[ENG {self.team}] FLEE → ADVANCE (enemy retreated)", "info")
            self.state = "ADVANCE"

    def _do_advance(self, all_units, bullets) -> None:
        self.state_ = "walk"
        self._move_toward(self.build_x, self.build_y)

        if self._at_build_zone():
            debug.log_debug(f"[ENG {self.team}] reached build zone → IDLE", "info")
            self.state = "IDLE"
            return

        # Fire pistol at enemies while advancing
        self._try_shoot(all_units, bullets)

    def _do_build(self, all_units) -> None:
        self.state_ = "idle"
        self.build_timer += 1
        if self.build_timer % 20 == 0:
            debug.log_debug(
                f"[ENG {self.team}] building… {self.build_timer}/{BUILD_TIME}", "info"
            )
        if self.build_timer >= BUILD_TIME:
            self._place_cover()
            self.build_timer = 0
            self.build_cd    = BUILD_COOLDOWN
            debug.log_debug(f"[ENG {self.team}] BUILD done → IDLE", "ok")
            self.state = "IDLE"

    def _do_repair(self, all_units) -> None:
        self.state_ = "walk"
        tgt = self.repair_target
        if tgt is None or not tgt.alive or not tgt.needs_repair:
            debug.log_debug(f"[ENG {self.team}] repair target gone → IDLE", "info")
            self.repair_target = None
            self.state         = "IDLE"
            return

        d = self._dist(tgt.x, tgt.y)
        if d > REPAIR_RANGE:
            self._move_toward(tgt.x, tgt.y)
        else:
            self.state_ = "idle"
            self.repair_timer += 1
            if self.repair_timer >= REPAIR_TIME:
                tgt.repair(REPAIR_AMOUNT)
                self.repair_timer = 0
                if not tgt.needs_repair:
                    debug.log_debug(
                        f"[ENG {self.team}] finished repairing cover #{tgt.uid} → IDLE", "ok"
                    )
                    self.repair_target = None
                    self.state         = "IDLE"

    def _do_idle(self, all_units, bullets) -> None:
        self.state_ = "idle"

        # Priority 1: trigger build if damage threshold met and cooldown clear
        if self.build_cd == 0 and self._damage_event_count() >= DAMAGE_THRESHOLD:
            debug.log_game(
                f"[ENG {self.team}] damage threshold met "
                f"({self._damage_event_count()} hits) → BUILD",
                "warn"
            )
            self.state = "BUILD"
            return

        # Priority 2: repair damaged own cover
        rt = self._find_repair_target()
        if rt is not None:
            self.repair_target = rt
            debug.log_debug(
                f"[ENG {self.team}] found damaged cover #{rt.uid} → REPAIR", "warn"
            )
            self.state = "REPAIR"
            return

        # Priority 3: stay near ally cluster
        ally = self._nearest_ally(all_units)
        if ally:
            d = self._dist(ally.x, ally.y)
            if d > 50:
                self._move_toward(ally.x, ally.y)
                self.state_ = "walk"

        # Priority 4: fire pistol
        self._try_shoot(all_units, bullets)

    def _try_shoot(self, all_units, bullets) -> None:
        if self.shoot_cd > 0:
            return
        ne = self._nearest_enemy(all_units)
        if ne and self._dist(ne.x, ne.y) <= PISTOL_RANGE:
            self.shoot_cd = PISTOL_RATE
            direction     = 1 if ne.x > self.x else -1
            from game.bullet import Bullet
            bullets.append(Bullet(
                x        = self.x + direction * 8,
                y        = self.y - 3,
                vx       = direction * (3.5 + random.uniform(0, 0.4)),
                vy       = random.uniform(-1, 1) * 1.8,
                team     = self.team,
                dmg      = PISTOL_DMG,
                aoe      = 0,
                is_arrow = False,
                color1   = self.color1,
            ))
            debug.log_game(
                f"[ENG {self.team}] pistol shot at ({ne.x:.0f},{ne.y:.0f})", "ok"
            )