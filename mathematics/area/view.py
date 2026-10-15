"""Draw each saved area lesson state as one Codimate scene."""

import math

import codimate as cm

from common import EDGE, TEAL, TEXT, YELLOW, brace
from geometry import AreaLayout, curve_height
from story import CAPTIONS, COUNTS, CURVED, FORMULAS, STACKED

DROP = 140
PEN = 2


class AreaView:
    """Render the lesson's lines, braces, circle, and curve from its state."""

    def __init__(self, layout: AreaLayout = AreaLayout()):
        self.layout = layout

    def __call__(self, frame):
        state = frame.state
        stage = state["stage"]
        scene = cm.Scene()
        overlay = scene.overlay()
        self._draw_words(overlay, state)
        self._draw_lines(scene, state, stage)
        self._draw_stack_braces(scene, state, stage)
        self._draw_circle_braces(scene, stage)
        self._draw_curve(scene, state, stage)
        return scene

    def _write(self, where, key, latex, spec):
        size, at, shown = spec
        where.formula(key, latex, size=size, at=at).fill(TEXT).write(
            reveal=1.0 if shown else 0.0, pen=PEN
        )

    def _draw_words(self, overlay, state):
        for latex in dict.fromkeys(CAPTIONS.values()):
            self._write(
                overlay,
                ("caption", latex),
                latex,
                (52, (540, 220), latex == state["caption"]),
            )
        for latex in dict.fromkeys(FORMULAS.values()):
            self._write(
                overlay,
                ("formula", latex),
                latex,
                (56, (540, 1460), latex == state["formula"]),
            )

    def _draw_lines(self, scene, state, stage):
        layout = self.layout
        for index in range(layout.line_count):
            placed = index < state["placed"]
            y = (
                layout.bottom
                - layout.line_thickness * (index + 0.5)
                - (0 if placed else DROP)
            )
            x, length, missing = layout.row(state, index)
            colour = YELLOW if index == 0 and stage == "ask" else TEAL

            if stage in CURVED:
                points = layout.straight_line(
                    layout.axis_left - 40,
                    layout.axis_right - layout.axis_left + 80,
                    layout.axis_bottom,
                )
                thickness, colour = 3, TEXT
            elif state["circle"]:
                radius = (layout.line_count - index - 0.5) * (
                    layout.circle_radius / layout.line_count
                )
                points = layout.ring(radius, state["unroll"])
                thickness = layout.circle_radius / layout.line_count
            else:
                points = layout.straight_line(x, length, y)
                thickness = layout.line_thickness

            scene.curve(("line", index), points, w=thickness).fill(colour).on(
                opacity=1.0 if placed else 0.0
            )
            copied = state["copy"] and not state["circle"]
            scene.curve(
                ("copy", index),
                layout.straight_line(x + length, missing * state["copy"], y),
                w=layout.line_thickness * copied,
            ).fill(YELLOW)

    def _draw_stack_braces(self, scene, state, stage):
        layout = self.layout
        shown = float(stage in STACKED) * (1.0 - state["circle"])
        x_bottom, _, _ = layout.row(state, 0)
        x_top, _, _ = layout.row(state, layout.line_count - 1)
        at = brace(
            scene,
            "brace/a",
            (x_bottom, layout.bottom + 14),
            (x_bottom + layout.base_length, layout.bottom + 14),
            ((0.0, 1.0), 30, shown),
        )
        self._write(scene, "label/a", "a", (60, at, shown))

        rising = shown if state["placed"] > 1 else 0.0
        at = brace(
            scene,
            "brace/h",
            (x_bottom - 14, layout.bottom),
            (x_bottom - 14, layout.bottom - layout.line_thickness * state["placed"]),
            ((-1.0, 0.0), 30, rising),
        )
        self._write(scene, "label/b", "b", (60, at, stage in ("rect", "slide")))
        self._write(scene, "label/h", "h", (60, at, stage in STACKED[3:]))

        topped = float(stage in ("trap", "trap_copy", "trap_area"))
        at = brace(
            scene,
            "brace/c",
            (x_top, layout.bottom - layout.height - 14),
            (x_top + layout.top_length, layout.bottom - layout.height - 14),
            ((0.0, -1.0), 30, topped),
        )
        self._write(scene, "label/c", "c", (60, at, topped))

    def _draw_circle_braces(self, scene, stage):
        layout = self.layout
        shown = float(stage == "rings")
        half_circumference = math.pi * layout.circle_radius
        centre_x = layout.centre[0]
        at = brace(
            scene,
            "brace/base",
            (centre_x - half_circumference, layout.bottom + 14),
            (centre_x + half_circumference, layout.bottom + 14),
            ((0.0, 1.0), 30, shown),
        )
        self._write(scene, "label/base", r"2\pi r", (56, at, shown))
        at = brace(
            scene,
            "brace/r",
            (centre_x - half_circumference - 14, layout.bottom),
            (centre_x - half_circumference - 14, layout.bottom - layout.circle_radius),
            ((-1.0, 0.0), 26, shown),
        )
        self._write(scene, "label/r", "r", (56, at, shown))

    def _draw_curve(self, scene, state, stage):
        layout = self.layout
        curved = stage in CURVED
        finest = COUNTS[-1]
        count = state["count"] or COUNTS[0]
        grown = 1.0 if state["count"] else 0.0
        for index in range(finest):
            strip = index * count // finest
            width = (layout.axis_right - layout.axis_left) / count
            graph_x = (strip + 0.5) * layout.axis_span / count
            height = layout.axis_height * curve_height(graph_x) * grown
            scene.rect(
                ("strip", index),
                w=width,
                h=height,
                at=(
                    layout.axis_left + (strip + 0.5) * width,
                    layout.axis_bottom - height / 2,
                ),
            ).fill(TEAL, edge=EDGE, edge_w=0.8 * grown)

        drawn = layout.axis_span * state["drawn"]
        curve = [
            layout.curve_point(x, curve_height(x))
            for x in (drawn * index / 200 for index in range(201))
        ]
        scene.curve("curve", curve, w=5 if state["drawn"] else 0).fill(TEXT).on(layer=5)
        for name, x in (("a", layout.axis_left), ("b", layout.axis_right)):
            self._write(
                scene,
                ("axis", name),
                name,
                (56, (x, layout.axis_bottom + 50), curved),
            )
