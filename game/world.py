import pygame
from game import renderer
from game.wave_manager import WaveManager
from game.constants import W, H, GY

class World:
    def __init__(self, screen: pygame.Surface):
        self.screen    = screen
        self.units:    list = []
        self.bullets:  list = []
        self.particles: list = []
        self.waves     = WaveManager()
        self.paused    = False
        self.game_over = False
        self.msg       = ""
        self.label_timer = 0
        renderer.init_fonts()

    # ── Lifecycle ────────────────────────────────────────────
    def new_battle(self) -> None:
        self.units.clear()
        self.bullets.clear()
        self.particles.clear()
        self.waves.reset()
        self.paused    = False
        self.game_over = False
        self.msg       = ""
        self.waves.force_next(self.units)
        self.label_timer = 120

    # ── Input ────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.key == pygame.K_n:
                self.new_battle()
            elif event.key == pygame.K_w and not self.game_over:
                self.waves.force_next(self.units)
                self.label_timer = 120

    # ── Update ───────────────────────────────────────────────
    def update(self) -> None:
        if self.paused or self.game_over:
            return

        for u in self.units:
            u.update(self.units, self.bullets)

        self.bullets  = [b for b in self.bullets if b.alive]
        for b in self.bullets:
            b.update(self.units, self.particles)
        self.bullets = [b for b in self.bullets if b.alive]

        self.particles = [p for p in self.particles if p.update()]

        spawned = self.waves.update(self.units, self.game_over)
        if spawned:
            self.label_timer = 120

        if self.label_timer > 0:
            self.label_timer -= 1

        self._check_victory()

    def _check_victory(self) -> None:
        if self.game_over or self.waves.wave_num == 0:
            return
        blue_alive = any(u.team == "blue" and not u.dead for u in self.units)
        red_alive  = any(u.team == "red"  and not u.dead for u in self.units)
        if not blue_alive and not red_alive:
            self.game_over = True
            self.msg = "DRAW!"
        elif not blue_alive:
            self.game_over = True
            self.msg = "RED ARMY WINS!"
        elif not red_alive:
            self.game_over = True
            self.msg = "BLUE ARMY WINS!"

    # ── Draw ─────────────────────────────────────────────────
    def draw(self) -> None:
        renderer.draw_terrain(self.screen)
        renderer.draw_wave_timer(self.screen, self.waves.progress, self.waves.wave_num)

        for u in self.units:
            if u.dead:
                renderer.draw_unit(self.screen, u)
        for u in self.units:
            if not u.dead:
                renderer.draw_unit(self.screen, u)

        for b in self.bullets:
            renderer.draw_bullet(self.screen, b)
        for p in self.particles:
            renderer.draw_particle(self.screen, p)

        label = self.waves.label if self.label_timer > 0 else ""
        renderer.draw_hud(self.screen, self.units, self.waves.wave_num, label, self.msg)
        renderer.draw_controls_hint(self.screen)

        if self.paused:
            self._draw_paused()

    def _draw_paused(self) -> None:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))
        fnt = pygame.font.SysFont("monospace", 28)
        txt = fnt.render("PAUSED", True, (255, 215, 0))
        self.screen.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - 14))