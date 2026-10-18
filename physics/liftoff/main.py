"""Lift-off: a car driving down a night road takes off on four jets, hovers, lands
and drives on.

    .venv/bin/python physics/liftoff/main.py

A car drives down a lit road at 40 km/h, the camera tracking it low at its
front corner. Its thrusters fire while it rolls; it rises off the road as it
slows, its wheels still spinning, and smoke smears along the road behind. It
hovers, creeping forward, while the camera swings once round it. Then it comes
down onto the road, its thrusters spool down, it rests a moment and drives on
into the dark through its own smoke while the camera holds and watches.

Everything is in 3D. The car (`car.py`) is drawn panel by panel, its jets
painted pictures (`jets.py`) laid along each thruster. The smoke (`smoke.py`)
is a crowd of puffs in space, born where the jets hit the road and carried by
swirling air, rendered as a lit volume, with the road and its light under it.
Codimate cannot compute pixels, so smoke and road are painted as two images
each frame, what is behind the car and what is in front of it, and the car
and the street lamps are drawn between them.

The paintings go to results/liftoff/, kept under a fingerprint of the
simulation: they are painted again only when it or the settings here change.
"""

import hashlib
import math
import multiprocessing
import os
import shutil
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import car
import codimate as cm
import jets
import numpy as np
import smoke
from codimate import science

cm.canvas(1080, 1920)  # vertical, 9:16, for TikTok and Reels

FPS, SECONDS = 60, 25.0
CRUISE = 11.0  # m/s, about 40 km/h
CREEP = 1.0  # m/s, its slow drift forward while it hovers
HOVER = 3.0  # metres it climbs
START = -5.0 * CRUISE  # where it starts on the road, so it lifts off near x = 0
FOLDER = Path("results/liftoff")
CAMERA = {"distance": 20, "scale": 190}
GROUND = (540, 1850)  # where the ground under the car's middle shows
FLAMES = 8  # painted jets to flicker between
# Street lamps along the right of the road: the pole's foot, and its head over
# the road's edge.
LAMP_HEIGHT, LAMP_SIDE, LAMP_REACH = 7.0, -5.6, 1.6
LAMPS = [(x, LAMP_SIDE) for x in range(-100, 160, 22)]
HEADS = [(x, y + LAMP_REACH, LAMP_HEIGHT - 0.1) for x, y in LAMPS]


@dataclass
class Pose:
    x: float  # how far along the road, metres
    lift: float  # metres off the road, above its springs' rest
    pitch: float  # radians, nose up
    roll: float  # radians, right side up
    spin: float  # how far the wheels have turned, radians
    deploy: float  # how far the thrusters are out of the belly, 0 to 1
    throttle: float  # 0 to 1
    thrust: tuple  # each jet's strength, 0 to 1: the throttle, flickering
    flame: tuple  # which of the painted jets each one shows, so it flickers
    shake: tuple  # the camera's jolt, in pixels


def _wobble(t, *waves):
    """A smooth wander: a sum of slow sines, `waves` as (amplitude, period, phase)."""
    return sum(a * math.sin(2 * math.pi * t / p + f) for a, p, f in waves)


def _ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def _speed(t):
    """How fast the car goes along the road at `t` seconds: cruising; slowing
    to a creep as it lifts off; creeping while it hovers; stopping as it lands;
    resting; then pulling away."""
    if t < 5.0:
        return CRUISE
    if t < 9.5:
        return CRUISE + (CREEP - CRUISE) * _ease((t - 5.0) / 4.5)
    if t < 16.0:
        return CREEP
    if t < 22.3:
        return CREEP * (1 - _ease((t - 16.0) / 3.0))
    return min(12.0, 2.6 * (t - 22.3))


