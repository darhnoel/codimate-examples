"""Codimate 0.4 launch film: thirty seconds of type, motion and sound on white.

    python about-codimate/ads/main.py            # the film, with its sound
    python about-codimate/ads/main.py --audio    # only the sound track
    python about-codimate/ads/main.py --stills   # a few frames, to check layout

The parts: ``story`` is what happens and for how long, ``scenes`` what each
moment looks like, ``look`` the type and colour, and ``sound`` everything heard.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import codimate as cm

import sound
from look import TITLES
from scenes import places, view
from story import Film, tell, timing

RESULTS = Path(__file__).resolve().parents[2] / "results"
OUT = RESULTS / "codimate-0.4-launch.mp4"
FPS = 30


def film() -> cm.Explanation:
    """The story, drawn by the scenes, moving by these rules."""
    big_titles = ("animated", "brand")  # these two enter letter by letter
    motion = [
        rule
        for name, title in TITLES.items()
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


def render(ad: cm.Explanation) -> None:
    """Draw the picture, then lay the mastered sound under it."""
    RESULTS.mkdir(exist_ok=True)
    ad.render(str(OUT), fps=FPS, scale=1.0)
    track = soundtrack(ad)
    with_sound = OUT.with_name(f"{OUT.stem}.sound{OUT.suffix}")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(OUT), "-i", str(track)]
        + ["-map", "0:v", "-map", "1:a", "-frames:v", str(round(ad.duration * FPS))]
        + ["-t", f"{ad.duration:.3f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k"]
        + ["-movflags", "+faststart", str(with_sound)],
        check=True,
    )
    with_sound.replace(OUT)
    print(f"wrote {OUT}")


def stills(ad: cm.Explanation) -> None:
    folder = RESULTS / "codimate-0.4-launch-stills"
    folder.mkdir(parents=True, exist_ok=True)
    for seconds in (0.9, 2, 7, 12, 17, 22, 27):
        ad.frame_at(seconds, str(folder / f"{int(seconds):02d}.png"))
    print(f"wrote {folder}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--audio", action="store_true", help="only the sound track")
    parser.add_argument("--stills", action="store_true", help="a few frames")
    args = parser.parse_args()

    ad = film()
    print(f"duration: {ad.duration:.2f}s")
    if args.audio:
        print(f"wrote {soundtrack(ad)}")
    elif args.stills:
        stills(ad)
    else:
        render(ad)


if __name__ == "__main__":
    main()
