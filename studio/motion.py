"""Motion-graphics templates for short promos, on a musical grid.

    from studio import motion

    timing = motion.BeatTiming(bpm=120)          # emit("word", beats=1)
    hook = motion.Headline("hook", "Type how it sounds", look, at=(960, 540))
    hook.draw(scene, shown=2)                    # the first two words are in

Every template draws the state it is handed and keeps none of its own, so a
film stays a deterministic function of time: the story sets the state, the
template draws it, and Codimate moves between the drawings.

- ``BeatTiming``: event lengths counted in beats, so every cut is on the grid.
- ``Headline``: a line whose words rise in one at a time, one per beat.
- ``ime_field``: an input box, typed text, a caret, and a candidate row.
- ``scan_list``: rows of options, a scan line, and the one picked.
- ``orbit``: cards on a flat ellipse, depth suggested by size and layer only.
- ``iris``: a circle growing from a point until it covers the frame.
- ``curtain``: one colour over the whole frame, for a fade out.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import codimate as cm


class BeatTiming(cm.Timing):
    """Event lengths in beats: ``emit("key", beats=0.5)`` lasts half a beat.
    An event with no ``beats`` is a cut. No opening and no final hold, so the
    film lasts exactly as long as its beats add up to."""

    def __init__(self, bpm: float):
        super().__init__(default=0.0, opening=0.0, final_hold=0.0)
        self.beat = 60.0 / bpm

    def for_event(self, event) -> float:
        return float(event.data.get("beats", 0.0)) * self.beat


@dataclass(frozen=True)
class Look:
    """One kind of text: its font, size and colour."""

    font: str
    size: float
    fill: str


def label(scene, key, words: str, look: Look, at: tuple):
    """Words centred on ``at``, in ``look``."""
    handle = scene.text(key, words, size=look.size, font=look.font, at=at)
    return handle.fill(look.fill)


def width(words: str, look: Look) -> float:
    return cm.measure(words, look.size, look.font)[0] if words else 0.0


class Headline:
    """A line of words centred on ``at``. Each word is its own text preset, so
    each can rise on its own beat: ``draw(scene, shown=k)`` shows the first
    ``k``. Pass ``rules()`` to the film's motion so the words rise."""

    def __init__(self, name: str, words: str, look: Look, at: tuple):
        style = cm.TextPresetStyle(size=look.size, font=look.font, fill=look.fill)
        gap = width("a a", look) - width("aa", look)
        sizes = [width(word, look) for word in words.split()]
        x = at[0] - (sum(sizes) + gap * (len(sizes) - 1)) / 2
        self.centres, self.presets = [], []
        for k, (word, size) in enumerate(zip(words.split(), sizes)):
            centre = (x + size / 2, at[1])
            self.centres.append(centre)
            self.presets.append(
                cm.text.words_up(f"{name}{k}", word, style=style, at=centre)
            )
            x += size + gap

    def draw(self, scene, shown: int) -> None:
        for k, preset in enumerate(self.presets):
            preset.draw(scene, state="shown" if k < shown else "hidden")

    def rules(self) -> list:
        return [rule for preset in self.presets for rule in preset.rules(stagger=0)]


@dataclass(frozen=True)
class Field:
    """An input field's state. ``box`` is (centre x, centre y, width, height);
    ``picked`` is the chosen candidate's index, or -1 for none."""

    box: tuple
    typed: str = ""
    candidates: tuple = ()
    picked: int = -1


@dataclass(frozen=True)
class FieldStyle:
    """How a field is drawn: the typed text, the candidates, and the colours
    of the box, the caret and a picked candidate (``page`` is its words)."""

    typed: Look
    candidate: Look
    accent: str
    page: str


def chip_centre(field: Field, style: FieldStyle, k: int) -> tuple:
    """Where candidate ``k`` of ``field`` sits: for a wipe that opens from it."""
    x, y, w, h = field.box
    cx = x - w / 2 + h / 4
    for j, words in enumerate(field.candidates[:k]):
        cx += _chip_width(words, j, style) + 20
    row_y = y + h / 2 + 34 + style.candidate.size
    return (cx + _chip_width(field.candidates[k], k, style) / 2, row_y)


