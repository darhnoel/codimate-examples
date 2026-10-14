"""Hydrogen and iron in the Bohr model, one above the other.

    .venv/bin/python physics/atoms/main.py

Each atom is a nucleus of protons and neutrons with its electrons going round on
circular orbits, the inner shells faster. Hydrogen is one proton and one electron;
iron is 26 protons, 30 neutrons and 26 electrons in shells of 2, 8, 14 and 2. Every
particle is three stacked flat circles, the middle one pushed towards the light,
and the camera turns slowly. Each atom has a Khmer title. The shells are in
bohr.py. It is a simplified picture: real electrons have no orbits.
"""

import math
import random

import codimate as cm

import bohr

cm.canvas(1080, 1920)  # vertical, 9:16, for TikTok and Reels

FPS = 30
DT = 1 / FPS
DURATION = 24.0  # seconds of film
FRAMES = round(DURATION * FPS)

# Each atom in turn: when it is on screen, how much it is enlarged, and its protons,
# neutrons and shells. Hydrogen first, then iron, each in the middle of the screen.
CENTRE = (540, 960)
ATOMS = [
    ("hydrogen", (0.0, 11.0), 1.8, bohr.HYDROGEN),
    ("iron", (11.0, 24.0), 1.0, bohr.IRON),
]
FADE = 0.6  # seconds for an atom to fade in or out
TITLES = {"hydrogen": "អាតូមអុីដ្រូសែន", "iron": "អាតូមដែក"}
TEXT = "#e8eef7"
YAW_RATE = math.radians(18)  # the camera turns this much each second
TILT = math.radians(20)
DEPTH = 500.0  # pixels that count as the full depth of an atom

NUCLEON_R = 22  # pixels
ELECTRON_R = 15
NUCLEUS_R = 110  # the packed iron nucleus, in pixels, far bigger than real scale

RED, BLUE, GREY, WHITE = "#ff5d5d", "#58c4dd", "#8d97ab", "#ffffff"
LIGHT = (-0.7071, -0.7071)
# The three circles, back to front: radius and push towards the light (shares of
# the particle's radius), and how much lighter than its colour.
LAYERS = [
    (1.00, 0.00, -0.45),
    (0.70, 0.12, 0.00),
    (0.40, 0.24, 0.45),
]


def mix(a, b, t):
    ca = tuple(int(a[k : k + 2], 16) for k in (1, 3, 5))
    cb = tuple(int(b[k : k + 2], 16) for k in (1, 3, 5))
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def lighter(colour, amount):
    return (
        mix(colour, WHITE, amount) if amount >= 0 else mix(colour, "#000000", -amount)
    )


def nucleus(protons, neutrons):
    """The nucleons, packed in a ball: a kind, and a position in pixels."""
    rng = random.Random(7)
    kinds = ["proton"] * protons + ["neutron"] * neutrons
    rng.shuffle(kinds)
    if len(kinds) == 1:
        return [(kinds[0], (0.0, 0.0, 0.0))]
    golden = math.pi * (3 - math.sqrt(5))
    out = []
    for i, kind in enumerate(kinds):
        z = 1 - 2 * (i + 0.5) / len(kinds)
        ring = math.sqrt(1 - z * z)
        reach = NUCLEUS_R * ((i + 0.5) / len(kinds)) ** (1 / 3)
        out.append(
            (
                kind,
                (
                    reach * ring * math.cos(i * golden),
                    reach * z,
                    reach * ring * math.sin(i * golden),
                ),
            )
        )
    return out


NUCLEI = [nucleus(protons, neutrons) for _, _, _, (protons, neutrons, _) in ATOMS]
CLOUDS = [bohr.electrons(shells) for _, _, _, (_, _, shells) in ATOMS]


class Film:
    """Only the time: where everything is follows from it."""

    def __init__(self):
        self.time = 0.0

    def copy(self):
        twin = Film()
        twin.time = self.time
        return twin


