"""Why a planet's orbit is an ellipse: the pull and the speed, together.

    .venv/bin/python physics/ellipse/main.py

A star pulls a planet towards itself, and the planet's speed carries it sideways.
Put together, they bend its path into an ellipse, with the star at one focus.
The red arrow is the pull, always towards the star; the yellow arrow is the
speed, always along the path. The physics is in orbit.py.
"""

import math

import codimate as cm

import orbit

cm.canvas(1080, 1920)  # vertical, 9:16, for TikTok and Reels

FPS = 60
DT = 1 / FPS
DURATION = 40.0  # seconds of film
FRAMES = round(DURATION * FPS)
SECONDS_PER_ORBIT = 10.0  # four orbits in the film, each one quicker to watch
SUBSTEPS = 40  # physics steps per frame, so the curve stays smooth

SCALE = 220  # pixels per unit of distance
STAR = (760, 960)  # screen position of the star, one focus of the ellipse
TRAIL, PLANET, STAR_COLOUR = "#58c4dd", "#f2f4f8", "#ffd166"
PULL, SPEED, TEXT, DIM = "#ff5d5d", "#ffd166", "#e8eef7", "#8d97ab"

# Each caption is shown for its own stretch of the film, fading in and out.
CAPTIONS = [
    (0.0, 5.0, "The star pulls it towards itself"),
    (5.0, 10.0, "Its speed v carries it sideways"),
    (10.0, 18.0, "1. The pull F grows as r shrinks"),
    (18.0, 26.0, "2. Equal areas in equal times"),
    (26.0, 34.0, "3. Let u = 1/r and substitute"),
    (34.0, 40.0, "So the path is an ellipse"),
]
# The equation shown for each part of the film, in the same place under the orbit.
EQUATIONS = [
    (10.0, 18.0, r"F = \frac{G M m}{r^{2}}"),
    (18.0, 26.0, r"h = r^{2}\dot{\theta}"),
    (26.0, 34.0, r"\frac{d^{2}u}{d\theta^{2}} + u = \frac{G M}{h^{2}}"),
    (34.0, 40.0, r"r = \frac{a(1-e^{2})}{1+e\cos\theta}"),
]
FADE = 0.5  # seconds for a caption to fade in or out
WRITE_SECONDS = 1.5  # how long an equation takes to write on, like Manim's Write
FADE_OUT = 0.4  # how long it takes to go before the next one


class Film:
    """What the film needs at one moment. `copy` is how the trace keeps a snapshot
    of it; the trail is copied too, so each moment keeps its own path."""

    def __init__(self):
        self.planet = orbit.Planet()
        self.time = 0.0
        self.trail = []  # the planet's past positions, in physics units

    def copy(self):
        twin = Film()
        twin.planet = self.planet.copy()
        twin.time = self.time
        twin.trail = list(self.trail)
        return twin


# --- the algorithm ----------------------------------------------------------


def film(state, emit):
    physics_per_frame = orbit.PERIOD / (SECONDS_PER_ORBIT * FPS)
    for _ in range(FRAMES):
        for _ in range(SUBSTEPS):
            state.planet.step(physics_per_frame / SUBSTEPS)
        state.time += DT
        state.trail.append((state.planet.x, state.planet.y))
        emit("tick")


# --- the view ---------------------------------------------------------------


def to_screen(x, y):
    return (STAR[0] + SCALE * x, STAR[1] - SCALE * y)


def fit(text, size, room=1080 - 80):
    """The largest size at or below `size` that keeps `text` inside the frame."""
    while size > 20 and cm.measure(text, size=size)[0] > room:
        size -= 1
    return size


def fade(t, start, end):
    """How visible something is between `start` and `end` seconds: it fades in
    over FADE seconds, and out again before the end."""
    return max(0.0, min(1.0, (t - start) / FADE, (end - t) / FADE))


def arrowhead(start, tip):
    """A triangle at `tip`, pointing from `start` towards it, in screen pixels."""
    dx, dy = tip[0] - start[0], tip[1] - start[1]
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    head, half = 26, 11
    base = (tip[0] - ux * head, tip[1] - uy * head)
    side = (-uy * half, ux * half)
    return [
        tip,
        (base[0] + side[0], base[1] + side[1]),
        (base[0] - side[0], base[1] - side[1]),
    ]


