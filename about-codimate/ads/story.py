"""The script: what happens on screen, in order, and how long each beat lasts.

Each ``emit`` is one beat of the film. Nothing here draws; ``scenes.py`` says
what each beat looks like, and ``sound/`` what it sounds like.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import codimate as cm

from look import TITLES

CODE = "x = 0\nfor step in range(5):\n    x += step"
BARS = (5, 1, 4, 2, 3)
TYPE_SECONDS = 0.027
SECTION = 5.0  # every section after the opening lasts five seconds


@dataclass
class Film:
    phase: str = "intro"
    titles: dict = field(default_factory=lambda: dict.fromkeys(TITLES, "hidden"))
    typing: str = ""
    ball_x: float = 330
    ball_visible: bool = False
    bars: list = field(default_factory=lambda: cm.items(list(BARS)))
    comparing: tuple = ()
    font_index: int = 0
    font_sample_visible: bool = False
    marker_reveal: float = 0
    show_install: bool = False


def tell(film: Film, emit) -> None:
    """The film, beat by beat."""
    _opening(film, emit)
    _write_python(film, emit)
    _sort(film, emit)
    _fonts(film, emit)
    _highlight(film, emit)
    _brand(film, emit)


def _opening(film, emit):
    film.titles["code"] = "shown"
    emit("code_in")
    emit("code_hold")
    film.titles["code"] = "hidden"
    emit("code_out")
    film.titles["animated"] = "shown"
    emit("animated")
    emit("animated_hold")


def _write_python(film, emit):
    film.phase = "python"
    film.titles["animated"] = "hidden"
    film.ball_visible = True
    emit("python_start")
    film.titles["python"] = "shown"
    emit("python_title")
    for char in CODE:
        film.typing += char
        emit("type")
    film.ball_x = 1590
    emit("roll")
    emit("python_end")


def _sort(film, emit):
    film.phase = "sort"
    film.titles["python"] = "gone"
    emit("sort_start")
    film.titles["sort"] = "shown"
    emit("sort_title")
    for end in range(len(film.bars) - 1, 0, -1):
        for index in range(end):
            left, right = film.bars[index : index + 2]
            film.comparing = (left.id, right.id)
            emit("compare", items=[left, right])
            if left > right:
                film.bars[index], film.bars[index + 1] = right, left
                emit("swap", items=[left, right])
    film.comparing = ()
    emit("sort_done")


def _fonts(film, emit):
    film.phase = "fonts"
    film.titles["sort"] = "gone"
    film.font_index = 0
    film.font_sample_visible = True
    emit("font_start")
    film.titles["fonts"] = "shown"
    emit("font_title")
    for index in range(1, 5):
        film.font_index = index
        emit("font")
    film.font_sample_visible = False
    emit("font_done")
    film.titles["fonts"] = "hidden"
    emit("font_clear")


def _highlight(film, emit):
    film.phase = "highlight"
    film.titles["highlight"] = "blurred"
    film.marker_reveal = 0
    emit("highlight_start")
    film.titles["highlight"] = "shown"
    emit("blur_resolve")
    film.marker_reveal = 1
    emit("mark")
    emit("highlight_done")
    film.phase = "clear"
    film.titles["highlight"] = "hidden"
    emit("brand_clear")


def _brand(film, emit):
    film.phase = "brand"
    film.titles["brand"] = "shown"
    emit("brand")
    film.show_install = True
    emit("install")


def timing() -> cm.Timing:
    """How long each beat lasts. The two long sections pad themselves out so
    each still takes exactly five seconds, however much happens inside."""
    compares = sum(range(len(BARS)))
    swaps = 6  # the inversions in BARS
    return cm.Timing(
        opening=0.22,
        final_hold=3.15,
        default=0.6,
        events={
            "code_in": 0.45,
            "code_hold": 0.38,
            "code_out": 0.26,
            "animated": 0.55,
            "animated_hold": 2.14,
            "python_start": 0.15,
            "python_title": 0.15,
            "type": TYPE_SECONDS,
            "roll": 1.5,
            "python_end": SECTION - 0.3 - len(CODE) * TYPE_SECONDS - 1.5,
            "sort_start": 0.0,
            "sort_title": 0.15,
            "compare": 0.05,
            "swap": 0.4,
            "sort_done": SECTION - 0.15 - compares * 0.05 - swaps * 0.4,
            "font_start": 0.0,
            "font_title": 0.2,
            "font": 0.75,
            "font_done": 1.3,
            "font_clear": 0.35,
            "highlight_start": 0.6,
            "blur_resolve": 0.4,
            "mark": 0.65,
            "highlight_done": 3.0,
            "brand_clear": 0.35,
            "brand": 2.0,
            "install": 1.0,
        },
    )
