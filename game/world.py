import pygame
from game import renderer
from game import debug
from game.wave_manager import WaveManager
from game.constants import W, H, GY, PANEL_W, GOLD, UNIT_COLORS


# ── Button ───────────────────────────────────────────────────
class Button:
    def __init__(self, label: str, x: int, y: int, w: int, h: int, action):
        self.label   = label
        self.rect    = pygame.Rect(x, y, w, h)
        self.action  = action
        self.hovered = False

    def draw(self, surf: pygame.Surface, font: pygame.font.Font) -> None:
        col_bg     = (70, 70, 100) if self.hovered else (35, 35, 60)
        col_border = (160,160,210) if self.hovered else (80, 80,120)
        col_text   = (255,255,255) if self.hovered else (190,190,220)
        pygame.draw.rect(surf, col_bg,     self.rect, border_radius=4)
        pygame.draw.rect(surf, col_border, self.rect, 1, border_radius=4)
        txt = font.render(self.label, True, col_text)
        surf.blit(txt, (self.rect.centerx - txt.get_width()  // 2,
                        self.rect.centery - txt.get_height() // 2))

    def handle(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()


# ── World ────────────────────────────────────────────────────
class World:
    def __init__(self, screen: pygame.Surface, window: pygame.Surface):
        self.screen  = screen   # internal canvas
        self.window  = window   # real pygame window (for mouse scaling)
        self.units:     list = []
        self.bullets:   list = []
        self.particles: list = []
        self.waves      = WaveManager()
        self.paused     = False
        self.game_over  = False
        self.msg        = ""
        self.label_timer = 0
        self._font_sm: pygame.font.Font | None = None
        self._font_md: pygame.font.Font | None = None
        self._buttons:  list[Button] = []
        renderer.init_fonts()
        self._build_buttons()

    # ── Button layout ────────────────────────────────────────
    def _build_buttons(self) -> None:
        BW   = PANEL_W - 20
        BH   = 30
        GAP  = 10
        bx   = 10
        by   = 180    # start below the stats block

        labels_actions = [
            ("New Battle",  self.new_battle),
            ("Pause",       self._toggle_pause),
            ("Next Wave",   self._force_wave),
            ("Fullscreen",  pygame.display.toggle_fullscreen),
            ("Quit",        self._quit),
        ]
        self._buttons = [
            Button(lbl, bx, by + i*(BH+GAP), BW, BH, act)
            for i, (lbl, act) in enumerate(labels_actions)
        ]

    # ── Actions ──────────────────────────────────────────────
    def _toggle_pause(self) -> None:
        self.paused = not self.paused
        self._buttons[1].label = "Resume" if self.paused else "Pause"
        debug.log_debug(f"{'PAUSED' if self.paused else 'RESUMED'}", "warn")

    def _force_wave(self) -> None:
        if not self.game_over:
            self.waves.force_next(self.units)
            self.label_timer = 120
            debug.log_debug("Wave forced by player", "warn")

    def _quit(self) -> None:
        pygame.quit()
        raise SystemExit

    # ── Lifecycle ────────────────────────────────────────────
    def new_battle(self) -> None:
        self.units.clear()
        self.bullets.clear()
        self.particles.clear()
        self.waves.reset()
        self.paused    = False
        self.game_over = False
        self.msg       = ""
        self._buttons[1].label = "Pause"
        debug.clear()
        debug.log_game("--- New Battle ---", "warn")
        self.waves.force_next(self.units)
        self.label_timer = 120

    # ── Input ────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            win_w, win_h = self.window.get_size()
            sx = int(event.pos[0] * W / win_w)
            sy = int(event.pos[1] * H / win_h)
            scaled = pygame.event.Event(event.type, {**event.__dict__, 'pos': (sx, sy)})
            for btn in self._buttons:
                btn.handle(scaled)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self._toggle_pause()
            elif event.key == pygame.K_n:
                self.new_battle()
            elif event.key == pygame.K_w and not self.game_over:
                self._force_wave()

    # ── Update ───────────────────────────────────────────────
    def update(self) -> None:
        if self.paused or self.game_over:
            return
        for u in self.units:
            u.update(self.units, self.bullets)
        self.bullets = [b for b in self.bullets if b.alive]
        for b in self.bullets:
            b.update(self.units, self.particles)
        self.bullets   = [b for b in self.bullets if b.alive]
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
            self.game_over = True; self.msg = "DRAW!"
            debug.log_game("Result: DRAW", "warn")
        elif not blue_alive:
            self.game_over = True; self.msg = "RED ARMY WINS!"
            debug.log_game("Result: RED WINS", "err")
        elif not red_alive:
            self.game_over = True; self.msg = "BLUE ARMY WINS!"
            debug.log_game("Result: BLUE WINS", "ok")

    # ── Draw ─────────────────────────────────────────────────
    def draw(self) -> None:
        self.screen.fill((18, 18, 35))          # clear canvas
        self._draw_side_panel()                  # panel first
        renderer.draw_terrain(self.screen)       # terrain right of panel
        renderer.draw_wave_timer(self.screen, self.waves.progress, self.waves.wave_num)

        for u in self.units:
            if u.dead:  renderer.draw_unit(self.screen, u)
        for u in self.units:
            if not u.dead: renderer.draw_unit(self.screen, u)
        for b in self.bullets:
            renderer.draw_bullet(self.screen, b)
        for p in self.particles:
            renderer.draw_particle(self.screen, p)

        label = self.waves.label if self.label_timer > 0 else ""
        renderer.draw_hud(self.screen, self.units, self.waves.wave_num, label, self.msg)

        self._draw_side_panel()

        if self.paused:
            self._draw_paused()

    def _get_fonts(self):
        if not self._font_sm:
            self._font_sm = pygame.font.SysFont("monospace", 12)
            self._font_md = pygame.font.SysFont("monospace", 14)
        return self._font_sm, self._font_md

    def _draw_side_panel(self) -> None:
        fsm, fmd = self._get_fonts()
        surf = self.screen

        # Panel background
        pygame.draw.rect(surf, (18, 18, 35),  (0, 0, PANEL_W, H))
        pygame.draw.rect(surf, (60, 60, 90),  (0, 0, PANEL_W, H), 1)
        pygame.draw.line(surf, (60, 60, 90),  (PANEL_W, 0), (PANEL_W, H), 1)

        # ── Title ────────────────────────────────────────────
        title = fmd.render("BATTLEWARS", True, GOLD)
        surf.blit(title, (PANEL_W//2 - title.get_width()//2, 14))
        pygame.draw.line(surf, (60,60,90), (10, 34), (PANEL_W-10, 34), 1)

        # ── Wave info ────────────────────────────────────────
        wave_lbl  = fsm.render(f"Wave  {self.waves.wave_num} / 5", True, (200,200,200))
        surf.blit(wave_lbl, (10, 44))

        # Wave progress bar
        bw = PANEL_W - 20
        pygame.draw.rect(surf, (40,40,60),  (10, 62, bw, 8))
        pygame.draw.rect(surf, GOLD,        (10, 62, int(bw * self.waves.progress), 8))
        pygame.draw.rect(surf, (80,80,110), (10, 62, bw, 8), 1)

        # ── Unit counts ──────────────────────────────────────
        pygame.draw.line(surf, (60,60,90), (10, 80), (PANEL_W-10, 80), 1)
        blue = sum(1 for u in self.units if u.team=="blue" and not u.dead)
        red  = sum(1 for u in self.units if u.team=="red"  and not u.dead)
        total= len([u for u in self.units if not u.dead])

        b_lbl = fsm.render(f"Blue  {blue:>3}", True, (79,195,247))
        r_lbl = fsm.render(f"Red   {red:>3}",  True, (239,83,80))
        t_lbl = fsm.render(f"Total {total:>3}", True, (180,180,180))
        surf.blit(b_lbl, (10, 90))
        surf.blit(r_lbl, (10, 107))
        surf.blit(t_lbl, (10, 124))

        # ── Unit type breakdown ───────────────────────────────
        pygame.draw.line(surf, (60,60,90), (10, 145), (PANEL_W-10, 145), 1)
        types = ["soldier","archer","cavalry","cannon"]
        ty = 152
        for ut in types:
            bc = sum(1 for u in self.units if u.unit_type==ut and u.team=="blue" and not u.dead)
            rc = sum(1 for u in self.units if u.unit_type==ut and u.team=="red"  and not u.dead)
            col = UNIT_COLORS[ut]["blue"][1]
            lbl = fsm.render(f"{ut:<8} B{bc:>2}  R{rc:>2}", True, col)
            surf.blit(lbl, (10, ty))
            ty += 15

        # ── Buttons ──────────────────────────────────────────
        pygame.draw.line(surf, (60,60,90), (10, ty+2), (PANEL_W-10, ty+2), 1)
        for btn in self._buttons:
            btn.draw(surf, fsm)

        # ── Keyboard hints ───────────────────────────────────
        hints = [("SPACE","Pause"),("N","New Battle"),("W","Next Wave")]
        hy = H - 70
        hint_hdr = fsm.render("Shortcuts", True, (100,100,130))
        surf.blit(hint_hdr, (10, hy - 14))
        for key, desc in hints:
            k_surf = fsm.render(f"[{key}]", True, GOLD)
            d_surf = fsm.render(desc, True, (140,140,160))
            surf.blit(k_surf, (10,  hy))
            surf.blit(d_surf, (60,  hy))
            hy += 14

    def draw_debug(self, screen: pygame.Surface) -> None:
        debug.draw(screen)

    def _draw_paused(self) -> None:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))
        fnt = pygame.font.SysFont("monospace", 28)
        txt = fnt.render("PAUSED", True, GOLD)
        self.screen.blit(txt, (W//2 - txt.get_width()//2, H//2 - 14))