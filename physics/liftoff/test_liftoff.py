"""`car.py`, `jets.py` and `smoke.py`, and the lift-off's motion: the car
climbs smoothly to its hover without a jump, the smoke is born at the jets and
spreads, the air it rides cannot be squeezed, and it paints behind and in front
of the car. Nothing renders here.
"""

import math

import car
import jets
import numpy as np
import smoke
from codimate import science


def poses():
    from pathlib import Path

    src = Path(__file__).with_name("main.py").read_text().split("PATHS = paint(")[0]
    ns = {}
    exec(src, ns)  # the motion and camera, without painting or rendering
    return ns


def test_the_car_drives_takes_off_rolling_lands_and_drives_on():
    ns = poses()
    poses_, fps = ns["POSES"], ns["FPS"]
    lifts = np.array([p.lift for p in poses_])
    xs = np.array([p.x for p in poses_])
    speed = np.diff(xs) * fps
    assert abs(speed[fps] - ns["CRUISE"]) < 0.1, "it starts out driving"
    up = next(k for k in range(len(lifts)) if lifts[k] > 0.3)
    assert speed[up] > 3.0, "it leaves the road while still rolling"
    assert max(lifts) < ns["HOVER"] * 1.08 and np.abs(np.diff(lifts, 2)).max() < 0.02
    # Down again at a walking pace, under power, and the jets off before it goes.
    touch = next(k for k in range(up + 2 * fps, len(lifts)) if lifts[k] < 0)
    assert -(lifts[touch] - lifts[touch - 1]) * fps < 0.5, "a soft touchdown"
    assert poses_[touch].throttle > 0.5, "still under power when it touches"
    pulls = next(k for k in range(touch, len(speed)) if speed[k] > 0.5)
    assert poses_[pulls].throttle < 0.05, "thrusters off before it drives on"
    assert speed[-1] > 5.0 and abs(lifts[-1]) < 0.02, "and it drives away"
    # The thrusters are stowed while it drives, out before they fire, and
    # stowed again before it drives off.
    fires = next(k for k, p in enumerate(poses_) if p.throttle > 0)
    assert poses_[fps].deploy == 0 and poses_[fires].deploy > 0.95
    assert poses_[pulls].deploy < 0.02


def test_wheels_turn_with_the_road_and_spin_down_in_the_air():
    ns = poses()
    poses_ = ns["POSES"]
    fps = ns["FPS"]
    turn = np.diff([p.spin for p in poses_]) * fps
    assert abs(turn[fps] - ns["CRUISE"] / car.WHEEL_R) < 0.5, "rolling, not sliding"
    assert turn[13 * fps] < 0.5, "still in the air, 13 s in"


def test_smoke_is_born_at_the_jets_and_spreads_and_rises():
    cloud = smoke.Smoke(seed=1)
    lines = car.jet_lines(car.pose(2.0))
    for _ in range(60):
        cloud.step(lines, [1.0] * 4, 1 / 30)
    assert len(cloud.age) > 1000
    feet = np.array([foot for _, foot in lines])
    reach = np.linalg.norm(cloud.pos[:, :2] - feet[:, :2].mean(0), axis=1)
    assert reach.max() > 3.0, "flung out along the ground"
    assert cloud.pos[:, 2].min() >= 0.05, "never through the ground"
    assert np.median(cloud.pos[:, 2]) > 0.3, "and rising"


def test_the_air_cannot_be_squeezed():
    cloud = smoke.Smoke(seed=2)
    p, e = np.array([[0.3, -0.7, 1.1]]), 1e-4
    div = sum(
        (cloud.air(p + e * np.eye(3)[i]) - cloud.air(p - e * np.eye(3)[i]))[0, i]
        / (2 * e)
        for i in range(3)
    )
    assert abs(div) < 1e-6


def test_smoke_renders_behind_and_in_front():
    cloud = smoke.Smoke(seed=3)
    lines = car.jet_lines(car.pose(2.0))
    for _ in range(30):
        cloud.step(lines, [1.0] * 4, 1 / 30)
    cam = science.Camera(azimuth=32, elevation=6, distance=20, scale=190)
    split = cam.project((0.0, 0.0, 2.5))[1]
    grids = smoke.volume(cloud.snapshot(), lines, [1.0] * 4, lamps=[(0, -4, 7)])
    pools = [(foot, 1.0) for _, foot in lines]
    stage = {"lamps": [(0, -4, 7)], "car": (0.0, 0.0, 2.0), "pools": pools}
    back, front = smoke.render(grids, cam, split, stage, size=(216, 384))
    w, h = 216 // smoke.SHRINK, 384 // smoke.SHRINK
    assert back.shape == front.shape == (h, w, 4)
    assert back[..., 3].max() > 0.3 and front[..., 3].max() > 0.3
    assert 0 <= back.min() and back.max() <= 1


def test_the_road_has_lines_and_lamplight():
    stage = {"lamps": [(0.0, -4.0, 7.0)], "car": (-50.0, 0.0, 0.0), "pools": []}
    x = np.array([[1.0, 1.0, 1.0, 20.0]])
    y = np.array([[0.0, 1.5, 3.32, 1.5]])
    lit = smoke.floor(x, y, stage).sum(-1)[0]
    assert lit[0] > 2 * lit[1], "the centre line shows against the asphalt"
    assert lit[2] > 2 * lit[1], "and so does the edge line"
    assert lit[1] > 2 * lit[3], "under the lamp is brighter than between lamps"
    assert math.isfinite(lit.sum())


def test_a_pose_tips_the_nose_up():
    at = car.pose(0.0, pitch=0.1)
    assert at((2.0, 0, 0))[2] > at((-2.0, 0, 0))[2]


def test_a_jet_is_painted_bright_at_the_mouth_and_clear_outside(
    tmp="/tmp/codimate-jet.png",
):
    from PIL import Image

    jets.paint_jet(tmp, seed=0, wide=32, tall=128)
    image = Image.open(tmp)
    assert image.size == (32, 128) and image.mode == "RGBA"
    assert image.getpixel((16, 6))[3] > 200, "white-hot at the mouth"
    assert image.getpixel((0, 6))[3] < 40, "nothing beside it"
    assert image.getpixel((16, 127))[3] < 40, "faded out at the end"


def test_the_car_draws():
    import codimate as cm

    cam = science.Camera(azimuth=32, elevation=6, distance=20, scale=190)
    look = car.Look(car.pose(1.0), [(1.0, None)] * 4, spin=0.5)
    assert car.draw(cm.Scene(), cam, look) > 20


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
    import support

    raise SystemExit(support.run(globals()))