def _height(t):
    """How high the pilot wants it: on the road; up to HOVER from 5.5 s,
    bobbing; down from 16 s, aiming a little below the road so it settles
    onto its springs rather than hovering just above them."""
    down = _ease((t - 16.0) / 3.0)
    up = _ease((t - 5.5) / 3.5) * (1 - down)
    bob = _wobble(t, (0.07, 2.7, 0.0), (0.03, 1.3, 1.0))
    bob *= _ease((t - 9.0) / 2.0) * (1 - _ease((t - 15.0) / 1.5))
    return HOVER * up + bob - 0.25 * down


def motion(count):
    """The car's pose at each frame. Along the road it goes at `_speed`; up
    and down it follows `_height` as a damped spring would, so it lags and
    eases, and settles onto its springs when it lands. Its wheels turn with
    the road, spin down in the air and turn again when it drives off. On its
    wheels it squats as it pulls away; in the air it dips its nose as it
    speeds up and lifts it as it slows."""
    dt = 1 / FPS
    x, z, vz, az = START, 0.0, 0.0, 0.0
    spin, turning = 0.0, 0.0  # the wheels: angle, and radians per second
    landed = None  # when it touched down
    flicker = np.random.default_rng(9)
    poses = []
    before = _speed(0.0)
    for k in range(count):
        t = k * dt
        # The thrusters fire at 4.6 s, while it rolls, and spool down only once
        # it is down.
        spool = _ease((t - 4.6) / 1.2)
        if landed is not None:
            spool *= 1 - _ease((t - landed - 0.5) / 1.0)
        # The thrusters slide out of the belly in the second before they fire,
        # and back in once they have spooled down after the landing.
        deploy = _ease((t - 3.4) / 1.1)
        if landed is not None:
            deploy *= 1 - _ease((t - landed - 1.6) / 0.8)
        speed = _speed(t)
        forward = (speed - before) / dt  # m/s²
        before = speed
        x += speed * dt
        wish = _height(t) + 0.06 * spool  # springs extend while thrust holds it
        calm = 0.55 + 0.4 * _ease((t - 15.0) / 1.0)  # damping: firmer to land
        for _ in range(4):  # small steps keep the springs stable
            az = 2.2**2 * (wish - z) - 2 * calm * 2.2 * vz
            if z < 0:  # on its springs: stiff and well damped
                az += 400 * -z - 40 * vz
                if landed is None and t > 12:
                    landed = t
            vz += az * dt / 4
            z += vz * dt / 4
        aloft = min(1.0, max(0.0, z / 0.3))
        rolling = speed / car.WHEEL_R
        turning = rolling if aloft < 0.5 else turning * math.exp(-dt / 1.2)
        spin += turning * dt
        climbing = max(-1.0, min(1.0, az))
        # A craft on jets is never quite still: a buzz while the thrust only
        # just holds it, slow wobbles as it corrects. A car on a road hums.
        buzz = spool * (1 - _ease((t - 6.0) / 1.5))
        drift = spool * _wobble(t, (0.012, 1.9, 0.3), (0.006, 0.7, 2.0))
        squat = 0.012 * forward * (1 - aloft) - 0.03 * forward * aloft
        pitch = squat + 0.03 * climbing + drift
        pitch += 0.006 * buzz * math.sin(2 * math.pi * 11 * t + 1)
        roll = spool * _wobble(t, (0.015, 2.3, 1.7), (0.006, 0.9, 0.4))
        roll += 0.006 * buzz * math.sin(2 * math.pi * 9 * t)
        road = (1 - aloft) * speed / CRUISE
        jitter = 0.004 * buzz * math.sin(2 * math.pi * 13 * t)
        jitter += 0.004 * road * math.sin(2 * math.pi * 7 * t)
        thrust = 0.8 + 0.2 * climbing + 0.05 * abs(forward)
        throttle = spool * min(1.0, thrust + 0.03 * math.sin(37 * t))
        bump = 4.0 * math.exp(-(t - landed) / 0.25) if landed is not None else 0.0
        jolt = 3.0 * buzz + 1.0 * spool + bump + 0.8 * road
        shake = (jolt * math.sin(53 * t), jolt * math.sin(41 * t + 1))
        thrust = tuple(throttle * flicker.uniform(0.9, 1.04) for _ in range(4))
        flame = tuple(int(f) for f in flicker.integers(0, FLAMES, 4))
        poses.append(
            Pose(
                x, z + jitter, pitch, roll, spin, deploy, throttle, thrust, flame, shake
            )
        )
    return poses


