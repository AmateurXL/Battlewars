import random
from units.base_unit import Unit
from units.types import WAVES
from game.constants import W, WAVE_INTERVAL
from game import debug

class WaveManager:
    def __init__(self):
        self.wave_num   = 0
        self.wave_timer = 0
        self.label      = ""   # shown on screen briefly

    def reset(self):
        self.wave_num   = 0
        self.wave_timer = 0
        self.label      = ""

    def update(self, units: list, game_over: bool) -> bool:
        """Tick timer. Returns True when a new wave is spawned."""
        if game_over:
            return False
        self.wave_timer += 1
        if self.wave_timer >= WAVE_INTERVAL and self.wave_num < len(WAVES):
            self._spawn(units)
            return True
        return False

    def force_next(self, units: list) -> None:
        self._spawn(units)

    def _spawn(self, units: list) -> None:
        comp = WAVES[min(self.wave_num, len(WAVES) - 1)]
        for entry in comp:
            for i in range(entry["count"]):
                bx = 80 + (i % 4) * 28
                rx = W - 80 - (i % 4) * 28
                units.append(Unit("blue", entry["type"], bx))
                units.append(Unit("red",  entry["type"], rx))
        self.wave_num  += 1
        self.wave_timer = 0
        names = ", ".join(f'{e["count"]}x {e["type"]}' for e in comp)
        self.label = f"Wave {self.wave_num} — {names}"
        debug.log_game(f"Wave {self.wave_num} spawned: {names}", "ok")
        debug.log_debug(f"Total units: {len(units)}", "info")

    @property
    def progress(self) -> float:
        return min(self.wave_timer / WAVE_INTERVAL, 1.0)