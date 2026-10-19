"""Each sound source, built from noise and resonance to imitate a real thing:
a laptop key, a wooden bar, struck glass, paper, a felt tip.

Every function takes a seeded ``rng`` and returns a mono clip peaking at 1,
except where a sound moves across the stereo field and returns stereo.
"""

from __future__ import annotations

import numpy as np

from .dsp import (
    SR,
    TAU,
    band,
    decay,
    grain,
    highpass,
    lowpass,
    norm,
    pan,
    ring,
    samples,
    sweep,
    times,
)

# ------------------------------------------------------------------ struck


def key(rng, kind="letter"):
    """A laptop key: plastic click, the switch's ring, a little body. Space
    and Return are heavier and rattle on their stabilisers."""
    heavy = {"letter": 1.0, "space": 1.6, "return": 2.2}[kind]
    seconds = 0.09 * heavy
    noise = rng.standard_normal(samples(seconds))
    click = highpass(noise, 2500) * decay(seconds, 0.0007)
    switch = ring(rng.uniform(2300, 3300) / heavy**0.3, seconds, 0.005)
    body = ring(rng.uniform(170, 250) / heavy**0.5, seconds, 0.010 * heavy)
    press = click + 0.35 * switch + 0.45 * heavy * body
    if kind != "letter":
        rattle = np.roll(click, samples(rng.uniform(0.003, 0.006))) * 0.5
        press = press + rattle
    return norm(press) * rng.uniform(0.75, 1.0)


def knock(freq, rng):
    """A tuned wooden bar, struck softly."""
    seconds = 0.45
    modes = [(1.0, 1.0, 0.11), (3.93, 0.25, 0.03), (9.2, 0.08, 0.012)]
    tone = sum(a * ring(freq * r, seconds, tau) for r, a, tau in modes)
    mallet = band(rng.standard_normal(samples(seconds)), 800, 4000)
    mallet = mallet * decay(seconds, 0.002)
    return norm(tone + 0.3 * mallet)


def marimba(freq, rng):
    """A marimba bar: longer and rounder than a knock."""
    seconds = 1.6
    modes = [(1.0, 1.0, 0.55), (3.9, 0.3, 0.12), (9.2, 0.07, 0.04)]
    tone = sum(a * ring(freq * r, seconds, tau) for r, a, tau in modes)
    mallet = lowpass(rng.standard_normal(samples(seconds)), 2500)
    mallet = mallet * decay(seconds, 0.003)
    return norm(tone + 0.15 * mallet)


def glass(freq, seconds, tau, rng):
    """Struck glass: inharmonic partials, the top ones dying first, and a
    slow beat between two near-identical copies of the fundamental."""
    partials = [
        (1.0, 1.0, 1.0),
        (2.32, 0.45, 0.55),
        (4.25, 0.22, 0.3),
        (6.63, 0.1, 0.15),
    ]
    tone = sum(a * ring(freq * r, seconds, tau * d) for r, a, d in partials)
    tone += 0.5 * ring(freq * 1.0012, seconds, tau)
    tick = highpass(rng.standard_normal(samples(seconds)), 5000)
    tick = tick * decay(seconds, 0.0006)
    return norm(tone + 0.25 * tick)


def thump(rng):
    """A first word landing: a breath of air, then a soft low weight."""
    seconds, lands = 0.6, 0.2
    air = sweep(seconds, lambda u: 300 * (2500 / 300) ** u, 0.9, rng)
    air *= np.linspace(0, 1, len(air)) ** 2 * np.exp(
        -np.maximum(times(seconds) - lands, 0) / 0.03
    )
    t = times(seconds - lands)
    pitch = 70 - 22 * (1 - np.exp(-t / 0.06))
    low = np.sin(TAU * np.cumsum(pitch) / SR) * np.exp(-t / 0.12)
    low = np.concatenate([np.zeros(samples(lands)), low])[: len(air)]
    return norm(0.35 * norm(air) + low)