POSES = motion(round(FPS * SECONDS))


def _at(pose):
    return car.pose(pose.lift, pose.pitch, pose.roll, (pose.x, 0.0))


def camera(k, shake=(0.0, 0.0)):
    """The camera at frame `k`. It tracks the car low at its front corner
    while it drives and lifts off; swings once round it while it hovers; turns
    on round to nearly behind it as it lands; and then holds still and
    watches it drive away down the road. As the car climbs the camera lowers
    its eye, widens a little and looks up at a point that rises with it."""
    t = k / FPS
    pose = POSES[k] if t < 21.0 else POSES[round(21.0 * FPS)]
    follow = max(0.0, pose.lift) / HOVER
    azimuth = 35 + 360 * _ease((t - 9.0) / 7.0) + 160 * _ease((t - 16.0) / 5.0)
    under = (pose.x, 0.0, 0.0)
    look = {
        **CAMERA,
        "scale": CAMERA["scale"] * (1 - 0.2 * min(follow, 1.0)),
        "azimuth": azimuth,
        "elevation": 6 - 8 * follow,
        "target": (under[0], 0.0, 2.0 * follow),
    }
    gx, gy = science.Camera(**look, centre=(0, 0)).at(under)
    ground = (GROUND[0], GROUND[1] - 90 * follow)
    return science.Camera(
        **look, centre=(ground[0] - gx + shake[0], ground[1] - gy + shake[1])
    )


def _stage(pose):
    """What the road needs to be painted: the lamps, where the car is, and
    where its jets land."""
    lines = car.jet_lines(_at(pose))
    pools = [(foot, s) for (_, foot), s in zip(lines, pose.thrust)]
    return {"lamps": HEADS, "car": (pose.x, 0.0, pose.lift), "pools": pools}


def _forget(found, keep):
    """Delete paintings a change of settings has left behind: they are only a
    cache, and each is hundreds of megabytes of frames no setting reaches."""
    keep = {Path(k) for k in (keep if isinstance(keep, list) else [keep])}
    for path in found:
        if path not in keep:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


def paint(count):
    """Simulate the smoke and paint it, frame by frame, as two RGBA pictures:
    behind the car's middle and in front of it. Reuse earlier paintings."""
    recipe = (
        Path(smoke.__file__).read_bytes()
        + Path(car.__file__).read_bytes()
        + repr((count, CAMERA, GROUND, LAMPS, [vars(p) for p in POSES])).encode()
    )
    folder = FOLDER / hashlib.sha1(recipe).hexdigest()[:12]
    _forget(FOLDER.glob("[0-9a-f]" * 12), keep=folder)
    paths = [
        tuple(str(folder / f"{k:04d}-{layer}.png") for layer in ("back", "front"))
        for k in range(count)
    ]
    if all(Path(p).exists() for pair in paths for p in pair):
        return paths
    folder.mkdir(parents=True, exist_ok=True)
    # The smoke moves on frame by frame, in order; each frame is then painted
    # on its own, side by side. Forked, so the workers do not run this script.
    cloud = smoke.Smoke()
    jobs = []
    for k, (pose, pair) in enumerate(zip(POSES, paths)):
        at = _at(pose)
        lines = car.jet_lines(at)
        cloud.step(lines, pose.thrust, 1 / FPS)
        cam = camera(k)
        split = cam.project(at((0.0, 0.0, 0.0)))[1]
        job = (cloud.snapshot(), lines, pose.thrust, cam, split, _stage(pose), pair)
        jobs.append(job)
    context = multiprocessing.get_context("fork")
    with ProcessPoolExecutor(max(1, os.cpu_count() - 2), mp_context=context) as pool:
        list(pool.map(smoke.paint, jobs, chunksize=4))
    return paths


