"""The cue sheet: which sound plays at which beat, how loud, and where.

Read top to bottom it is the film's sound, section by section. Every time comes
from the film's own timeline and every position from the layout, so nothing is
placed by ear and nothing drifts when the picture changes.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from studio.sound import instruments as play
from studio.sound.dsp import note, pan
from studio.sound.room import Track
from studio.sound.timeline import Beats

from .ball import roll
from .follow import bubble_swaps, letter_starts


@dataclass(frozen=True)
class Places:
    """Where things are on screen, so each cue sits where it is seen."""

    width: float
    code_left: float  # where typed code starts
    ball: tuple  # (start x, end x)
    bar_xs: tuple  # each bar slot's x, left to right
    bars: tuple  # the values being sorted, in their starting order
    marker: tuple  # (left x, right x) of the highlighted word
    code: str  # what is typed, one beat per character
    animated: str  # the title that enters letter by letter

    def pan(self, x):
        """A pan position for an x on screen, kept off the hard edges."""
        return (x - self.width / 2) / (self.width / 2) * 0.7


def score(timeline, duration: float, places: Places, seed: int = 4) -> np.ndarray:
    """Every cue on the film's timeline, as stereo float samples. The same
    seed gives the same track, sample for sample."""
    rng = np.random.default_rng(seed)
    beats, track = Beats(timeline), Track(duration)
    for section in (_opening, _write_python, _sort, _fonts, _highlight, _brand):
        section(track, beats, places, rng)
    return track.mix(rng)


def _opening(track, beats, places, rng):
    """ "Code." lands with weight; "Animated." rises on a glass tick per letter."""
    start, _ = beats.first("code_in")
    track.add(start, play.thump(rng), db=-5, wet=0.12)

    start, length = beats.first("animated")
    scale = ["A4", "B4", "C#5", "E5", "F#5", "A5", "B5", "C#6", "E6"]
    for k, at in enumerate(letter_starts(places.animated, start, length, 0.72)):
        ping = play.glass(note(scale[k % len(scale)]), 0.9, 0.35, rng)
        track.add(at + 0.01, ping, db=-17, position=-0.4 + 0.8 * k / 8, wet=0.35)


def _write_python(track, beats, places, rng):
    """The headline slides down; every key is typed; the ball rolls on its spring."""
    start, _ = beats.first("python_title")
    track.add(start, play.paper_slide(rng), db=-13, wet=0.15)

    keys = {
        "letter": [play.key(rng, "letter") for _ in range(8)],
        "space": [play.key(rng, "space") for _ in range(4)],
        "return": [play.key(rng, "return") for _ in range(3)],
    }
    order = rng.permutation(64)
    typed = beats.starts("type")
    code_x = places.code_left / (places.width / 2) - 1
    for k, (at, char) in enumerate(zip(typed, places.code)):
        kind = "return" if char == "\n" else "space" if char == " " else "letter"
        clip = keys[kind][order[k % 64] % len(keys[kind])]
        jitter = rng.uniform(-0.004, 0.004)
        track.add(
            at + jitter,
            clip,
            db=-21 + rng.uniform(-2, 1),
            position=code_x + 0.3 * k / len(typed),
            wet=0.08,
        )

    start, length = beats.first("roll")
    track.add(start, roll(length, places.ball, places.pan, rng), db=-9, wet=0.1)


def _sort(track, beats, places, rng):
    """Each swap knocks a wooden bar, taller bars lower; sorted, a chord."""
    start, _ = beats.first("sort_title")
    track.add(start - 0.08, play.swipe(0.5, rng, direction=-1), db=-15, wet=0.15)

    notes = {1: "E5", 2: "D5", 3: "B4", 4: "A4", 5: "F#4"}
    for at, (slot, value) in zip(beats.starts("swap"), bubble_swaps(places.bars)):
        middle = (places.bar_xs[slot] + places.bar_xs[slot + 1]) / 2
        knock = play.knock(note(notes[value]), rng)
        track.add(at + 0.02, knock, db=-12, position=places.pan(middle), wet=0.2)

    start, _ = beats.first("sort_done")
    for k, name in enumerate(("D5", "F#5", "A5")):
        bar = play.marimba(note(name), rng)
        at = start + 0.05 + 0.045 * k
        track.add(at, bar, db=-14, position=(k - 1) * 0.25, wet=0.25)


def _fonts(track, beats, places, rng):
    """The headline slides the other way; each new font flicks over like a card."""
    start, _ = beats.first("font_title")
    track.add(start - 0.08, play.swipe(0.5, rng, direction=1), db=-15, wet=0.15)

    for at in beats.starts("font"):
        flick = play.card_flick(rng)
        track.add(at, flick, db=-17, position=rng.uniform(-0.1, 0.1), wet=0.12)


def _highlight(track, beats, places, rng):
    """The headline swells into focus; the marker scratches across its word."""
    start, _ = beats.first("highlight_start")
    resolve, length = beats.first("blur_resolve")
    swell = play.blur_swell(resolve + length - start - 0.1, rng)
    track.add(start + 0.1, swell, db=-15, wet=0.3)

    start, length = beats.first("mark")
    stroke = play.felt_tip(length, rng)
    left, right = places.marker
    travel = np.linspace(places.pan(left), places.pan(right), len(stroke))
    track.add(start, pan(stroke, travel), db=-12, wet=0.1)


def _brand(track, beats, places, rng):
    """A low lift under the wordmark, a two-note chime as it lands, a tap."""
    start, length = beats.first("brand")
    track.add(start, play.brand_swell(length, rng), db=-17, wet=0.3)
    landed = start + length
    low = play.glass(note("E5"), 3.0, 1.1, rng)
    track.add(landed, low, db=-9, position=-0.12, wet=0.45)
    high = play.glass(note("B5"), 3.0, 1.0, rng)
    track.add(landed + 0.09, high, db=-11, position=0.12, wet=0.45)

    start, _ = beats.first("install")
    track.add(start + 0.15, play.confirm_tap(rng), db=-19, wet=0.2)
