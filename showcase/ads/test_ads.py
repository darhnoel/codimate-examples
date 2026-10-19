"""The launch film: its sound follows its picture, the same every run.

Nothing renders and no file is written.
"""

import numpy as np

import sound
from main import film
from scenes import places
from sound.follow import bubble_swaps, letter_starts, spring
from studio.sound.dsp import SR


def _level(track, a, b):
    part = track[int(a * SR) : int(b * SR)]
    return 20 * np.log10(np.sqrt((part**2).mean()) + 1e-12)


def _power(part, channel):
    return (part[:, channel] ** 2).sum()


def test_the_swaps_are_bubble_sorts_own():
    assert bubble_swaps([5, 1, 4, 2, 3]) == [
        (0, 5), (1, 5), (2, 5), (3, 5), (1, 4), (2, 4)
    ]  # fmt: skip


def test_a_too_wide_stagger_is_narrowed_like_the_engine():
    starts = letter_starts("Animated.", 1.0, 0.55, 0.72)
    assert len(starts) == 9
    assert abs(starts[-1] - (1.0 + 0.95 * 0.55)) < 1e-9, "the last letter ends the beat"


def test_the_spring_starts_still_and_lands_exactly():
    u = np.linspace(0, 1, 101)
    p = spring(u, 0.35)
    assert p[0] == 0 and abs(p[-1] - 1) < 1e-12
    assert p.max() > 1, "it overshoots before it settles"


def test_the_track_is_the_film_and_the_same_every_run():
    ad, where = film(), places()
    track = sound.score(ad.timeline(), ad.duration, where)
    assert track.shape == (round(ad.duration * SR), 2)
    assert np.array_equal(track, sound.score(ad.timeline(), ad.duration, where))
    assert _level(track, 5.41, 6.9) > _level(track, 21.0, 23.5) + 30, "the ball rolls"
    early = track[int(5.45 * SR) : int(5.7 * SR)]
    late = track[int(6.2 * SR) : int(6.6 * SR)]
    assert _power(early, 0) > _power(early, 1), "the ball starts on the left"
    assert _power(late, 1) > _power(late, 0), "and ends on the right"
