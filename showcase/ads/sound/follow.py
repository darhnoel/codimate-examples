"""The picture's motion, re-derived, so a sound can follow what it cannot see.

Each function answers one question with the Engine's own arithmetic: where the
ball is on its spring, when each letter of a staggered title moves, which bar
moves in each swap of the sort.
"""

from __future__ import annotations

import numpy as np

TAU = 2 * np.pi


def spring(u, bounciness):
    """Progress along ``ease="spring"`` at ``u`` (0..1): the Engine's damped
    spring, scaled to land exactly on 1."""
    damping, freq = 7 - 4 * bounciness, TAU * (0.8 + 1.4 * bounciness)

    def raw(t):
        return 1 - np.exp(-damping * t) * (
            np.cos(freq * t) + damping / freq * np.sin(freq * t)
        )

    return raw(u) / raw(1.0)


def letter_starts(text, start, length, stagger):
    """When each letter of a staggered title starts to move, narrowing a
    stagger too wide for its beat the way the Engine does."""
    letters = [c for c in text if not c.isspace()]
    n = len(letters)
    if n > 1 and 1 - (n - 1) * stagger < 0.05:
        stagger = 0.95 / (n - 1)
    return [start + k * stagger * length for k in range(n)]


def bubble_swaps(values):
    """Each swap bubble sort makes: (left slot, the value moving right)."""
    values, swaps = list(values), []
    for end in range(len(values) - 1, 0, -1):
        for i in range(end):
            if values[i] > values[i + 1]:
                swaps.append((i, values[i]))
                values[i], values[i + 1] = values[i + 1], values[i]
    return swaps
