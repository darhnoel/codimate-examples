"""What each moment looks like: one drawing per section, and ``view`` picking
the one the story is in.

``places`` reports where the moving things sit, so the sound can follow them.
"""

from __future__ import annotations

import codimate as cm

import look
import sound
from look import (
    CENTRE,
    CODE_FONT,
    INTER,
    INTER_BOLD,
    INTER_MEDIUM,
    WIDTH,
    TextStyle,
    text,
    titles,
)
from story import CODE, Film

FLOOR = 800
CODE_LEFT = 430
BALL_PATH = (330, 1590)
FONT_SAMPLES = (  # (text, font, label, size)
    ("Codimate", "Helvetica Neue", "Helvetica Neue", 148),
    ("Codimate", "Georgia", "Georgia", 148),
    ("Codimate", "Menlo", "Menlo", 144),
    ("សួស្តី", INTER, "Khmer", 150),
    ("你好", INTER, "Chinese", 170),
)
SENTENCE = ("See what ", "changed.")


def view(frame):
    film = frame.state
    scene = cm.Scene()
    scene.rect("background", w=WIDTH, h=1080, at=(CENTRE, 540)).fill(look.palette.page)
    for name, title in titles().items():
        if film.titles[name] != "gone":
            title.draw(scene, state=film.titles[name])
    section = SECTIONS.get(film.phase)
    if section:
        section(scene, film)
    return scene


def _python(scene, film):
    start, end = BALL_PATH
    track = scene.line("track", start=(start, FLOOR), end=(end, FLOOR), w=2)
    track.fill(look.palette.line)
    lines = film.typing.split("\n")
    for index, y in enumerate((470, 560, 650)):
        if index < len(lines) and lines[index]:
            width, _ = cm.measure(lines[index], size=42, font=CODE_FONT)
            style = TextStyle(size=42, y=y, font=CODE_FONT, x=CODE_LEFT + width / 2)
            text(scene, ("code", index), lines[index], style)
    if film.ball_visible:
        ball = scene.circle("ball", r=34, at=(film.ball_x, FLOOR))
        ball.fill(look.palette.ink).on(layer=1)


def _bar_slots(bars):
    return cm.row(bars, gap=45, size=(140, 400), at=cm.at(bottom=FLOOR))


def _sort(scene, film):
    colours = look.palette
    scene.line("baseline", start=(475, FLOOR), end=(1445, FLOOR), w=2).fill(
        colours.line
    )
    for slot, item in _bar_slots(film.bars):
        color = colours.muted if item.id in film.comparing else colours.ink
        scene.rect(
            ("bar", item.id), w=116, h=item.value * 66, at=cm.at(x=slot.x, bottom=FLOOR)
        ).fill(color)
        style = TextStyle(size=32, y=855, font=INTER_MEDIUM, x=slot.x)
        text(scene, ("value", item.id), str(item.value), style)


def _fonts(scene, film):
    sample, font, label, size = FONT_SAMPLES[film.font_index]
    shown = 1 if film.font_sample_visible else 0
    text(scene, "sample", sample, TextStyle(size=size, y=535, font=font)).on(
        opacity=shown
    )
    muted = look.palette.muted
    label_style = TextStyle(size=30, y=680, font=INTER_MEDIUM, color=muted)
    text(scene, "font_label", label, label_style).on(opacity=shown)


def _sentence():
    """The highlight sentence's layout: (left edge, prefix width, word width)."""
    prefix, word = SENTENCE
    prefix_width, _ = cm.measure(prefix, size=86, font=INTER_MEDIUM)
    word_width, _ = cm.measure(word, size=86, font=INTER_BOLD)
    return CENTRE - (prefix_width + word_width) / 2, prefix_width, word_width


def _highlight(scene, film):
    prefix, word = SENTENCE
    left, prefix_width, word_width = _sentence()
    style = TextStyle(size=86, y=550, font=INTER_MEDIUM, x=left + prefix_width / 2)
    text(scene, "sentence_prefix", prefix, style)
    at = (left + prefix_width + word_width / 2, 550)
    band, words = scene.highlight("key_word", word, size=86, font=INTER_BOLD, at=at)
    band.fill(look.palette.marker).write(reveal=film.marker_reveal)
    words.fill(look.palette.ink)  # their colour when the marker is off them


def _brand(scene, film):
    if film.show_install:
        accent = look.palette.accent
        style = TextStyle(size=38, y=610, font=INTER_MEDIUM, color=accent)
        text(scene, "install", "pip install codimate", style)


SECTIONS = {
    "python": _python,
    "sort": _sort,
    "fonts": _fonts,
    "highlight": _highlight,
    "brand": _brand,
}


def places() -> sound.Places:
    """Where each sound's source sits on screen."""
    bars = Film().bars
    left, prefix_width, word_width = _sentence()
    return sound.Places(
        width=WIDTH,
        code_left=CODE_LEFT,
        ball=BALL_PATH,
        bar_xs=tuple(slot.x for slot, _ in _bar_slots(bars)),
        bars=tuple(item.value for item in bars),
        marker=(left + prefix_width, left + prefix_width + word_width),
        code=CODE,
        animated=titles()["animated"].content,
    )
