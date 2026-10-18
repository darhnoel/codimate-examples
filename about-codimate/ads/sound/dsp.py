"""The building blocks every sound is made of: noise, filters, envelopes,
resonances, panning and pitch names. Mono signals are 1-D arrays at ``SR``."""

from __future__ import annotations

import numpy as np

SR = 48_000
TAU = 2 * np.pi


def samples(seconds: float) -> int:
    return max(1, int(round(seconds * SR)))


def times(seconds: float) -> np.ndarray:
    """Each sample's time, in seconds from the start."""
    return np.arange(samples(seconds)) / SR


def _filtered(x: np.ndarray, gain) -> np.ndarray:
    """Shape ``x`` by a magnitude response over frequency, with zero phase."""
    spectrum = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(spectrum * gain(np.maximum(freqs, 1.0)), len(x))


def lowpass(x, fc, order=2):
    return _filtered(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order)))


def highpass(x, fc, order=2):
    return _filtered(x, lambda f: 1 / np.sqrt(1 + (fc / f) ** (2 * order)))


def band(x, lo, hi, order=2):
    return highpass(lowpass(x, hi, order), lo, order)


def decay(seconds, tau, attack=0.0005):
    """A strike's envelope: a short rise, then an exponential fall."""
    t = times(seconds)
    rise = np.clip(t / attack, 0, 1) if attack > 0 else 1.0
    return rise * np.exp(-t / tau)


def ring(freq, seconds, tau, phase=0.0):
    """A damped sine: one mode of something struck."""
    t = times(seconds)
    return np.sin(TAU * freq * t + phase) * np.exp(-t / tau)


def sweep(seconds, centre, width, rng, bands=28):
    """Noise whose pitch follows ``centre(u)`` (Hz, u in 0..1), ``width``
    octaves wide: the body of every swipe, swell and slide."""
    n = samples(seconds)
    u = np.linspace(0, 1, n)
    edges = np.geomspace(120, 14_000, bands + 1)
    mids = np.sqrt(edges[:-1] * edges[1:])
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    where = np.log2(centre(u))
    for lo, hi, mid in zip(edges[:-1], edges[1:], mids):
        weight = np.exp(-0.5 * ((np.log2(mid) - where) / width) ** 2)
        if weight.max() > 1e-3:
            out += band(noise, lo, hi, order=3) * weight
    return out


def grain(n, rate, depth, rng):
    """Slow random wobble in loudness: paper fibre, a felt tip catching."""
    jitter = lowpass(rng.standard_normal(n), rate, order=1)
    jitter /= np.abs(jitter).max() + 1e-9
    return 1 - depth * (0.5 + 0.5 * jitter)


def norm(x):
    """Scale to a peak of 1."""
    return x / (np.abs(x).max() + 1e-12)


def pan(mono, position):
    """Constant-power pan to stereo; ``position`` -1 (left) .. 1, or one per
    sample to move it."""
    angle = (np.clip(position, -1, 1) + 1) * np.pi / 4
    return np.stack([mono * np.cos(angle), mono * np.sin(angle)], axis=1)


def note(name: str) -> float:
    """A pitch name's frequency: ``note("A4")`` is 440, ``note("C#5")`` 554."""
    steps = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    letter, rest = name[0], name[1:]
    sharp = rest.startswith("#")
    octave = int(rest[1:] if sharp else rest)
    return 440.0 * 2 ** ((steps[letter] + sharp + 12 * (octave - 4)) / 12)
