import random
from units.base_unit import Unit
from units.types import WAVES
from game.constants import W, PANEL_W, WAVE_INTERVAL
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

    def update(self, units: list, covers: list, game_over: bool) -> bool:
        """Tick timer. Returns True when a new wave is spawned."""
        if game_over or self.wave_num >= len(WAVES):
            return False
        self.wave_timer += 1
        if self.wave_timer >= WAVE_INTERVAL:
            self._spawn(units, covers)
            return True
        return False

    def force_next(self, units: list, covers: list) -> None:
        if self.wave_num >= len(WAVES):
            debug.log_debug("[WAVE] already at final wave, ignoring force", "warn")
            return
        self._spawn(units, covers)

    def _spawn(self, units: list, covers: list) -> None:
        from units.engineer import Engineer  # local import avoids circular dependency
        comp = WAVES[min(self.wave_num, len(WAVES) - 1)]
        for entry in comp:
            for i in range(entry["count"]):
                bx = PANEL_W + 60 + (i % 4) * 28
                rx = W - 60 - (i % 4) * 28
                if entry["type"] == "engineer":
                    units.append(Engineer("blue", bx, covers))
                    units.append(Engineer("red",  rx, covers))
                    debug.log_debug(
                        f"[WAVE] spawned engineer pair "
                        f"blue_x={bx} red_x={rx}", "ok"
                    )
                else:
                    units.append(Unit("blue", entry["type"], bx))
                    units.append(Unit("red",  entry["type"], rx))

        self.wave_num  += 1
        self.wave_timer = 0
        names = ", ".join(f'{e["count"]}x {e["type"]}' for e in comp)
        self.label = f"Wave {self.wave_num} — {names}"
        debug.log_game(f"Wave {self.wave_num} spawned: {names}", "ok")
        debug.log_debug(f"Total units after spawn: {len(units)}", "info")

    @property
    def progress(self) -> float:
        return min(self.wave_timer / WAVE_INTERVAL, 1.0)