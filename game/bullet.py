import math
import random
from game.constants import W, H
from game.particles import Particle


class Bullet:
    def __init__(self, x, y, vx, vy, team, dmg, aoe, is_arrow, color1):
        self.x        = x
        self.y        = y
        self.vx       = vx
        self.vy       = vy
        self.team     = team
        self.dmg      = dmg
        self.aoe      = aoe
        self.is_arrow = is_arrow
        self.color    = (255, 204, 2) if team == "blue" else (255, 87, 34)
        self.alive    = True

    def update(self, units: list, particles: list) -> None:
        self.x += self.vx
        self.y += self.vy

        if not (0 < self.x < W and 0 < self.y < H):
            self.alive = False
            return

        for unit in units:
            if unit.dead or unit.team == self.team:
                continue
            hit_r = {"cannon": 14, "cavalry": 12}.get(unit.unit_type, 8)
            if math.hypot(unit.x - self.x, unit.y - self.y) < hit_r:
                if self.aoe > 0:
                    self._explode(units, particles)
                else:
                    unit.take_damage(self.dmg, particles)
                    self._spawn_hit_particles(particles)
                self.alive = False
                return

    def _explode(self, units: list, particles: list) -> None:
        for unit in units:
            if not unit.dead and unit.team != self.team:
                if math.hypot(unit.x - self.x, unit.y - self.y) < self.aoe:
                    unit.take_damage(self.dmg, particles)
        for _ in range(12):
            a = random.uniform(0, math.tau)
            s = random.uniform(1, 3)
            particles.append(Particle(self.x, self.y,
                                      math.cos(a) * s,
                                      math.sin(a) * s - 1,
                                      (255, 152, 0)))

    def _spawn_hit_particles(self, particles: list) -> None:
        col = (79, 195, 247) if self.team == "blue" else (239, 83, 80)
        for _ in range(5):
            a = random.uniform(0, math.tau)
            s = random.uniform(1, 2)
            particles.append(Particle(self.x, self.y,
                                      math.cos(a) * s,
                                      math.sin(a) * s - 1,
                                      col))