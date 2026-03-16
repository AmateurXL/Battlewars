import math
import random
from game.constants import W, GY, UNIT_COLORS
from game.particles import Particle
from game import debug
from units.types import UNIT_TYPES


class Unit:
    def __init__(self, team: str, unit_type: str, x: int):
        self.team      = team
        self.unit_type = unit_type
        cfg            = UNIT_TYPES[unit_type]

        self.x         = x + random.uniform(-15, 15)
        self.y         = GY - 14 + random.uniform(0, 22)
        self.hp        = cfg.hp
        self.max_hp    = cfg.hp
        self.speed     = cfg.speed * random.uniform(0.85, 1.15)
        self.range     = cfg.range
        self.shoot_rate = cfg.shoot_rate * random.uniform(0.85, 1.15)
        self.dmg       = cfg.dmg
        self.aoe       = cfg.aoe
        self.shoot_cd  = random.uniform(0, self.shoot_rate)

        self.state       = "walk"
        self.anim_frame  = random.uniform(0, 100)
        self.dead        = False
        self.death_timer = 0
        self.flash       = 0

        c = UNIT_COLORS[unit_type][team]
        self.color1 = c[0]
        self.color2 = c[1]

    # ── AI ──────────────────────────────────────────────────
    def nearest_enemy(self, all_units: list) -> "Unit | None":
        enemies = [u for u in all_units if u.team != self.team and not u.dead]
        if not enemies:
            return None
        return min(enemies, key=lambda u: math.hypot(u.x - self.x, u.y - self.y))

    def update(self, all_units: list, bullets: list) -> None:
        if self.dead:
            self.death_timer += 1
            return
        if self.flash > 0:
            self.flash -= 1

        self.anim_frame += 1
        self.shoot_cd   -= 1

        target = self.nearest_enemy(all_units)
        if not target:
            return

        dx   = target.x - self.x
        dy   = target.y - self.y
        dist = math.hypot(dx, dy)
        direction = 1 if dx > 0 else -1

        if dist > self.range:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed * 0.3
            self.state = "walk"
        else:
            self.state = "idle"
            if self.shoot_cd <= 0:
                self.shoot_cd = self.shoot_rate
                self._fire(direction, bullets)

        self.x = max(20, min(W - 20, self.x))
        self.y = max(GY - 48, min(GY + 30, self.y))

    def _fire(self, direction: int, bullets: list) -> None:
        from game.bullet import Bullet   # local import breaks bullet ↔ unit cycle
        spd_map = {"cannon": 2.5, "archer": 2.8}
        spd     = spd_map.get(self.unit_type, 4.0) + random.uniform(0, 0.5)
        spread  = 1.5 if self.unit_type == "cannon" else 2.5
        bullets.append(Bullet(
            x        = self.x + direction * 10,
            y        = self.y - 3,
            vx       = direction * spd,
            vy       = random.uniform(-1, 1) * spread,
            team     = self.team,
            dmg      = self.dmg,
            aoe      = self.aoe,
            is_arrow = (self.unit_type == "archer"),
            color1   = self.color1,
        ))

    # ── Combat ──────────────────────────────────────────────
    def take_damage(self, dmg: int, particles: list) -> None:
        self.hp   -= dmg
        self.flash = 6
        debug.log_game(f"HIT [{self.team}] {self.unit_type} hp={self.hp}/{self.max_hp}", "warn")
        if self.hp <= 0:
            self.dead = True
            debug.log_game(f"DEATH [{self.team}] {self.unit_type}", "err")
            for _ in range(8):
                a   = random.uniform(0, math.tau)
                spd = random.uniform(1, 3)
                particles.append(Particle(
                    self.x, self.y,
                    math.cos(a) * spd,
                    math.sin(a) * spd - 1,
                    (255, 204, 0)
                ))