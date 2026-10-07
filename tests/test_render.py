"""Every example renders a video, end to end: view, diff, tween, rasterize, ffmpeg.

Slow, and needs `ffmpeg` and `typst`. Run it with `python tests/run.py --render`, or
with names to render only those: `python tests/run.py --render year maxwell`.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = sorted(ROOT.glob("*/main.py"))

# `run.py --render <name>...` grades only those.
_only = [n for n in os.environ.get("CODIMATE_ONLY", "").split(",") if n]
if _only:
    EXAMPLES = [m for m in EXAMPLES if m.parent.name in _only]
    missing = set(_only) - {m.parent.name for m in EXAMPLES}
    if missing:
        raise SystemExit(f"no such example: {', '.join(sorted(missing))}")

WIDTH, HEIGHT = 1920, 1080
RATES = (30.0, 60.0)


def _probe(video, fields):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v",
         "-show_entries", f"stream={fields}", "-of", "csv=p=0", str(video)],
        capture_output=True, text=True, check=True).stdout.strip()
    return out.split(",")


def _frames(video, count=12):
    """A frame a second, as small greyscale thumbnails."""
    w, h = 160, 90
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video),
         "-vf", f"fps=1,scale={w}:{h}", "-frames:v", str(count),
         "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True).stdout
    size = w * h
    return [raw[i * size:(i + 1) * size] for i in range(len(raw) // size)]


_RENDERED = {}


def _video(main_py):
    """Run one example the way a reader would, and return what it wrote."""
    if main_py not in _RENDERED:
        done = subprocess.run([sys.executable, str(main_py)],
                              cwd=ROOT, capture_output=True, text=True)
        assert done.returncode == 0, \
            f"{main_py.parent.name} failed:\n{done.stderr[-2000:]}"
        written = [l for l in done.stdout.splitlines() if l.startswith("wrote ")]
        assert written, f"{main_py.parent.name} printed no output path:\n{done.stdout}"
        video = ROOT / written[-1][len("wrote "):].strip()
        assert video.exists(), f"{video} was announced but not written"
        _RENDERED[main_py] = video
    return _RENDERED[main_py]


def test_every_example_renders_a_video():
    assert EXAMPLES, "no examples found"
    for main_py in EXAMPLES:
        name = main_py.parent.name
        video = _video(main_py)
        w, h, rate = _probe(video, "width,height,r_frame_rate")
        num, den = rate.split("/")
        assert (int(w), int(h)) == (WIDTH, HEIGHT), f"{name}: {w}x{h}"
        fps = int(num) / int(den)
        assert any(abs(fps - r) < 0.01 for r in RATES), f"{name}: {rate}"
        assert float(_probe(video, "duration")[0]) > 2.0, f"{name}: too short"


def test_every_example_actually_draws_and_moves():
    """Catches the two ways a render fails while still producing a file: a black
    video, and a frozen one. It does not catch a video that moves wrongly."""
    for main_py in EXAMPLES:
        name = main_py.parent.name
        frames = _frames(_video(main_py))
        assert len(frames) >= 3, f"{name}: could not sample frames"
        assert max(max(f) for f in frames) > 40, f"{name}: nearly black"
        moved = [sum(1 for a, b in zip(x, y) if abs(a - b) > 24) / len(x)
                 for x, y in zip(frames, frames[1:])]
        ink = max(sum(1 for p in f if p > 24) / len(f) for f in frames)
        assert ink > 0.0, f"{name}: nothing is drawn at all"
        assert max(moved) / ink > 0.15, f"{name}: nothing moves"