PATHS = paint(len(POSES))


def paint_flames():
    """The painted jets, once each, kept beside the smoke."""
    tag = hashlib.sha1(Path(jets.__file__).read_bytes()).hexdigest()[:12]
    FOLDER.mkdir(parents=True, exist_ok=True)
    paths = [FOLDER / f"jet-{tag}-{k}.png" for k in range(FLAMES)]
    _forget(FOLDER.glob("jet-*.png"), keep=paths)
    for k, path in enumerate(paths):
        if not path.exists():
            jets.paint_jet(path, seed=k)
    return [str(path) for path in paths]


FLAME_PATHS = paint_flames()
GLOW = (
    FOLDER
    / f"glow-{hashlib.sha1(Path(jets.__file__).read_bytes()).hexdigest()[:12]}.png"
)
_forget(FOLDER.glob("glow-*.png"), keep=GLOW)
if not GLOW.exists():
    jets.paint_glow(GLOW)


@dataclass
class Clock:
    frame: int = 0


def run(clock, emit):
    for k in range(1, len(PATHS)):
        clock.frame = k
        emit("tick")


def draw_lamps(scene, cam, split, near, layer):
    """The street lamps further than `split` (a depth), or nearer if `near`:
    a pole, an arm over the road and a glowing head each. Returns the next
    free layer."""
    for n, (x, y) in enumerate(LAMPS):
        (fx, fy), depth = cam.project((x, y, 0.0))
        if depth < 2.0 or (depth < split) != near or not -400 < fx < 1480:
            continue
        metre = cam.focal / depth
        top, end = cam.at((x, y, LAMP_HEIGHT)), cam.at(HEADS[n])
        pole = max(1.0, 0.16 * metre)
        scene.line(("lamp", n, "pole"), start=(fx, fy), end=top, w=pole).fill(
            "#2c2f36"
        ).on(layer=layer)
        scene.line(("lamp", n, "arm"), start=top, end=end, w=pole * 0.7).fill(
            "#2c2f36"
        ).on(layer=layer)
        glow = 3.0 * metre
        scene.image(("lamp", n, "glow"), str(GLOW), size=(glow, glow), at=end).on(
            layer=layer + 1
        )
        scene.circle(("lamp", n, "head"), r=max(1.5, 0.14 * metre), at=end).fill(
            "#fff4e0"
        ).on(layer=layer + 2)
    return layer + 3


def view(frame):
    k = frame.state.frame
    pose = POSES[k]
    cam = camera(k, pose.shake)
    scene = cm.Scene()
    back, front = PATHS[k]
    at = (540 + pose.shake[0], 960 + pose.shake[1])  # painted unshaken
    scene.image("smoke behind", back, size=(1080, 1920), at=at).on(layer=0)
    split = cam.project(_at(pose)((0.0, 0.0, 0.0)))[1]
    top = draw_lamps(scene, cam, split, near=False, layer=1)
    flames = [FLAME_PATHS[f] for f in pose.flame]
    look = car.Look(_at(pose), list(zip(pose.thrust, flames)), pose.spin, pose.deploy)
    top = car.draw(scene, cam, look, layer=max(top, 10))
    top = draw_lamps(scene, cam, split, near=True, layer=top)
    scene.image("smoke in front", front, size=(1080, 1920), at=at).on(layer=top)
    return scene


cm.explain(
    trace=cm.trace(run, Clock()),
    view=view,
    timing=cm.Timing(default=1 / FPS, opening=0.0, final_hold=0.0),
).render("results/liftoff.mp4", fps=FPS, scale=1.0)

print("wrote results/liftoff.mp4")
