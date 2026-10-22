"""How a deck looks: Inter on white or black, one accent, an Apple-keynote type
scale, and words laid out by measure so every line sits where it should.

A Japanese deck (``use("ja")``) is set in Noto Sans JP, without spaces: its text
breaks between characters, never inside a run of Latin letters or digits, and never
before closing punctuation."""

from __future__ import annotations

from dataclasses import dataclass

import re

import codimate as cm

from .. import FONTS

REGULAR = str(FONTS / "Inter-Regular.otf")
MEDIUM = str(FONTS / "Inter-Medium.otf")
BOLD = str(FONTS / "Inter-Bold.otf")
JAPANESE_FONTS = {
    REGULAR: str(FONTS / "NotoSansJP-Regular.otf"),
    MEDIUM: str(FONTS / "NotoSansJP-Medium.otf"),
    BOLD: str(FONTS / "NotoSansJP-Bold.otf"),
}
_faces: dict = {}  # the fonts the deck's language swaps in
TOKEN = re.compile(r"\*|[A-Za-z0-9%#_+\-/.,:']+|\s|.")  # Japanese text, piece by piece
NO_START = set("、。，．・：；？！ー…」』）〕］｝〉》%)]}!?.,")  # never begins a line


def use(language: str) -> None:
    """Set the deck's language: "ja" is Noto Sans JP and no spaces, else Inter."""
    _faces.clear()
    if language == "ja":
        _faces.update(JAPANESE_FONTS)


def face(font: str) -> str:
    """The font to set text in, for the deck's language."""
    return _faces.get(font, font)


def gap() -> str:
    """What goes between words: a space, or nothing in Japanese."""
    return "" if _faces else " "

WIDTH, HEIGHT = 1920, 1080
CENTRE = (WIDTH / 2, HEIGHT / 2)
MEASURE = 1500  # the widest a line of text may run


@dataclass(frozen=True)
class Theme:
    page: str
    ink: str
    accent: str
    muted: str
    line: str


THEMES = {
    "light": Theme("#ffffff", "#1d1d1f", "#0071e3", "#86868b", "#d2d2d7"),
    "dark": Theme("#000000", "#f5f5f7", "#2997ff", "#86868b", "#424245"),
}


@dataclass(frozen=True)
class Type:
    size: float
    font: str = BOLD
    role: str = "ink"
    leading: float = 1.18


# The scale, largest first. Big and few: a slide says one thing.
HUGE = Type(220)  # a big number
TITLE = Type(112)
STATEMENT = Type(92)
HEAD = Type(68)
QUOTE = Type(60, MEDIUM, leading=1.3)
MARK = Type(200, BOLD, "accent", leading=1.0)  # a quotation's opening mark
ITEM = Type(52, MEDIUM, leading=1.3)  # a point on a list
BODY = Type(44, MEDIUM, "muted", leading=1.35)
SMALL = Type(36, MEDIUM, "muted")


def runs(text: str) -> list:
    """``text`` as ``(word, accented)`` pairs: ``*two systems*`` is accented.
    In Japanese a "word" is a character, or a run of Latin letters and digits.
    Stars mark an accent only in pairs: a lone one, as in ``int *p``, is text."""
    out, accent = [], False
    if (text.count("*") - text.count("\\*")) % 2:
        pieces = TOKEN.findall(text.strip()) if _faces else text.split()
        return [(piece, False) for piece in pieces]
    if _faces:
        for piece in TOKEN.findall(text.strip()):
            if piece == "*":
                accent = not accent
            else:
                out.append((piece, accent))
        return out
    for word in text.split():
        start = word.startswith("*")
        end = word.rstrip(".,;:!?\"'”)").endswith("*")
        bare = word.replace("*", "")
        accent = accent or start
        out.append((bare, accent))
        if end:
            accent = False
    return out


def wrap(text: str, kind: Type, width: float = MEASURE) -> list:
    """Lines of ``(word, accented)`` pairs, no line wider than ``width``."""
    lines, line = [], []
    for word, accent in runs(text):
        trial = gap().join(w for w, _ in line + [(word, accent)])
        wide = cm.measure(trial, kind.size, face(kind.font))[0] > width
        if line and wide and word not in NO_START:
            lines.append(line)
            line = []
        if line or not word.isspace():  # a line never starts with a space
            line.append((word, accent))
    if line:
        lines.append(line)
    return _balance(lines, kind, width)


def _balance(lines, kind, width):
    """Move words down until the last line is no lonely word: "the / ball?"
    reads badly, "How much is / the ball?" does not."""

    def wide(line):
        return cm.measure(gap().join(w for w, _ in line), kind.size, face(kind.font))[0]

    while len(lines) > 1 and len(lines[-1]) < 2 and len(lines[-2]) > 2 and not _faces:
        moved = lines[-2][-1:] + lines[-1]
        if wide(moved) > width:
            break
        lines = lines[:-2] + [lines[-2][:-1], moved]
    return lines


def height(text: str, kind: Type, width: float = MEASURE) -> float:
    return len(wrap(text, kind, width)) * kind.size * kind.leading


@dataclass(frozen=True)
class Setting:
    """How a piece of text is set: its type, theme, measure and alignment."""

    kind: Type
    theme: Theme
    width: float = MEASURE
    align: str = "centre"


def write(scene, key, text: str, setting: Setting, at):
    """``text`` set as ``setting`` says, its first line's centre at ``at`` (or
    its left edge, when aligned left), wrapped to the measure, accented words in
    the accent colour. Each word is its own shape, so a phrase can be coloured."""
    kind, theme = setting.kind, setting.theme
    x, y = at
    font = face(kind.font)
    pair = cm.measure("a a", kind.size, font)[0]
    space = 0.0 if _faces else pair - cm.measure("aa", kind.size, font)[0]
    for row, line in enumerate(wrap(text, kind, setting.width)):
        widths = [cm.measure(word, kind.size, font)[0] for word, _ in line]
        total = sum(widths) + space * (len(line) - 1)
        left = x - total / 2 if setting.align == "centre" else x
        for k, ((word, accent), w) in enumerate(zip(line, widths)):
            colour = theme.accent if accent else getattr(theme, kind.role)
            centre = (left + w / 2, y + row * kind.size * kind.leading)
            shape = scene.text(
                (key, row, k), word, size=kind.size, font=font, at=centre
            )
            shape.fill(colour)
            left += w + space
