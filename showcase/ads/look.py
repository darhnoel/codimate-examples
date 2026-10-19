"""How the film looks: one accent colour, Inter throughout, light or dark.

Importing this sets the canvas and the film's font, so every part of the ad
lays out the same way however it is entered: the film, its sound, its tests.
``use("dark")`` switches the palette; everything reads it as it draws.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path

import codimate as cm

FONTS = Path(__file__).resolve().parents[2] / "studio" / "fonts"
INTER = str(FONTS / "Inter-Regular.otf")
INTER_MEDIUM = str(FONTS / "Inter-Medium.otf")
INTER_BOLD = str(FONTS / "Inter-Bold.otf")
CODE_FONT = "Menlo"


@dataclass(frozen=True)
class Palette:
    page: str  # the background
    ink: str  # type, bars, the ball
    accent: str  # "Animated." and the install line
    marker: str  # the highlighter
    muted: str  # labels, a bar being compared
    line: str  # the floor under the ball and the bars


LIGHT = Palette("#ffffff", "#1d1d1f", "#0071e3", "#ffd60a", "#86868b", "#d2d2d7")
DARK = Palette("#000000", "#f5f5f7", "#2997ff", "#ffd60a", "#86868b", "#424245")
THEMES = {"light": LIGHT, "dark": DARK}
palette = LIGHT


def use(theme: str) -> None:
    """Draw the film in ``theme``: ``"light"`` (the default) or ``"dark"``."""
    global palette
    palette = THEMES[theme]


WIDTH, HEIGHT = 1920, 1080
CENTRE = WIDTH / 2

cm.canvas(WIDTH, HEIGHT)
cm.font(INTER)


# The opening words, big and centred; then a headline at the top of each section.
OPENING = (CENTRE, 540)
TOP = (CENTRE, 220)


def titles() -> dict:
    """Every headline, by the section it opens, in the current palette."""
    return _titles(palette)


@cache
def _titles(colours: Palette) -> dict:
    def opening(fill):
        return cm.TextPresetStyle(size=164, fill=fill, distance=46)

    headline = cm.TextPresetStyle(size=78, font=INTER_BOLD, fill=colours.ink)
    brand = cm.TextPresetStyle(size=142, font=INTER_BOLD, fill=colours.ink)
    return {
        "code": cm.text.words_up(
            "code_title", "Code.", style=opening(colours.ink), at=OPENING
        ),
        "animated": cm.text.letters_up(
            "animated_title", "Animated.", style=opening(colours.accent), at=OPENING
        ),
        "python": cm.text.words_down(
            "python_title", "Write Python.", style=headline, at=TOP
        ),
        "sort": cm.text.words_left(
            "sort_title", "It moves for you.", style=headline, at=TOP
        ),
        "fonts": cm.text.words_right(
            "font_title", "Any font. Any language.", style=headline, at=TOP
        ),
        "highlight": cm.text.words_up_blur(
            "highlight_title", "Mark what matters.", style=headline, at=TOP
        ),
        "brand": cm.text.letters_down(
            "brand_title", "Codimate.", style=brand, at=(CENTRE, 470)
        ),
    }


@dataclass(frozen=True)
class TextStyle:
    size: float
    y: float
    font: str = INTER
    color: str = None  # the palette's ink
    x: float = CENTRE


def text(scene, key, value, style: TextStyle):
    """A line of text in one of the film's styles."""
    return scene.text(
        key, value, size=style.size, font=style.font, at=(style.x, style.y)
    ).fill(style.color or palette.ink)
