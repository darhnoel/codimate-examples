"""The mix: one stereo bus the length of the film, and one small room that
every cue is sent into, so they sound like they happened in the same place."""

from __future__ import annotations

import numpy as np

from .dsp import lowpass, pan, samples, times


class Track:
    """A dry bus and a reverb send. Add clips at their times, then ``mix``."""

    def __init__(self, seconds: float):
        self.dry = np.zeros((samples(seconds), 2))
        self.send = np.zeros_like(self.dry)

    def add(self, at: float, clip, db: float = 0.0, position=0.0, wet: float = 0.15):
        """Lay ``clip`` at ``at`` seconds, ``db`` louder or quieter. A mono clip
        is panned to ``position``; ``wet`` is how much of it reaches the room."""
        stereo = clip if clip.ndim == 2 else pan(clip, position)
        start = samples(at) if at > 0 else 0
        stereo = stereo[: len(self.dry) - start] * 10 ** (db / 20)
        self.dry[start : start + len(stereo)] += stereo
        self.send[start : start + len(stereo)] += stereo * wet

    def mix(self, rng) -> np.ndarray:
        """The dry bus plus the room's answer to the send."""
        wet = _convolve(self.send, _room(rng))[: len(self.dry)]
        return self.dry + wet


def _room(rng) -> np.ndarray:
    """A small, soft room's impulse response: a pre-delay, three early
    reflections, then a darkening tail, decorrelated left and right."""
    t = times(1.1)
    tail = rng.standard_normal((len(t), 2)) * np.exp(-t / 0.16)[:, None]
    tail[: samples(0.012)] = 0
    tail = np.stack([lowpass(tail[:, c], 5500) for c in (0, 1)], axis=1)
    for delay, gain in ((0.007, 0.5), (0.013, 0.35), (0.021, 0.25)):
        tail[samples(delay), :] += gain
    return tail / np.sqrt((tail**2).sum(axis=0))


def _convolve(signal, impulse):
    size = 1 << int(np.ceil(np.log2(len(signal) + len(impulse))))
    return np.stack(
        [
            np.fft.irfft(
                np.fft.rfft(signal[:, c], size) * np.fft.rfft(impulse[:, c], size),
                size,
            )
            for c in (0, 1)
        ],
        axis=1,
    )
