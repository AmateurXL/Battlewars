import math
import random
import pygame
from game import debug
from game.particles import Particle
from game.constants import UNIT_COLORS


class Bullet:
    """
    Single projectile. On each update tick it:
      1. checks cover objects for collision first (bullets are blocked by cover)
      2. then checks enemy units
    """

    def __init__(self, x, y, vx, vy, team, dmg, aoe, is_arrow, color1):
        self.x        = x
        self.y        = y
        self.vx       = vx
        self.vy       = vy
        self.team     = team
        self.dmg      = dmg
        self.aoe      = aoe
        self.is_arrow = is_arrow
        self.color    = color1
        self.alive    = True

    # ── Collision helpers ─────────────────────────────────────
    def _hit_radius(self, unit) -> int:
        return {"cannon": 14, "cavalry": 12}.get(unit.unit_type, 8)

    # ── Update ────────────────────────────────────────────────
    def update(self, all_units: list, particles: list,
               covers: list | None = None) -> None:
        if not self.alive:
            return

        self.x += self.vx
        self.y += self.vy

        # Out of bounds
        from game.constants import W, H, PANEL_W
        if self.x < PANEL_W or self.x > W or self.y < 0 or self.y > H:
            self.alive = False
            return

        # ── 1. Cover collision (bullets absorbed / blocked) ───
        if covers:
            for cover in covers:
                if not cover.alive:
                    continue
                # Only enemy team's cover blocks this bullet
                # (own cover doesn't block own bullets)
                if cover.team == self.team:
                    continue
                if cover.collides_point(self.x, self.y, radius=3):
                    debug.log_game(
                        f"[BULLET] blocked by cover #{cover.uid} "
                        f"({cover.cover_type}) team={cover.team}",
                        "warn"
                    )
                    cover.take_damage(self.dmg)
                    self._spawn_hit_particles(particles, self.x, self.y,
                                             (180, 155, 100))
                    self.alive = False
                    return

        # ── 2. Unit collision ─────────────────────────────────
        for unit in all_units:
            if unit.dead or unit.team == self.team:
                continue
            d = math.hypot(unit.x - self.x, unit.y - self.y)
            if d < self._hit_radius(unit):
                if self.aoe > 0:
                    self._explode(all_units, particles)
                else:
                    unit.take_damage(self.dmg, particles)
                    self._spawn_hit_particles(particles, self.x, self.y,
                                             self._team_color())
                self.alive = False
                return

    # ── AOE ───────────────────────────────────────────────────
    def _explode(self, all_units: list, particles: list) -> None:
        from game.constants import W
        debug.log_game(
            f"[BULLET] AOE explosion at ({self.x:.0f},{self.y:.0f}) "
            f"r={self.aoe} team={self.team}",
            "warn"
        )
        hit_count = 0
        for unit in all_units:
            if unit.dead or unit.team == self.team:
                continue
            if math.hypot(unit.x - self.x, unit.y - self.y) < self.aoe:
                unit.take_damage(self.dmg, particles)
                hit_count += 1
        debug.log_debug(f"[BULLET] AOE hit {hit_count} units", "info")
        # Orange explosion particles
        for _ in range(14):
            a   = random.uniform(0, math.tau)
            spd = random.uniform(1.5, 3.5)
            particles.append(Particle(
                self.x, self.y,
                math.cos(a) * spd,
                math.sin(a) * spd - 0.5,
                (255, 152, 0)
            ))

    # ── Particles ─────────────────────────────────────────────
    def _team_color(self):
        return (79, 195, 247) if self.team == "blue" else (239, 83, 80)

    def _spawn_hit_particles(self, particles, x, y, color):
        for _ in range(5):
            a   = random.uniform(0, math.tau)
            spd = random.uniform(0.8, 2.0)
            particles.append(Particle(
                x, y,
                math.cos(a) * spd,
                math.sin(a) * spd - 0.3,
                color
            ))