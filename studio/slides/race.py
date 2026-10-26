"""A race: one input, two models, side by side, on a running clock. The fast
lane answers with typed fields and their probabilities; the slow lane types its
answer out token by token. Both finish when their ``seconds`` say.

    Race(
        "Same ticket, two models",
        "I was charged twice this month. Fix it, or I'm cancelling.",
        fast=("Jev", 0.3, [("category", "billing", 0.94), ...]),
        slow=("GPT", 3.0, '{"category": "billing", ...}'),
        note="Illustrative. Times as TypeSafe reports them.",
        say=["...", "..."],
    )
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import codimate as cm

from .code import MONO, PANEL, SYNTAX, spans
from .look import BOLD, CENTRE, HEAD, MEDIUM, SMALL, Setting, Type, theme_name, write

VALUE = Type(44, BOLD)
CLOCK = Type(40, MEDIUM, "muted")
CODE = 32  # the slow lane's answer, in points
TOP, BOTTOM = 380, 830  # the lanes
ROW = 80  # between the fast lane's fields
LINE = 46  # between the slow lane's lines
TICKET = Type(44, MEDIUM, "ink")
LANES = (560, 1360)  # their centres, as Compare's columns
WIDE = 720
GROW = 0.3  # seconds a probability bar takes to fill
_TOKEN = re.compile(r'"[^"]*"|\w+|\S')


def _dark(theme) -> str:
    return theme_name(theme)


def _pairs(text: str) -> dict:
    """Each closing bracket's place in ``text``, to its opening bracket's."""
    pairs, open_ = {}, []
    for at, char in enumerate(text):
        if char in "{[(":
            open_.append(at)
        elif char in "}])" and open_:
            pairs[at] = open_.pop()
    return pairs


def _clock(t: float, seconds: float) -> tuple:
    """A lane's clock at ``t``: its text, and its type (ink once it stops)."""
    done = t >= seconds
    text = f"{min(t, seconds):.1f} s"
    return text, Type(CLOCK.size, CLOCK.font, "ink" if done else "muted")


@dataclass(frozen=True)
class Race:
    title: str
    ticket: str
    fast: tuple  # (name, seconds, [(field, value, probability), ...])
    slow: tuple  # (name, seconds, the answer as text)
    note: str = ""
    say: object = ""

    def parts(self):
        from .kinds import Part, _lines

        lines = _lines(self.say, 2)

        def ticket(scene, key, theme, dy):
            write(
                scene,
                key + ("t",),
                self.title,
                Setting(HEAD, theme),
                (CENTRE[0], 150 + dy),
            )
            card = scene.rect(key + ("card",), w=1500, h=110, at=(CENTRE[0], 270 + dy))
            card.fill(PANEL[_dark(theme)], edge=theme.line, edge_w=2).round(22)
            text = f"“{self.ticket}”"
            write(
                scene,
                key + ("q",),
                text,
                Setting(TICKET, theme, 1400),
                (CENTRE[0], 270 + dy),
            )

        def race(scene, key, theme, dy, t):
            for side, (name, seconds, _), x in zip("fs", (self.fast, self.slow), LANES):
                left, right = x - WIDE / 2, x + WIDE / 2
                # the clock: a new shape for each reading, so it ticks by cuts
                text, kind = _clock(t, seconds)
                wide = cm.measure(text, kind.size, kind.font)[0]
                at = (right - 50 - wide / 2, TOP + 55 + dy)
                write(scene, key + (side, text), text, Setting(kind, theme), at)
                lane = scene.rect(
                    key + (side, "lane"),
                    w=WIDE,
                    h=BOTTOM - TOP,
                    at=(x, (TOP + BOTTOM) / 2 + dy),
                )
                lane.fill(PANEL[_dark(theme)], edge=theme.line, edge_w=2).round(22)
                head = Setting(HEAD, theme, WIDE, align="left")
                write(scene, key + (side, "h"), name, head, (left + 50, TOP + 55 + dy))
            self._fast(scene, key + ("f",), theme, dy, t)
            self._slow(scene, key + ("s",), theme, dy, t)
            if self.note and t >= self.slow[1]:
                write(
                    scene,
                    key + ("n",),
                    self.note,
                    Setting(SMALL, theme),
                    (CENTRE[0], 885 + dy),
                )

        moves = self.slow[1] + 0.6
        return [Part(ticket, lines[0]), Part(race, lines[1], moves=moves)]

    def _fast(self, scene, key, theme, dy, t):
        _, seconds, fields = self.fast
        left = LANES[0] - WIDE / 2
        if t < seconds:
            return
        grown = min((t - seconds) / GROW, 1.0)
        grown = 1 - (1 - grown) ** 3
        for row, (field, value, chance) in enumerate(fields):
            y = TOP + 150 + row * ROW + dy
            label = Setting(SMALL, theme, 300, align="left")
            write(scene, key + (row, "f"), field, label, (left + 50, y))
            write(
                scene,
                key + (row, "v"),
                value,
                Setting(VALUE, theme, 300, align="left"),
                (left + 260, y),
            )
            track = scene.rect(key + (row, "track"), w=120, h=10, at=(left + 530, y))
            track.fill(theme.line).round(5).on(layer=1)
            if grown > 0:
                width = 120 * chance * grown
                bar = scene.rect(
                    key + (row, "bar"), w=width, h=10, at=(left + 470 + width / 2, y)
                )
                bar.fill(theme.accent).round(5).on(layer=2)
            percent = Setting(Type(36, MEDIUM, "accent"), theme, 200, align="left")
            write(scene, key + (row, "p"), f"{chance:.0%}", percent, (left + 610, y))
        write(
            scene,
            key + ("ready",),
            "Ready to use.",
            Setting(SMALL, theme),
            (LANES[0], BOTTOM - 50 + dy),
        )

    def _slow(self, scene, key, theme, dy, t):
        _, seconds, answer = self.slow
        left = LANES[1] - WIDE / 2
        ends = [m.end() for m in _TOKEN.finditer(answer)]  # where each token ends
        said = min(int(len(ends) * t / seconds), len(ends))
        shown = ends[said - 1] if said else 0  # characters typed so far
        colours = SYNTAX[_dark(theme)]
        advance = cm.measure("0" * 20, CODE, MONO)[0] / 20
        closes = _pairs(answer)  # a bracket closes as soon as it opens, as in an editor
        at = 0
        for row, line in enumerate(answer.split("\n")):
            col = 0
            for text, kind in spans(line, "json"):
                for char in text:
                    typed = at < shown or closes.get(at, shown) < shown
                    if typed and not char.isspace():
                        centre = (
                            left + 50 + (col + 0.5) * advance,
                            TOP + 140 + row * LINE + dy,
                        )
                        shape = scene.text(
                            key + ("c", row, col), char, size=CODE, font=MONO, at=centre
                        )
                        shape.fill(colours.get(kind, theme.ink))
                    col += 1
                    at += 1
            at += 1  # the newline
        if t >= seconds:
            write(
                scene,
                key + ("then",),
                "Now parse it, and check it.",
                Setting(SMALL, theme),
                (LANES[1], BOTTOM - 50 + dy),
            )
