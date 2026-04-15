# Asteroids (Python)

A classic Asteroids arcade game built with Python and Pygame. The player pilots a triangular ship, shoots projectiles to destroy incoming asteroids, and ends when an asteroid collides with the ship.

---

## Table of Contents

- [Gameplay](#gameplay)
- [Project Structure](#project-structure)
- [File Reference](#file-reference)
- [Setup & Running](#setup--running)
- [Controls](#controls)
- [Configuration](#configuration)
- [Logging](#logging)

---

## Gameplay

- Asteroids spawn continuously from the edges of the screen and drift inward.
- Shooting a large asteroid splits it into two smaller, faster ones.
- The game ends when the player's ship collides with any asteroid.
- There is no score display — survival is the goal.

---

## Project Structure

```
asteroids_python/
├── main.py            # Entry point — game loop and collision logic
├── constants.py       # All tunable game constants
├── circleshape.py     # Abstract base class for all game objects
├── player.py          # Player ship: movement, rotation, shooting
├── shot.py            # Bullet fired by the player
├── asteroid.py        # Asteroid: movement and split behaviour
├── asteroidfield.py   # Spawner that produces asteroids from screen edges
├── logger.py          # JSONL diagnostic logger (state + events)
├── pyproject.toml     # Project metadata and dependencies (uv/pip)
└── .python-version    # Pinned Python version (3.13)
```

---

## File Reference

### [main.py](main.py)

The entry point. Initialises Pygame, wires up the four sprite groups (`updatable`, `drawable`, `asteroids`, `shots`), and runs the game loop at 60 FPS.

Each frame it:
1. Calls `updatable.update(dt)` to advance all game objects.
2. Checks asteroid–player collision → prints `"Game over!"` and exits.
3. Checks asteroid–shot collision → splits the asteroid and removes the shot.
4. Clears the screen and draws all `drawable` sprites.

---

### [constants.py](constants.py)

Central configuration for every magic number in the game. Edit this file to tune gameplay without touching logic.

| Constant | Value | Purpose |
|---|---|---|
| `SCREEN_WIDTH` | 1280 | Window width in pixels |
| `SCREEN_HEIGHT` | 720 | Window height in pixels |
| `PLAYER_RADIUS` | 20 | Collision radius of the player ship |
| `LINE_WIDTH` | 2 | Stroke width for all drawn shapes |
| `PLAYER_TURN_SPEED` | 300 | Degrees per second the ship rotates |
| `PLAYER_SPEED` | 200 | Pixels per second the ship moves |
| `ASTEROID_MIN_RADIUS` | 20 | Radius of the smallest asteroid fragment |
| `ASTEROID_KINDS` | 3 | Number of size tiers (small / medium / large) |
| `ASTEROID_SPAWN_RATE_SECONDS` | 0.8 | Seconds between each new asteroid spawn |
| `ASTEROID_MAX_RADIUS` | 60 | Largest asteroid radius (`MIN × KINDS`) |
| `SHOT_RADIUS` | 5 | Collision radius of a bullet |
| `PLAYER_SHOT_SPEED` | 500 | Pixels per second a bullet travels |
| `PLAYER_SHOOT_COOLDOWN_SECONDS` | 0.3 | Minimum seconds between shots |

---

### [circleshape.py](circleshape.py)

Abstract base class that all game objects inherit from. Extends `pygame.sprite.Sprite`.

- Stores `position` (Vector2), `velocity` (Vector2), and `radius`.
- Registers itself into `self.containers` on construction — the mechanism Pygame uses to add sprites to groups automatically.
- `collides_with(other)` — returns `True` when the distance between centres is less than the sum of both radii (circle–circle collision).
- `draw` and `update` are stubs that subclasses must override.

---

### [player.py](player.py)

The `Player` class (inherits `CircleShape`). Renders as a white triangle polygon.

**Key methods:**

| Method | Description |
|---|---|
| `triangle()` | Computes the three vertices of the ship polygon based on current `rotation` |
| `draw(screen)` | Draws the triangle outline with `pygame.draw.polygon` |
| `rotate(dt)` | Adjusts `self.rotation` by `PLAYER_TURN_SPEED × dt` |
| `move(dt)` | Advances `self.position` along the current heading at `PLAYER_SPEED` |
| `shoot()` | Spawns a `Shot` at the ship's position, fired in the forward direction; respects `shoot_cooldown` |
| `update(dt)` | Polls keyboard state each frame: A/D to rotate, W/S to move, Space to shoot |

---

### [shot.py](shot.py)

The `Shot` class (inherits `CircleShape`). A small white circle.

- `update(dt)` moves the shot along its velocity each frame.
- `draw(screen)` renders a filled circle outline.
- No special behaviour — it is simply removed from all groups (`kill()`) when it hits an asteroid.

---

### [asteroid.py](asteroid.py)

The `Asteroid` class (inherits `CircleShape`). A white circle that drifts in a straight line.

**Key method — `split()`:**

1. Removes itself from all groups (`self.kill()`).
2. If the radius is already at the minimum, the asteroid is fully destroyed (no children spawned).
3. Otherwise, two child asteroids are created at the same position with:
   - Radius reduced by `ASTEROID_MIN_RADIUS`.
   - Velocities rotated ±20–50° from the parent's velocity and scaled up by 1.2×.
4. Logs an `"asteroid_split"` event via the logger.

---

### [asteroidfield.py](asteroidfield.py)

The `AsteroidField` class manages the continuous spawning of asteroids. It is itself a `pygame.sprite.Sprite` that lives only in the `updatable` group (not drawn).

- Defines four **edge zones** (left, right, top, bottom) each with a direction vector and a position lambda that places the spawn point just off-screen.
- `update(dt)` accumulates elapsed time; once it exceeds `ASTEROID_SPAWN_RATE_SECONDS` it picks a random edge, a random speed (40–100 px/s) with up to ±30° angular jitter, and spawns a new asteroid at a random size tier.

---

### [logger.py](logger.py)

A diagnostic logger that writes structured data to two JSONL files during gameplay. It runs for the first 16 seconds of each session, sampling state approximately once per second.

**`log_state()`** — called every frame from `main.py`. Once per second it inspects the caller's local variables via `inspect.currentframe()`, finds sprite groups and individual sprites, and appends a JSON record to `game_state.jsonl` containing:
- Timestamp, elapsed seconds, frame number, screen size.
- Per-group sprite counts with position, velocity, radius, and rotation for up to 10 sprites per group.

**`log_event(event_type, **details)`** — called when notable things happen. Appends a record to `game_events.jsonl`. Currently emits:
- `"player_hit"` — when an asteroid touches the player.
- `"asteroid_shot"` — when a bullet hits an asteroid.
- `"asteroid_split"` — when a large asteroid breaks apart.

Both files are **overwritten** on each new run (not appended across sessions).

---

## Setup & Running

**Prerequisites:** Python 3.13, [uv](https://github.com/astral-sh/uv) (or pip).

```bash
# Clone and enter the directory
git clone <repo-url>
cd asteroids_python

# Install dependencies
uv sync
# or: pip install pygame==2.6.1

# Run the game
uv run python main.py
# or: python main.py
```

---

## Controls

| Key | Action |
|---|---|
| `W` | Thrust forward |
| `S` | Thrust backward |
| `A` | Rotate left |
| `D` | Rotate right |
| `Space` | Shoot |

---

## Logging

While playing, two log files are generated in the project root:

| File | Contents |
|---|---|
| `game_state.jsonl` | Periodic snapshots of all sprite positions, velocities, and radii |
| `game_events.jsonl` | Discrete events: hits, shots, and splits with timestamps |

Logging stops automatically after 16 seconds and both files are reset on each launch.