def _chip_width(words: str, k: int, style: FieldStyle) -> float:
    return width(f"{k + 1}  {words}", style.candidate) + 44


def ime_field(scene, key, field: Field, style: FieldStyle) -> None:
    """The box; the typed text with a caret after it; then the candidates in
    a row under it, numbered as an input method numbers them. A picked
    candidate is filled with the accent and its words turn to the page."""
    x, y, w, h = field.box
    box = scene.rect(key + ("box",), w=w, h=h, at=(x, y)).round(h / 2)
    box.fill(style.page, edge=style.typed.fill, edge_w=3)
    left = x - w / 2 + h / 2
    typed = width(field.typed, style.typed)
    if field.typed:
        label(scene, key + ("typed",), field.typed, style.typed, (left + typed / 2, y))
    caret_x = left + typed + 8
    reach = style.typed.size * 0.55
    caret = scene.line(
        key + ("caret",), start=(caret_x, y - reach), end=(caret_x, y + reach), w=3
    )
    caret.fill(style.accent)
    on_accent = Look(style.candidate.font, style.candidate.size, style.page)
    for k, words in enumerate(field.candidates):
        at = chip_centre(field, style, k)
        picked = k == field.picked
        chip = scene.rect(
            key + ("chip", k),
            w=_chip_width(words, k, style),
            h=style.candidate.size * 1.8,
            at=at,
        )
        chip.round(16).fill(
            style.accent if picked else style.page, edge=style.accent, edge_w=2
        )
        look = on_accent if picked else style.candidate
        label(scene, key + ("chip", k, "words"), f"{k + 1}  {words}", look, at)


@dataclass(frozen=True)
class ListStyle:
    """Rows centred on ``at`` (the first row), ``gap`` apart, in ``row``; the
    scan line and a picked row in ``accent``; ``span`` is the line's width."""

    row: Look
    accent: str
    at: tuple
    gap: float
    span: float


@dataclass(frozen=True)
class Scan:
    """A list's state: its ``rows``; where the scan line is, in rows (0 is on
    the first, and it may sit between rows), or None; and the picked row."""

    rows: tuple
    line: float | None = None
    picked: int = -1


def scan_list(scene, key, scan: Scan, style: ListStyle) -> None:
    """Rows of options, a scan line across them, the picked row in accent."""
    rows, picked = scan.rows, scan.picked
    x, y = style.at
    for k, words in enumerate(rows):
        look = style.row
        if k == picked:
            look = Look(look.font, look.size, style.accent)
        label(scene, key + ("row", k), words, look, (x, y + k * style.gap))
    if scan.line is not None:
        line_y = y + scan.line * style.gap
        line = scene.line(
            key + ("scan",),
            start=(x - style.span / 2, line_y),
            end=(x + style.span / 2, line_y),
            w=4,
        )
        line.fill(style.accent).on(layer=2)


def orbit(count: int, turn: float, centre: tuple, radius: tuple) -> list:
    """Where ``count`` cards sit on a flat ellipse turned by ``turn`` steps:
    ``[(x, y, scale, layer), ...]``. Card 0 is in front at ``turn=0``. The
    depth is suggested by size and drawing order only; it is not 3D."""
    cx, cy = centre
    rx, ry = radius
    spots = []
    for k in range(count):
        angle = 2 * math.pi * (k - turn) / count
        depth = math.cos(angle)  # 1 in front, -1 at the back
        spots.append((
            cx + rx * math.sin(angle),
            cy + ry * depth,
            0.62 + 0.38 * (depth + 1) / 2,
            round(5 + 4 * depth),
        ))
    return spots


def iris(scene, key, at: tuple, radius: float, fill: str):
    """A circle of ``radius`` at ``at``: grow it from a few pixels to past the
    frame's corners for a wipe that opens from one point."""
    return scene.circle(key, r=max(radius, 0.5), at=at).fill(fill).on(layer=8)


def curtain(scene, key, fill: str, opacity: float, frame=(1920, 1080)) -> None:
    """``fill`` over the whole frame at ``opacity``, above everything."""
    w, h = frame
    shade = scene.rect(key, w=w, h=h, at=(w / 2, h / 2)).fill(fill)
    shade.on(layer=9, opacity=opacity)
