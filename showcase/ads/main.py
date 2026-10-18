"""Codimate 0.4 launch film: thirty seconds of type, motion and sound, light or dark.

    python showcase/ads/main.py            # the film, with its sound
    python showcase/ads/main.py --audio    # only the sound track
    python showcase/ads/main.py --stills   # a few frames, to check layout
    python showcase/ads/main.py --dark     # any of these, on black

The parts: ``story`` is what happens and for how long, ``scenes`` what each
moment looks like, ``look`` the type and colour, and ``sound`` everything heard.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import codimate as cm

import look
import sound
from scenes import places, view
from story import Film, tell, timing

RESULTS = Path(__file__).resolve().parents[2] / "results"
NAME = "codimate-0.4-launch"
FPS = 30


def film() -> cm.Explanation:
    """The story, drawn by the scenes, moving by these rules."""
    big_titles = ("animated", "brand")  # these two enter letter by letter
    motion = [
        rule
        for name, title in look.titles().items()
        for rule in title.rules(stagger=0.72 if name in big_titles else 0.14)
    ] + [
        cm.Rule("ball", ease="spring", bounciness=0.35),
        cm.Rule("bar/*", ease="spring", stagger=0.08, order="centre"),
        cm.Rule("key_word marker", ease="out"),
    ]
    return cm.explain(
        trace=cm.trace(tell, Film()), view=view, motion=motion, timing=timing()
    )


def soundtrack(ad: cm.Explanation) -> Path:
    return sound.soundtrack(ad.timeline(), ad.duration, places(), RESULTS / "ad-sounds")


def render(ad: cm.Explanation, name: str) -> None:
    """Draw the picture, then lay the mastered sound under it."""
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"{name}.mp4"
    ad.render(str(out), fps=FPS, scale=1.0)
    track = soundtrack(ad)
    with_sound = out.with_name(f"{out.stem}.sound{out.suffix}")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(out), "-i", str(track)]
        + ["-map", "0:v", "-map", "1:a", "-frames:v", str(round(ad.duration * FPS))]
        + ["-t", f"{ad.duration:.3f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k"]
        + ["-movflags", "+faststart", str(with_sound)],
        check=True,
    )
    with_sound.replace(out)
    print(f"wrote {out}")


def stills(ad: cm.Explanation, name: str) -> None:
    folder = RESULTS / f"{name}-stills"
    folder.mkdir(parents=True, exist_ok=True)
    for seconds in (0.9, 2, 7, 12, 17, 22, 27):
        ad.frame_at(seconds, str(folder / f"{int(seconds):02d}.png"))
    print(f"wrote {folder}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--audio", action="store_true", help="only the sound track")
    parser.add_argument("--stills", action="store_true", help="a few frames")
    parser.add_argument("--dark", action="store_true", help="on black, not white")
    args = parser.parse_args()

    look.use("dark" if args.dark else "light")
    name = f"{NAME}-dark" if args.dark else NAME
    ad = film()
    print(f"duration: {ad.duration:.2f}s")
    if args.audio:
        print(f"wrote {soundtrack(ad)}")
    elif args.stills:
        stills(ad, name)
    else:
        render(ad, name)


if __name__ == "__main__":
    main()
