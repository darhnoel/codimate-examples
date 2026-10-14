"""A drop falls into still water, and the ripple spreads across the grid.

    .venv/bin/python physics/ripple/main.py

The water is a grid of heights, moved one step at a time by the wave equation
(pool.py). The drop falls under gravity and lands in the middle. It lifts the
water gradually while it shrinks into it, and the ripple spreads outwards, turns
back at the walls and fades. Codimate has no 3D, so this view projects each grid
point itself and draws the lines between them.
"""

import math

import codimate as cm

import pool
from pool import DT, GRAVITY, N, point

cm.canvas(1080, 1920)  # vertical, 9:16, for TikTok and Reels

SHOW_WORDS = False  # the captions and the note; off while only the picture is wanted
DURATION = 30.0  # seconds of film
DROP_RADIUS = 0.2  # metres, drawn: bigger than life so the drop reads on screen
SHRINK = 0.3  # seconds the drop takes to shrink into the water
FALL_STEPS = math.ceil(pool.fall_time() / DT)
PUSH_STEPS = round(SHRINK / DT)  # the frames the drop takes to land and shrink
RIPPLE_STEPS = round(DURATION / DT) - FALL_STEPS - PUSH_STEPS

# The view. The camera looks down at a three-quarter angle and turns slowly.
TILT = math.radians(30)
YAW_START = math.radians(-25)
TURN = math.radians(30)  # how far the camera swings over the whole film
EYE = 3.8  # metres from the eye to the middle of the pool
LENS = 500  # pixels per metre, at the middle of the pool
MIDDLE = (540, 960)
VERT = 20  # heights are drawn this many times their true size

WATER, WATER_INK, DROP = "#3fa7bb", "#e8eef7", "#9fe3ff"


class Film:
    """Everything the film needs at one moment. `copy` is how the trace keeps a
    snapshot of it, and it has to copy the water too, or every moment would
    share one grid."""

    def __init__(self):
        self.water = pool.Pool()
        self.time = 0.0  # seconds since the drop let go
        self.landed = None  # the time it landed, or None while it is falling
        self.over = False  # set once the last moment of the ripple has happened

    def copy(self):
        twin = Film()
        twin.water = self.water.copy()
        twin.time = self.time
        twin.landed = self.landed
        twin.over = self.over
        return twin


# --- the algorithm ----------------------------------------------------------


def film(state, emit):
    for _ in range(FALL_STEPS):
        state.time += DT
        emit("fall")
    state.landed = state.time
    for k in range(PUSH_STEPS):
        state.water.land((k + 1) / PUSH_STEPS)
        state.water.step()
        state.time += DT
        emit("land")
    for _ in range(RIPPLE_STEPS):
        state.water.step()
        state.time += DT
        emit("tick")
    state.over = True
    emit("done")


# --- the view ---------------------------------------------------------------


def look(p, yaw):
    """Where a point of the water goes on screen, and how far from the eye it is."""
    x, y, z = p
    x, z = (x * math.cos(yaw) + z * math.sin(yaw),
            -x * math.sin(yaw) + z * math.cos(yaw))
    # Tilting the camera down: points further away sit higher on the screen.
    y, z = (y * math.cos(TILT) + z * math.sin(TILT),
            -y * math.sin(TILT) + z * math.cos(TILT))
    away = z + EYE
    return (MIDDLE[0] + LENS * x / away, MIDDLE[1] - LENS * y / away), away


def grid_lines():
    """Every row and column of the grid, each one line. Yields a name and the
    grid points along it."""
    for axis in (0, 1):
        for fixed in range(N):
            if axis == 0:
                cells = [(i, fixed) for i in range(N)]
            else:
                cells = [(fixed, j) for j in range(N)]
            yield (axis, fixed), cells


def caption(film):
    if film.landed is None:
        return "A drop falls"
    since = film.time - film.landed
    if since < 2.0:
        return "The ripple spreads outwards"
    if since < 8.0:
        return "It reaches the edge and turns back"
    return "The ripples fade as the water settles"


def view(frame):
    film = frame.state
    yaw = YAW_START + TURN * film.time / DURATION
    height = film.water.height
    scene = cm.Scene()
    hud = scene.overlay()

    for name, cells in grid_lines():
        pts = [look((point(i), VERT * height[i][j], point(j)), yaw)[0]
               for i, j in cells]
        scene.curve(("line",) + name, pts, w=2.0).fill(WATER).on(opacity=0.85)

    # The drop falls, then shrinks into the water where it landed.
    if film.landed is None:
        fallen = GRAVITY * (film.time**2) / 2
        drop_y = max(0.0, pool.DROP_HEIGHT - fallen)
        size, shown = DROP_RADIUS, 1.0
    else:
        drop_y = 0.0
        since = film.time - film.landed
        size = DROP_RADIUS * max(0.0, 1.0 - since / SHRINK)
        shown = 1.0 if since < SHRINK else 0.0
    at, away = look((0.0, drop_y, 0.0), yaw)
    scene.circle("drop", r=max(LENS * size / away, 0.5), at=at).fill(DROP).on(
        opacity=shown, layer=5)


    if SHOW_WORDS and not film.over:  # both go once the film has finished
        hud.text("caption", caption(film), size=34, at=(640, 60)).fill(WATER_INK)
        hud.text("note", f"heights drawn {VERT} times their true size", size=20,
                 at=(640, 700)).fill("#8d97ab")
    return scene


cm.explain(
    trace=cm.trace(film, Film(), snapshot=lambda f: f.copy()),
    view=view,
    motion=[cm.Rule("*", position="linear")],
    timing=cm.Timing(
        default=DT,
        opening=0.3,
        final_hold=1.0,
    ),
).render("results/ripple.mp4", fps=60, scale=1.0)

print("wrote results/ripple.mp4")