def film(state, emit):
    for _ in range(FRAMES):
        state.time += DT
        emit("tick")


def fade(t, window):
    start, end = window
    return max(0.0, min(1.0, (t - start) / FADE, (end - t) / FADE))


def turn(p, scale, yaw):
    """A point seen from the camera: screen position and depth (bigger is farther)."""
    x, y, z = (c * scale for c in p)
    x, z = x * math.cos(yaw) + z * math.sin(yaw), -x * math.sin(yaw) + z * math.cos(yaw)
    y, z = (
        y * math.cos(TILT) + z * math.sin(TILT),
        -y * math.sin(TILT) + z * math.cos(TILT),
    )
    return (CENTRE[0] + x, CENTRE[1] - y), z


def particle(scene, key, at, radius, paint):
    """Three stacked flat circles, and a sign in the middle of the inner one.
    `paint` is the colour, the sign (or ""), the first layer to use and the opacity."""
    colour, sign, base, opacity = paint
    inner = at
    for k, (share, push, tone) in enumerate(LAYERS):
        centre = (at[0] + LIGHT[0] * push * radius, at[1] + LIGHT[1] * push * radius)
        if k == 2:
            inner = centre
        scene.circle((key, k), r=share * radius, at=centre).fill(
            lighter(colour, tone)
        ).on(layer=base + k, opacity=opacity)
    if sign:
        scene.formula((key, "sign"), sign, size=radius * 1.1, at=inner).fill(
            lighter(colour, -0.65)
        ).on(layer=base + 3, opacity=opacity)


def draw_atom(scene, index, t, yaw):
    name, window, scale, _ = ATOMS[index]
    opacity = fade(t, window)
    if opacity <= 0.0:
        return
    title = TITLES[name]
    scene.overlay().text((name, "title"), title, size=96, at=(540, 200)).fill(TEXT).on(
        opacity=opacity
    )
    drawn = []  # (depth, key, screen, radius, paint)
    for i, (kind, p) in enumerate(NUCLEI[index]):
        wobble = 2.0 * math.sin(2 * math.pi * t / 1.7 + i)
        at, depth = turn((p[0] + wobble, p[1], p[2]), scale, yaw)
        colour, sign = (RED, "+") if kind == "proton" else (GREY, "")
        drawn.append(
            (depth, (name, "nucleon", i), at, NUCLEON_R * scale, (colour, sign))
        )
    for k, electron in enumerate(CLOUDS[index]):
        at, depth = turn(electron.position(t), scale, yaw)
        drawn.append(
            (depth, (name, "electron", k), at, ELECTRON_R * scale, (BLUE, "-"))
        )
        # The orbit itself, faint, as a line (open, so it is not filled).
        orbit = [
            turn(electron.at_angle(2 * math.pi * j / 64), scale, yaw)[0]
            for j in range(65)
        ]
        scene.curve((name, "orbit", k), orbit, w=1.5).fill(BLUE).on(
            opacity=0.2 * opacity, layer=index * 20000 + 5
        )
    drawn.sort(key=lambda item: -item[0])
    for rank, (depth, key, at, radius, (colour, sign)) in enumerate(drawn):
        near = 1 - 0.12 * depth / DEPTH  # a little bigger when nearer
        base = index * 20000 + 20 + rank * 5
        particle(scene, key, at, radius * near, (colour, sign, base, opacity))


def view(frame):
    t = frame.state.time
    yaw = YAW_RATE * t
    scene = cm.Scene()
    for index in range(len(ATOMS)):
        draw_atom(scene, index, t, yaw)
    return scene


cm.explain(
    trace=cm.trace(film, Film(), snapshot=lambda f: f.copy()),
    view=view,
    motion=[cm.Rule("*", position="linear")],
    timing=cm.Timing(default=DT, opening=0.3, final_hold=1.0),
).render("results/atoms.mp4", fps=FPS, scale=1.0)

print("wrote results/atoms.mp4")