def confirm_tap(rng):
    """A soft interface tap: a falling pop with a tiny tick on top."""
    seconds = 0.12
    t = times(seconds)
    pitch = 1200 + 600 * np.exp(-t / 0.01)
    pop = np.sin(TAU * np.cumsum(pitch) / SR) * decay(seconds, 0.02, 0.001)
    tick = highpass(rng.standard_normal(len(t)), 4000) * decay(seconds, 0.0008)
    return norm(pop + 0.3 * tick)


# ------------------------------------------------------------------- air


def swipe(seconds, rng, direction):
    """Air past the ear as text slides sideways: the pitch arches and the pan
    travels with it. ``direction`` -1 moves right to left. Stereo."""
    body = sweep(seconds, lambda u: 700 * (4.5 ** np.sin(np.pi * u)), 0.6, rng)
    u = np.linspace(0, 1, len(body))
    body *= np.sin(np.pi * u) ** 1.6
    return pan(norm(body), direction * (0.7 - 1.4 * u))


def blur_swell(seconds, rng):
    """Out of focus into focus: air rising in pitch and level, then gone."""
    body = sweep(seconds, lambda u: 350 * (7000 / 350) ** u, 1.0, rng)
    u = np.linspace(0, 1, len(body))
    body *= u**2.2 * np.clip((1 - u) / 0.06, 0, 1)
    return norm(body)


def brand_swell(seconds, rng):
    """A low, soft lift under the wordmark."""
    u = np.linspace(0, 1, samples(seconds))
    air = lowpass(sweep(seconds, lambda u: 200 * 6**u, 1.2, rng), 3000)
    sub = np.sin(TAU * 55 * times(seconds))
    level = np.sin(np.pi / 2 * u) ** 2 * np.clip((1 - u) / 0.15, 0, 1)
    return norm((0.6 * norm(air) + 0.4 * sub) * level)


# ----------------------------------------------------------------- paper


def paper_slide(rng):
    """A sheet sliding down, its pitch falling, the paper's grain in it."""
    seconds = 0.34
    body = sweep(seconds, lambda u: 4200 * (1300 / 4200) ** u, 0.7, rng)
    u = np.linspace(0, 1, len(body))
    body *= np.sin(np.pi * u**0.6) * grain(len(body), 180, 0.55, rng)
    return norm(body)


def card_flick(rng):
    """A card flicked over: a snap, then a short flutter."""
    seconds = 0.12
    snap = highpass(rng.standard_normal(samples(seconds)), 3000)
    snap *= decay(seconds, 0.0012)
    flutter = band(rng.standard_normal(samples(seconds)), 1800, 7000)
    flutter *= decay(seconds, 0.02, 0.004)
    flutter *= 1 - 0.6 * (np.sin(TAU * rng.uniform(55, 75) * times(seconds)) > 0)
    return norm(snap + 0.6 * flutter)


def felt_tip(seconds, rng):
    """A highlighter drawn across paper, loudest while it moves fastest (as
    the stroke's ``out`` ease does), with a faint squeak riding the scratch."""
    n = samples(seconds)
    u = np.linspace(0, 1, n)
    speed = (1 - u) ** 2  # the slope of 1 - (1 - u)^3, up to a scale
    scratch = band(rng.standard_normal(n), 1500, 7500) * grain(n, 300, 0.7, rng)
    drift = lowpass(rng.standard_normal(n), 6, order=1)
    wobble = 1450 + 120 * drift / (np.abs(drift).max() + 1e-9)
    squeak = np.sin(TAU * np.cumsum(wobble) / SR) * 0.12
    attack = np.clip(u / 0.02, 0, 1)
    body = (scratch + squeak) * attack * speed**0.6
    tip = highpass(rng.standard_normal(n), 3000) * decay(seconds, 0.0015)
    return norm(body + 0.5 * tip)