def arrow(scene, key, start, vector, paint):
    """An arrow from `start` along `vector`, in screen pixels. `paint` is its
    colour and how visible it is."""
    colour, opacity = paint
    tip = (start[0] + vector[0], start[1] + vector[1])
    scene.line((key, "shaft"), start=start, end=tip, w=8).fill(colour).on(
        opacity=opacity, layer=5
    )
    scene.polygon((key, "head"), arrowhead(start, tip)).fill(colour).on(
        opacity=opacity, layer=6
    )


def view(frame):
    st = frame.state
    t = st.time
    planet = st.planet
    scene = cm.Scene()
    hud = scene.overlay()

    for start, end, text in CAPTIONS:
        size = fit(text, 44)
        hud.text(("caption", start), text, size=size, at=(540, 200)).fill(TEXT).on(
            opacity=fade(t, start, end)
        )

    # Each equation writes on from the left, as Manim's Write does, stays while its
    # step is shown, and fades out before the next one arrives.
    for index, (start, end, latex) in enumerate(EQUATIONS):
        reveal = max(0.0, min(1.0, (t - start) / WRITE_SECONDS))
        visible = (1.0 if t >= start else 0.0) * max(
            0.0, min(1.0, (end - t) / FADE_OUT)
        )
        hud.formula(("equation", index), latex, size=64, at=(540, 1480)).fill(
            TEXT
        ).write(reveal=reveal).on(opacity=visible)

    # The path the planet has taken so far.
    if len(st.trail) >= 2:
        path = [to_screen(x, y) for x, y in st.trail]
        scene.curve("trail", path, w=4).fill(TRAIL).on(opacity=0.9, layer=1)

    star = to_screen(0.0, 0.0)
    scene.circle("star", r=44, at=star).fill(STAR_COLOUR).on(layer=2)
    scene.text("star/label", "star", size=36, at=(star[0], star[1] + 90)).fill(DIM)

    at = to_screen(planet.x, planet.y)
    scene.circle("planet", r=22, at=at).fill(PLANET).on(layer=4)

    # The pull: always towards the star, longer the nearer the planet is.
    r = planet.distance()
    pull_length = 60 + 180 * (1 / r**2) / (1 / orbit.R_START**2)
    toward = (-planet.x / r, planet.y / r)  # towards the star, in screen pixels
    pull_vector = (toward[0] * pull_length, toward[1] * pull_length)
    arrow(scene, "pull", at, pull_vector, (PULL, 1.0))
    pull_tip = (at[0] + pull_vector[0], at[1] + pull_vector[1])

    # The speed: always along the path, longer the faster the planet is.
    v = planet.speed()
    speed_length = 60 + 180 * v / orbit.SPEED_START
    along = (planet.vx / v, -planet.vy / v)
    speed_vector = (along[0] * speed_length, along[1] * speed_length)
    arrow(scene, "speed", at, speed_vector, (SPEED, fade(t, 5.0, 1e9)))
    speed_tip = (at[0] + speed_vector[0], at[1] + speed_vector[1])

    # Labels on the objects, so each letter in an equation points at something.
    radius_on = max(0.0, min(1.0, (t - 10.0) / FADE))
    mid = ((star[0] + at[0]) / 2, (star[1] + at[1]) / 2)
    scene.line("radius", start=star, end=at, w=3).fill(DIM).on(
        opacity=radius_on, layer=3
    )
    scene.text("label/r", "r", size=40, at=(mid[0] + 22, mid[1] - 18)).fill(TEXT).on(
        opacity=radius_on, layer=7
    )
    scene.text("label/F", "F", size=40, at=(pull_tip[0] + 22, pull_tip[1])).fill(
        PULL
    ).on(opacity=radius_on, layer=7)
    scene.text("label/v", "v", size=40, at=(speed_tip[0] + 22, speed_tip[1])).fill(
        SPEED
    ).on(opacity=max(0.0, min(1.0, (t - 5.0) / FADE)), layer=7)
    scene.text("label/u", "u = 1/r", size=40, at=(at[0] - 120, at[1] + 60)).fill(
        TEXT
    ).on(opacity=fade(t, 26.0, 34.0), layer=7)

    return scene


cm.explain(
    trace=cm.trace(film, Film(), snapshot=lambda f: f.copy()),
    view=view,
    motion=[cm.Rule("*", position="linear")],
    timing=cm.Timing(default=DT, opening=0.5, final_hold=1.0),
).render("results/ellipse.mp4", fps=FPS, scale=1.0)

print("wrote results/ellipse.mp4")
