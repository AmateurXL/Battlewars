# Battlewars — Project Documentation

## Overview
Battlewars is a pixel-art army battle simulation built in Python with Pygame. Two armies (blue vs red) fight across 5 escalating waves, each with a mix of unit types. All AI, physics, and rendering are handled procedurally — no external assets required.

---

## Tech Stack
| Item | Detail |
|---|---|
| Language | Python 3.12+ (tested on 3.14 with pygame-ce) |
| Framework | pygame-ce 2.5.7 |
| Python min. | 3.12 (3.14 requires pygame-ce instead of pygame) |
| IDE | VS Code |
| Repo | https://github.com/AmateurXL/Battlewars |

---

## Project Structure
```
Battlewars/
├── main.py                  ← Entry point
├── requirements.txt         ← Dependencies
├── README.md
├── .gitignore
│
├── game/
│   ├── __init__.py
│   ├── constants.py         ← All game constants and colour palettes
│   ├── world.py             ← Main game loop controller + side panel + buttons
│   ├── renderer.py          ← All drawing functions
│   ├── wave_manager.py      ← Wave spawning and timing
│   ├── bullet.py            ← Bullet logic and hit detection
│   ├── particles.py         ← Particle system
│   └── debug.py             ← Dual-panel debug overlay (always visible)
│
├── units/
│   ├── __init__.py
│   ├── base_unit.py         ← Unit class with AI, movement, combat
│   ├── types.py             ← Unit configs and wave compositions
│   └── ai.py                ← (stub) Reserved for advanced AI
│
└── audio/
    └── __init__.py          ← (stub) Reserved for sound effects
```

---

## File Descriptions

### `main.py`
Entry point. Initialises pygame, creates a resizable game window starting at 1280x720, renders all game logic to a fixed internal canvas, then scales it to the current window size every frame for pixel-perfect scaling. Debug panels are drawn after the scale blit at native window resolution for crisp text. Supports fullscreen toggle via F11.

---

### `game/constants.py`
Pure data file — no imports. Defines all shared constants used across the project:
- Window size (`W=1280`, `H=720`, `FPS=60`, `GY`, `PANEL_W=220`)
- Colour tuples for terrain, UI, HP bars, unit palettes
- `WAVE_INTERVAL` — frames between auto wave spawns
- `UNIT_COLORS` — per-team colour pairs for each unit type

---

### `game/world.py`
Top-level game state controller. Owns all lists (`units`, `bullets`, `particles`), the side panel, and all buttons. Orchestrates every subsystem each frame.

**Button class** — lightweight clickable button with hover state, drawn directly onto the canvas. Mouse coordinates are scaled from window size back to canvas coordinates so clicks register correctly at any window size.

Key methods:
| Method | Purpose |
|---|---|
| `new_battle()` | Resets all state, clears debug logs, spawns wave 1 |
| `handle_event()` | Keyboard + scaled mouse input for buttons |
| `update()` | Ticks units, bullets, particles, wave manager, victory check |
| `draw()` | Clears canvas, draws side panel, terrain, units, HUD |
| `_draw_side_panel()` | Renders the left panel with all stats and buttons |
| `draw_debug()` | Draws debug overlay at native window resolution after scale |

**Side panel contents (220px, left side):**
- BATTLEWARS title
- Wave number + progress bar
- Live unit counts (Blue / Red / Total)
- Per-type unit breakdown (soldier, archer, cavalry, cannon)
- 5 action buttons
- Keyboard shortcut reference

---

### `game/renderer.py`
All pygame drawing code. Stateless functions that take a surface and draw to it. The battlefield starts at `BX = PANEL_W` and spans `BW = W - PANEL_W` pixels wide.

Key functions:
| Function | Purpose |
|---|---|
| `init_fonts()` | Loads monospace fonts (SM/MD/LG) once on startup |
| `draw_terrain()` | Sky gradient, ground layers, trees, stars, divider line — offset by BX |
| `draw_unit()` | Dispatches to per-type drawers with flash effect |
| `_draw_soldier()` | Helmet, belt, boots, chest armour, animated legs |
| `_draw_archer()` | Hood, quiver with arrows, bow arc + bowstring |
| `_draw_cavalry()` | Full horse anatomy, 4 animated legs, rider with lance |
| `_draw_cannon()` | Spoked wheels, barrel with bands, crew member |
| `draw_shadow()` | Alpha shadow beneath each unit |
| `draw_bullet()` | Renders bullets, arrows (with shaft), cannonballs |
| `draw_particle()` | Alpha-faded pixel particles with transparent clear |
| `draw_hud()` | Wave announce label + result message centered on battlefield |
| `draw_wave_timer()` | Gold progress bar centered above battlefield |
| `draw_controls_hint()` | No-op — hints live in side panel |

---

