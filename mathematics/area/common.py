"""Shared drawing colours and the curly-brace shape."""

import math

from geometry import brace_path


TEAL, YELLOW, TEXT = "#3fa7bb", "#ffd166", "#e8eef7"
EDGE = "#0b1a20"  # the hairline between lines


def brace(scene, key, start, end, paint):
    """A curly brace from `start` to `end`, drawn as a filled shape: thin at its
    ends and at its point, thickest along its arms. `paint` is (outward unit
    vector, depth in pixels, grow): at grow 0 it has shrunk to nothing at its
    middle, so it grows in and out rather than fading. Returns where its label
    goes."""
    (nx, ny), full_depth, grow = paint
    mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    start = (mid[0] + (start[0] - mid[0]) * grow, mid[1] + (start[1] - mid[1]) * grow)
    end = (mid[0] + (end[0] - mid[0]) * grow, mid[1] + (end[1] - mid[1]) * grow)
    depth = full_depth * grow
    length = math.dist(start, end) or 1.0
    ux, uy = (end[0] - start[0]) / length, (end[1] - start[1]) / length
    path = brace_path(length, depth)
    centre = [(start[0] + ux * x + nx * y, start[1] + uy * x + ny * y) for x, y in path]
    left, right = [], []
    for k, (x, y) in enumerate(centre):
        x0, y0 = centre[max(k - 1, 0)]
        x1, y1 = centre[min(k + 1, len(centre) - 1)]
        tx, ty = x1 - x0, y1 - y0
        size = math.hypot(tx, ty) or 1.0
        px, py = -ty / size, tx / size
        along = path[k][0] / length
        v = along if along <= 0.5 else 1 - along
        half = (
            grow * 3.2 * (0.25 + 0.75 * math.sin(math.pi * v / 0.5))
        )  # thin ends, tip
        left.append((x + px * half, y + py * half))
        right.append((x - px * half, y - py * half))
    scene.polygon(key, left + right[::-1]).fill(TEXT)
    return (mid[0] + nx * (full_depth + 44), mid[1] + ny * (full_depth + 44))
