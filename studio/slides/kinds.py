"""The eight kinds of slide. Each is plain data: what it says, and the lines a
narrator speaks. A slide comes on in parts; each part arrives as its line
starts. ``*word*`` marks a word in the accent colour.

    Title("Thinking, Fast and Slow", by="Daniel Kahneman", say="...")
    Statement("Your mind runs on *two systems.*", say="...")
    Quote("Nothing in life is as important...", by="Daniel Kahneman", say="...")
    BigNumber("5¢", "the ball's real price", say="...")
    Compare(("System 1", "fast, automatic"), ("System 2", "slow, effortful"), say=[...])
    List("Takeaways", ["...", "..."], say=[...])
    Steps("The peak-end rule", ["...", "..."], say=[...])
    Question("How much is the ball?", "5 cents", say=["...", "..."])
"""

from __future__ import annotations

from dataclasses import dataclass, field

import codimate as cm

from .look import (
    ITEM,
    MARK,
    BODY,
    CENTRE,
    HEAD,
    HUGE,
    QUOTE,
    SMALL,
    STATEMENT,
    TITLE,
    WIDTH,
    Setting,
    face,
    height,
    write,
)


@dataclass(frozen=True)
class Part:
    """One piece of a slide that arrives together, and the line said with it."""

    draw: object  # draw(scene, key, theme, dy): dy is how far below its place
    say: str = ""
    moves: float = 0.0  # seconds it animates: then draw(..., dy, t), every frame
    alone: bool = False  # it redraws the whole slide: earlier parts stop drawing


def _lines(say, n):
    """``say`` as one line per part: a list as given, a string for the first."""
    if isinstance(say, (list, tuple)):
        return list(say) + [""] * (n - len(say))
    return [say] + [""] * (n - 1)


@dataclass(frozen=True)
class Title:
    title: str
    by: str = ""
    say: str = ""

    def parts(self):
        def draw(scene, key, theme, dy):
            top = CENTRE[1] - (height(self.title, TITLE) + 90) / 2 + TITLE.size / 2
            write(
                scene,
                key + ("title",),
                self.title,
                Setting(TITLE, theme),
                (CENTRE[0], top + dy),
            )
            below = top + height(self.title, TITLE) - TITLE.size / 2 + 60
            write(
                scene,
                key + ("by",),
                self.by,
                Setting(SMALL, theme),
                (CENTRE[0], below + dy),
            )

        return [Part(draw, self.say)]


@dataclass(frozen=True)
class Statement:
    text: str
    say: str = ""

    def parts(self):
        def draw(scene, key, theme, dy):
            top = CENTRE[1] - height(self.text, STATEMENT) / 2 + STATEMENT.size / 2
            write(
                scene, key, self.text, Setting(STATEMENT, theme), (CENTRE[0], top + dy)
            )

        return [Part(draw, self.say)]


@dataclass(frozen=True)
class Quote:
    text: str
    by: str = ""
    say: object = ""

    def _top(self):
        return CENTRE[1] - (height(self.text, QUOTE, 1400) + 120) / 2 + QUOTE.size / 2

    def parts(self):
        lines = _lines(self.say, 2)

        def quote(scene, key, theme, dy):
            top = self._top()
            write(
                scene,
                key + ("mark",),
                "“",
                Setting(MARK, theme),
                (CENTRE[0], top - 150 + dy),
            )
            write(
                scene,
                key + ("text",),
                self.text,
                Setting(QUOTE, theme, 1400),
                (CENTRE[0], top + dy),
            )

        def by(scene, key, theme, dy):
            below = self._top() + height(self.text, QUOTE, 1400) - QUOTE.size / 2 + 70
            write(
                scene,
                key + ("by",),
                f"— {self.by}",
                Setting(SMALL, theme),
                (CENTRE[0], below + dy),
            )

        return [Part(quote, lines[0]), Part(by, lines[1])]


