"""The ball rolling across on its spring: the one sound that follows a motion
along its whole length, so it lives beside ``follow``."""

from __future__ import annotations

import numpy as np
from studio.sound.dsp import SR, TAU, band, grain, highpass, lowpass, norm, pan, samples
from studio.sound.instruments import knock

from .follow import spring


def roll(seconds, path, to_pan, rng, bounciness=0.35):
    """A ball rolling along ``path`` (start x, end x) on its spring: a low
    rumble that tracks its speed, the turn of the ball in it, a soft tap at
    each turn of the overshoot, and a pan that follows it. ``to_pan`` maps an
    x on screen to a pan position. Stereo."""
    n = samples(seconds)
    x0, x1 = path
    x = x0 + (x1 - x0) * spring(np.linspace(0, 1, n), bounciness)
    v = np.gradient(x) * SR  # px per second
    speed = np.abs(v) / np.abs(v).max()

    rumble = highpass(lowpass(np.cumsum(rng.standard_normal(n)), 260), 35)
    turn = np.cumsum(np.abs(v)) / SR / (TAU * 34)  # the ball's radius is 34 px
    rumble *= 1 + 0.35 * np.sin(TAU * turn)
    texture = band(rng.standard_normal(n), 700, 2200) * grain(n, 40, 0.6, rng) * 0.08
    body = (norm(rumble) + texture) * speed**0.8

    taps = np.zeros(n)
    turns = np.where(np.diff(np.sign(v)) != 0)[0][:2]
    for k, i in enumerate(turns):
        hit = knock(rng.uniform(150, 180), rng)[: n - i] * (0.5, 0.3)[k]
        taps[i : i + len(hit)] += hit
    return pan(norm(body) + taps, to_pan(x))
