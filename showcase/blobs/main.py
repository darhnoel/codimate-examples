"""A cluster of shaded balls, turning: 3D on a 2D engine, two ways.

    .venv/bin/python showcase/blobs/main.py          # stacked circles
    .venv/bin/python showcase/blobs/main.py mesh     # the science kit's meshes

Forty off-white balls, the way a microscope's software shows segmented cell
nuclei, with the camera walking once round them. A `science.Camera` places them
either way. The light rides with the camera, up and to the left of the viewer,
so the shading stays put while the cluster turns, as it would on a turntable.

**Stacked circles** (the default) draw each ball as 32 circles, shrinking and
brightening toward the light. Because the light never moves on screen, every
ball is shaded the same way in every frame; only its place, size and order
change. About 1,300 shapes a frame, smooth, and fast.

**Meshes** (`mesh`) are `science.World` and `science.Sphere`: every ball a mesh
of faces, each shaded by a `science.Light`, all painted far to near. True shading
from any light, at about 6,300 shapes a frame.
"""

import math
import sys
from dataclasses import dataclass

import codimate as cm
from cluster import cluster
from codimate import science

cm.canvas(1080, 1920)  # vertical, 9:16, for TikTok and Reels

FPS, SECONDS = 60, 12.0  # one turn
BALLS = cluster(40)
IVORY, SHADE = "#ece6da", "#1c1a17"
ELEVATION, DISTANCE, SCALE = 12.0, 2600.0, 1.6
STYLE = sys.argv[1] if len(sys.argv) > 1 else "circles"
if STYLE not in ("circles", "mesh"):
    raise SystemExit("pick circles or mesh")

COUNT = 32  # circles in one ball: more is smoother, and each one is another shape


def rings(count):
    """One ball as stacked circles, outermost first: how big each is (of the
    ball's radius), how far its middle moves toward the light (of the radius),
    and how lit it is (0 shadow, 1 ivory). Brightness rises fast at first and
    levels off, as on a lit ball; the last, a small highlight, is a touch past
    ivory."""
    out = []
    for n in range(count):
        t = n / (count - 1)
        lit = 0.30 + 0.70 * (1 - (1 - t) ** 2)
        out.append((1.0 - 0.87 * t, 0.38 * t, lit if n < count - 1 else 1.10))
    return out


RINGS = rings(COUNT)
TO_LIGHT = (-0.6, -0.8)  # up and to the left on screen


@dataclass
class Orbit:
    azimuth: float = 0.0  # degrees: where the camera stands round the cluster


def walk(orbit, emit):
    # One moment per video frame: the World sorts faces once per moment, so
    # fewer would make the order jump (see `science.World`).
    frames = round(FPS * SECONDS)
    for frame in range(1, frames + 1):
        orbit.azimuth = 360 * frame / frames
        emit("turn")


def light_for(camera):
    """A light up and to the left of the viewer, wherever the camera stands."""
    az, el = math.radians(camera.azimuth), math.radians(camera.elevation)
    toward = (math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))
    right = (-math.sin(az), math.cos(az), 0.0)
    way = tuple(
        0.7 * t - 0.5 * r + 0.6 * u for t, r, u in zip(toward, right, (0, 0, 1))
    )
    return science.Light(direction=way, ambient=0.22, shadow=SHADE)


def camera_for(state):
    return science.Camera(
        azimuth=state.azimuth,
        elevation=ELEVATION,
        distance=DISTANCE,
        scale=SCALE,
        centre=(540, 960),
    )


def mix(a, b, part):
    """The colour `part` of the way from `a` to `b`; past 1 runs on toward white."""
    rgb = []
    for i in (1, 3, 5):
        x, y = int(a[i : i + 2], 16), int(b[i : i + 2], 16)
        value = x + (y - x) * part if part <= 1 else y + (255 - y) * (part - 1) * 2
        rgb.append(round(min(255, max(0, value))))
    return "#%02x%02x%02x" % tuple(rgb)


SHADES = [mix(SHADE, IVORY, lit) for _, _, lit in RINGS]


def circles(frame):
    """Each ball as stacked circles; the balls painted far to near."""
    camera = camera_for(frame.state)
    seen = []
    for k, (centre, r) in enumerate(BALLS):
        (x, y), depth = camera.project(centre)
        seen.append((depth, k, x, y, r * camera.focal / depth))
    seen.sort(reverse=True)  # far first
    scene = cm.Scene()
    for rank, (_, k, x, y, radius) in enumerate(seen):
        for n, ((size, shift, _), colour) in enumerate(zip(RINGS, SHADES)):
            at = (x + TO_LIGHT[0] * shift * radius, y + TO_LIGHT[1] * shift * radius)
            scene.circle(("ball", k, n), r=size * radius, at=at).fill(colour).on(
                layer=rank * len(RINGS) + n
            )
    return scene


def meshes(frame):
    """Each ball a shaded mesh: `science.World` does the shading and the order."""
    camera = camera_for(frame.state)
    scene = cm.Scene()
    balls = {
        ("ball", k): science.Sphere(centre, r, IVORY, detail=2)
        for k, (centre, r) in enumerate(BALLS)
    }
    science.World(camera, light=light_for(camera)).draw(scene, balls)
    return scene


OUT = "results/blobs.mp4" if STYLE == "circles" else "results/blobs_mesh.mp4"

cm.explain(
    trace=cm.trace(walk, Orbit()),
    view=circles if STYLE == "circles" else meshes,
    timing=cm.Timing(default=1 / FPS, opening=0.0, final_hold=0.0),
).render(OUT, fps=FPS, scale=1.0)

print(f"wrote {OUT}")
