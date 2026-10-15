"""Pure geometry for turning equal-width lines into familiar areas.

This module knows coordinates and lengths, not Codimate scenes. That makes the
shape calculations easy to check without building or rendering a film.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

Point = tuple[float, float]


@dataclass(frozen=True)
class AreaLayout:
    """Dimensions shared by the stack, circle, and area-under-a-curve scenes."""

    line_count: int = 40
    base_length: float = 520
    height: float = 400
    top_length: float = 180
    shear: float = 160
    bottom: float = 1100
    points_per_line: int = 49
    circle_radius: float = 135
    centre: Point = (540, 965)
    axis_left: float = 160
    axis_right: float = 920
    axis_bottom: float = 1180
    axis_height: float = 480
    axis_span: float = 3.0

    def __post_init__(self):
        if self.line_count < 1:
            raise ValueError("line_count must be positive")
        if self.points_per_line < 2:
            raise ValueError("points_per_line must be at least 2")
        if self.circle_radius <= 0 or self.height <= 0 or self.axis_span <= 0:
            raise ValueError("height, circle_radius, and axis_span must be positive")

    @property
    def line_thickness(self) -> float:
        return self.height / self.line_count

    def straight_line(self, x: float, length: float, y: float) -> list[Point]:
        """Sample a horizontal line with a fixed number of points."""
        intervals = self.points_per_line - 1
        return [(x + length * i / intervals, y) for i in range(self.points_per_line)]

    def ring(self, radius: float, unroll: float) -> list[Point]:
        """Return one line as a ring, partly opened into its full circumference."""
        circumference = 2 * math.pi * radius
        bend = (1 - unroll) / radius
        bottom_x, bottom_y = self.centre[0], self.centre[1] + radius
        points = []
        for index in range(self.points_per_line):
            distance = -circumference / 2 + circumference * index / (
                self.points_per_line - 1
            )
            if bend < 1e-9:
                points.append((bottom_x + distance, bottom_y))
                continue
            angle = bend * distance
            points.append(
                (
                    bottom_x + math.sin(angle) / bend,
                    bottom_y - (1 - math.cos(angle)) / bend,
                )
            )
        return points

    def unplaced_row(self, state: dict, index: int) -> tuple[float, float, float]:
        """Return a row's shear, line length, and missing length before centring."""
        fraction = (index + 0.5) / self.line_count
        length = self.base_length + (state["top"] - self.base_length) * fraction
        missing = (
            0.0
            if state["top"] == self.base_length
            else self.base_length + state["top"] - length
        )
        return state["shear"] * fraction, length, missing

    def row(self, state: dict, index: int) -> tuple[float, float, float]:
        """Return a centred row's x position, line length, and missing length."""
        ends = [self.unplaced_row(state, edge) for edge in (0, self.line_count - 1)]
        left = min(x for x, _, _ in ends)
        right = max(x + length + missing * state["copy"] for x, length, missing in ends)
        x, length, missing = self.unplaced_row(state, index)
        centre_x = self.centre[0]
        return x + centre_x - (left + right) / 2, length, missing

    def curve_point(self, x: float, y: float) -> Point:
        """Map a point in graph units to the on-screen axes."""
        width = self.axis_right - self.axis_left
        screen_x = self.axis_left + width * x / self.axis_span
        screen_y = self.axis_bottom - self.axis_height * y
        return screen_x, screen_y


def curve_height(x: float) -> float:
    """The smooth example curve, in graph units."""
    return 0.55 + 0.3 * math.sin(1.7 * x + 0.3) + 0.12 * x


def brace_path(length: float, depth: float, steps: int = 40) -> list[Point]:
    """Brace centreline along the x-axis, from zero to ``length``."""
    radius = depth / 2
    half = []
    for index in range(steps + 1):
        angle = math.pi - (math.pi / 2) * index / steps
        half.append((radius + radius * math.cos(angle), radius * math.sin(angle)))
    half.append((length / 2 - radius, radius))
    for index in range(steps + 1):
        angle = -math.pi / 2 + (math.pi / 2) * index / steps
        half.append(
            (
                length / 2 - radius + radius * math.cos(angle),
                2 * radius + radius * math.sin(angle),
            )
        )
    mirror = [(length - x, y) for x, y in reversed(half[:-1])]
    return half + mirror
