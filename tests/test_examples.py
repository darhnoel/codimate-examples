"""Every example still builds, and every equation in it typesets. Nothing renders.

Building a film runs its script up to the `render` call, which is where nearly every
mistake in an example shows: a bad shape, a clash of names, a LaTeX string the Typst
bridge cannot read. It needs `typst` for the formulas, and no `ffmpeg`.

Examples are discovered, not listed, so a new one is covered the day it is added.
"""

from pathlib import Path

import codimate as cm
from codimate import preview

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = sorted(ROOT.glob("*/*/main.py"))


def test_there_are_examples():
    assert EXAMPLES, "no */*/main.py found: has the layout changed?"


def test_every_example_builds_and_every_formula_in_it_typesets():
    for main in EXAMPLES:
        name = main.parent.name
        try:
            film = preview.build(main)
        except Exception as wrong:
            raise AssertionError(f"{name} does not build: {wrong}") from wrong
        assert len(film.scenes) > 2, f"{name}: a film of {len(film.scenes)} moments"
        formulas = {}
        for scene in film.scenes:
            for shape in scene._shapes.values():
                if shape.kind == "formula":
                    formulas[shape.text] = shape.size
        for latex, size in formulas.items():
            width, height = cm.measure_math(latex, size)
            assert width > 0 and height > 0, f"{name}: {latex!r}"
