"""The area lesson's coordinate calculations need no Codimate render."""

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mathematics.area.geometry import AreaLayout, brace_path  # noqa: E402


def test_rectangle_rows_keep_their_width_and_centre():
    layout = AreaLayout()
    state = {"top": layout.base_length, "shear": 0, "copy": 0}

    rows = [layout.row(state, index) for index in range(layout.line_count)]

    assert all(math.isclose(row[0], 280) for row in rows)
    assert all(math.isclose(row[1], layout.base_length) for row in rows)
    assert all(row[2] == 0 for row in rows)


def test_flipped_rows_fill_constant_base_width():
    layout = AreaLayout()
    state = {"top": layout.top_length, "shear": layout.shear, "copy": 1}

    for index in range(layout.line_count):
        _, length, missing = layout.row(state, index)
        assert math.isclose(length + missing, layout.base_length + layout.top_length)


def test_ring_and_straight_line_have_the_same_length():
    layout = AreaLayout(points_per_line=49)
    radius = 12

    ring = layout.ring(radius, unroll=0)
    straight = layout.ring(radius, unroll=1)

    for x, y in ring:
        centre_x, centre_y = layout.centre
        assert math.isclose(math.hypot(x - centre_x, y - centre_y), radius)
    assert math.isclose(straight[-1][0] - straight[0][0], 2 * math.pi * radius)
    assert all(point[1] == straight[0][1] for point in straight)


def test_brace_starts_and_ends_at_its_requested_length():
    path = brace_path(100, 20)

    assert math.isclose(path[0][0], 0)
    assert math.isclose(path[-1][0], 100)