@dataclass(frozen=True)
class BigNumber:
    number: str
    caption: str = ""
    say: object = ""

    def parts(self):
        lines = _lines(self.say, 2)

        def number(scene, key, theme, dy):
            write(
                scene,
                key + ("n",),
                f"*{self.number}*",
                Setting(HUGE, theme),
                (CENTRE[0], 470 + dy),
            )

        def caption(scene, key, theme, dy):
            write(
                scene,
                key + ("c",),
                self.caption,
                Setting(BODY, theme, 1200),
                (CENTRE[0], 650 + dy),
            )

        return [Part(number, lines[0]), Part(caption, lines[1])]


@dataclass(frozen=True)
class Compare:
    left: tuple  # (head, body)
    right: tuple
    title: str = ""
    say: object = ""

    def parts(self):
        lines = _lines(self.say, 3 if self.title else 2)
        parts = []
        if self.title:

            def title(scene, key, theme, dy):
                write(
                    scene,
                    key + ("t",),
                    self.title,
                    Setting(HEAD, theme),
                    (CENTRE[0], 330 + dy),
                )

            parts.append(Part(title, lines.pop(0)))
        top = 520 if self.title else 470
        for side, (head, body), x in (("l", self.left, 560), ("r", self.right, 1360)):
            parts.append(Part(_column(head, body, (x, top), side), lines.pop(0)))
        return parts


def _column(head, body, at, side):
    """One side of a Compare: its head over its body, centred on ``at``."""
    x, top = at

    def draw(scene, key, theme, dy):
        write(scene, key + (side, "h"), head, Setting(HEAD, theme, 640), (x, top + dy))
        write(
            scene,
            key + (side, "b"),
            body,
            Setting(BODY, theme, 640),
            (x, top + 110 + dy),
        )
        if side == "r":  # the line between them, once both are there
            bar = scene.rect(key + ("divider",), w=2, h=300, at=(WIDTH / 2, top + 100))
            bar.fill(theme.line)

    return draw


@dataclass(frozen=True)
class List:
    title: str
    items: list = field(default_factory=list)
    say: object = ""
    numbered: bool = False

    def parts(self):
        lines = _lines(self.say, len(self.items) + 1)
        widest = max(
            cm.measure(i.replace("*", ""), ITEM.size, face(ITEM.font))[0]
            for i in self.items
        )
        left = (WIDTH - (widest + 90)) / 2  # the block centred, marks and all
        top = CENTRE[1] - (130 + len(self.items) * 110) / 2 + HEAD.size / 2

        def title(scene, key, theme, dy):
            setting = Setting(HEAD, theme, align="left")
            write(scene, key + ("t",), self.title, setting, (left, top + dy))

        parts = [Part(title, lines[0])]
        for k, item in enumerate(self.items):
            mark = f"*{k + 1}*" if self.numbered else "*—*"
            at = (left, top + 130 + k * 110)
            parts.append(Part(_row(mark, item, at), lines[k + 1]))
        return parts


def _row(mark, item, at):
    """One row of a List: its mark, then its words, from ``at``'s left edge."""
    left, y = at

    def draw(scene, key, theme, dy):
        write(scene, key + ("m",), mark, Setting(HEAD, theme), (left + 24, y + dy))
        item_setting = Setting(ITEM, theme, 1300, "left")
        write(scene, key + ("i",), item, item_setting, (left + 90, y + dy))

    return draw


def Steps(title, steps, say=""):
    """A List with numbers: a sequence, in order."""
    return List(title, steps, say, numbered=True)


@dataclass(frozen=True)
class Question:
    question: str
    answer: str
    say: object = ""
    think: float = 2.5  # seconds of silence before the answer

    def parts(self):
        lines = _lines(self.say, 2)

        def ask(scene, key, theme, dy):
            top = 400 - height(self.question, HEAD, 1400) / 2 + HEAD.size / 2
            write(
                scene,
                key + ("q",),
                self.question,
                Setting(HEAD, theme, 1400),
                (CENTRE[0], top + dy),
            )

        def answer(scene, key, theme, dy):
            write(
                scene,
                key + ("a",),
                f"*{self.answer}*",
                Setting(TITLE, theme),
                (CENTRE[0], 720 + dy),
            )

        return [Part(ask, lines[0]), Part(answer, lines[1])]
