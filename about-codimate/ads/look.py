"""How the film looks: dark type on white, one blue, Inter throughout.

Importing this sets the canvas and the film's font, so every part of the ad
lays out the same way however it is entered: the film, its sound, its tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import codimate as cm

FONTS = Path(__file__).resolve().parent / "fonts"
INTER = str(FONTS / "Inter-Regular.otf")
INTER_MEDIUM = str(FONTS / "Inter-Medium.otf")
INTER_BOLD = str(FONTS / "Inter-Bold.otf")
CODE_FONT = "Menlo"

WHITE = "#ffffff"
INK = "#1d1d1f"
BLUE = "#0071e3"
YELLOW = "#ffd60a"
MUTED = "#86868b"
PALE = "#d2d2d7"

WIDTH, HEIGHT = 1920, 1080
CENTRE = WIDTH / 2

cm.canvas(WIDTH, HEIGHT)
cm.font(INTER)


# The opening words, big and centred; then a headline at the top of each section.
OPENING = (CENTRE, 540)
TOP = (CENTRE, 220)
HEADLINE = cm.TextPresetStyle(size=78, font=INTER_BOLD, fill=INK)


def _opening(fill):
    return cm.TextPresetStyle(size=164, fill=fill, distance=46)


# Every headline, by the section it opens. Each knows how it enters.
TITLES = {
    "code": cm.text.words_up("code_title", "Code.", style=_opening(INK), at=OPENING),
    "animated": cm.text.letters_up(
        "animated_title", "Animated.", style=_opening(BLUE), at=OPENING
    ),
    "python": cm.text.words_down(
        "python_title", "Write Python.", style=HEADLINE, at=TOP
    ),
    "sort": cm.text.words_left(
        "sort_title", "It moves for you.", style=HEADLINE, at=TOP
    ),
    "fonts": cm.text.words_right(
        "font_title", "Any font. Any language.", style=HEADLINE, at=TOP
    ),
    "highlight": cm.text.words_up_blur(
        "highlight_title", "Mark what matters.", style=HEADLINE, at=TOP
    ),
    "brand": cm.text.letters_down(
        "brand_title",
        "Codimate.",
        style=cm.TextPresetStyle(size=142, font=INTER_BOLD, fill=INK),
        at=(CENTRE, 470),
    ),
}


@dataclass(frozen=True)
class TextStyle:
    size: float
    y: float
    font: str = INTER
    color: str = INK
    x: float = CENTRE


def text(scene, key, value, style: TextStyle):
    """A line of text in one of the film's styles."""
    return scene.text(
        key, value, size=style.size, font=style.font, at=(style.x, style.y)
    ).fill(style.color)