### `game/debug.py`
Always-visible dual-panel debug overlay rendered at native window resolution (after canvas scale), ensuring crisp readable text at any window size.

| Panel | Content |
|---|---|
| Left — Game Events | Unit fires, hits, deaths, wave spawns, battle results |
| Right — Debug / System | Pause/resume, unit counts, forced waves |

Features:
- Automatic text wrapping for long messages
- `▲ more above` indicator when lines overflow the panel
- Panel width and position calculated dynamically from window size
- Colour-coded log levels: 🔵 ok, 🟠 warn, 🔴 err, gray info

Key functions:
| Function | Purpose |
|---|---|
| `log_game(msg, level)` | Append to game events panel |
| `log_debug(msg, level)` | Append to debug/system panel |
| `clear()` | Wipe both logs (called on new battle) |
| `draw(surf)` | Render both panels at native window resolution |

---

### `game/wave_manager.py`
Manages wave progression. Tracks wave number and frame timer. Spawns both blue and red units symmetrically from `WAVES` config, offset to start after the side panel.

Key properties/methods:
| Item | Purpose |
|---|---|
| `wave_num` | Current wave index |
| `progress` | Float 0–1 for the wave timer bar |
| `update()` | Auto-spawns next wave when timer expires |
| `force_next()` | Manual wave skip (W key or button) |

---

### `game/bullet.py`
Bullet data and per-frame physics. Moves by velocity each tick, checks collision radius against all enemy units, handles both single-hit and AOE damage.

Key methods:
| Method | Purpose |
|---|---|
| `update()` | Move + hit detection |
| `_explode()` | AOE radius damage + orange particles |
| `_spawn_hit_particles()` | Team-coloured hit sparks |

---

### `game/particles.py`
Minimal particle class. Each particle has position, velocity, colour, and a life counter. `update()` returns `False` when life hits zero. Draw uses `SRCALPHA` with explicit transparent clear to prevent ghost rectangles.

---

### `units/base_unit.py`
The `Unit` class — handles all per-unit state, AI behaviour, and combat. Units are clamped to stay within the battlefield (right of `PANEL_W`).

Key methods:
| Method | Purpose |
|---|---|
| `nearest_enemy()` | Finds closest living enemy by distance |
| `update()` | Moves toward target or holds and shoots |
| `_fire()` | Creates a `Bullet` with correct speed/spread per type, logs to debug |
| `take_damage()` | Reduces HP, sets flash timer, spawns death particles, logs hit/death |

---

### `units/types.py`
Pure data. Defines `UnitConfig` dataclass and two key data structures:

`UNIT_TYPES` — stats per unit type:
| Unit | HP | Speed | Range | Fire rate | Damage | AOE |
|---|---|---|---|---|---|---|
| Soldier | 3 | 0.45 | 110 | 70 | 1 | 0 |
| Archer | 2 | 0.30 | 200 | 110 | 1 | 0 |
| Cavalry | 5 | 1.10 | 18 | 40 | 2 | 0 |
| Cannon | 6 | 0.12 | 160 | 200 | 3 | 28 |

`WAVES` — 5 escalating wave compositions, from pure soldiers to full mixed armies.

---

### `units/ai.py`
Empty stub. Reserved for future advanced AI behaviours such as flanking, target priority, formation logic, or retreat.

---

### `audio/__init__.py`
Empty stub. Reserved for `pygame.mixer` sound integration. The sound design spec (reverb, chorus, distortion, per-unit effects) is documented separately in the browser version.

---

## Controls
| Input | Action |
|---|---|
| `SPACE` | Pause / resume |
| `N` | New battle |
| `W` | Force next wave |
| `F11` | Toggle fullscreen |
| `Alt+F4` / close | Quit |
| Mouse click | Side panel buttons |

---

## Rendering Architecture
```
pygame window (resizable, starts 1280x720)
    └── canvas (fixed 1280x720)
            ├── screen.fill()            ← clear to dark background
            ├── _draw_side_panel()       ← 220px left panel
            ├── draw_terrain()           ← starts at x=220 (BX)
            ├── draw_wave_timer()
            ├── draw_unit() × n          ← dead units first, then alive
            ├── draw_bullet() × n
            ├── draw_particle() × n
            └── draw_hud()
    └── pygame.transform.scale → screen
    └── debug.draw(screen)               ← native res, always on top
```

---

## Setup
```bash
git clone https://github.com/AmateurXL/Battlewars
cd Battlewars
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python main.py
```

> **Note:** Python 3.13+ requires `pip install pygame-ce` instead of `pygame`.

---

## Roadmap
- [ ] Sound effects via `pygame.mixer` (design spec complete)
- [ ] Advanced unit AI in `units/ai.py`
- [ ] Player-controlled hero unit
- [ ] Cover / destructible terrain
- [ ] Upgrade panel between waves
- [ ] Unit selection and formation controls