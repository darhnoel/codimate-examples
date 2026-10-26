"""Code on a slide: a snippet on a panel, coloured the way Xcode colours it, in
the deck's theme. Python, Java and C are known; anything else is plain.

    Code("Classitis", JAVA_SNIPPET, language="java", caption="...", say=[...])
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import codimate as cm

from .look import CENTRE, HEAD, SMALL, Setting, height, theme_name, write

MONO = "Menlo"
KEYWORDS = {
    "js": set(
        "function const let var return for if else new import export from "
        "true false null".split()
    ),
    "python": set(
        "and as def class else for from if import in is not or return with "
        "while try except None True False lambda yield pass raise".split()
    ),
    "java": set(
        "new public private protected static final class void int long boolean "
        "return if else for while try catch throw throws import package this null "
        "true false".split()
    ),
    "c": set("int char void return if else for while struct const sizeof".split()),
}
SYNTAX = {  # Xcode, Default (Light) and Default (Dark)
    "light": {
        "keyword": "#9b2393",
        "type": "#3900a0",
        "call": "#326d74",
        "string": "#c41a16",
        "number": "#1c00cf",
        "comment": "#5d6c79",
    },
    "dark": {
        "keyword": "#fc5fa3",
        "type": "#d0a8ff",
        "call": "#67b7a4",
        "string": "#fc6a5d",
        "number": "#d0bf69",
        "comment": "#6c7986",
    },
}
PANEL = {"light": "#f5f5f7", "dark": "#1c1c1e"}
_TOKEN = re.compile(
    r'(?P<comment>#.*|//.*)|(?P<string>"[^"]*"?)|(?P<number>\b\d+\b)'
    r"|(?P<word>[A-Za-z_]\w*)"
)


def spans(line: str, language: str) -> list:
    """One line as ``(text, kind)`` spans; kind is a SYNTAX key or ``ink``."""
    out, at = [], 0
    for match in _TOKEN.finditer(line):
        out.append((line[at : match.start()], "ink"))
        kind = match.lastgroup
        if kind == "word":
            word = match.group()
            after = line[match.end() :].lstrip()
            if word in KEYWORDS.get(language, ()):
                kind = "keyword"
            elif word[0].isupper():
                kind = "type"
            elif after.startswith("("):
                kind = "call"
            else:
                kind = "ink"
        out.append((match.group(), kind))
        at = match.end()
    out.append((line[at:], "ink"))
    return [span for span in out if span[0]]


@dataclass(frozen=True)
class Code:
    title: str
    code: str
    language: str = "python"
    caption: str = ""
    say: object = ""

    def _size(self) -> float:
        """As big as fits: 1400 wide, and title, panel and caption in 880 tall,
        so a long program never runs down into the captions at y=975."""
        rows = self.code.split("\n")
        widest = max(len(line) for line in rows)
        caption = height(self.caption, SMALL, 1300) + 50 if self.caption else 0
        tallest = (880 - 130 - 80 - caption) / (1.6 * len(rows))
        return min(40.0, 1400 / (0.6 * widest), tallest)

    def _box(self):
        """The panel: (left, top, right, bottom), centred on the slide."""
        size = self._size()
        rows = self.code.split("\n")
        width = max(len(line) for line in rows) * 0.6 * size + 120
        tall = len(rows) * size * 1.6 + 80
        caption = height(self.caption, SMALL, 1300) + 50 if self.caption else 0
        block = tall + caption + 130
        top = min(CENTRE[1] - block / 2, 930 - block) + 130
        return CENTRE[0] - width / 2, top, CENTRE[0] + width / 2, top + tall

    def parts(self):
        from .kinds import Part, _lines

        lines = _lines(self.say, 2 if self.caption else 1)

        def panel(scene, key, theme, dy):
            left, top, right, bottom = self._box()
            write(
                scene,
                key + ("t",),
                self.title,
                Setting(HEAD, theme),
                (CENTRE[0], top - 90 + dy),
            )
            name = theme_name(theme)
            back = scene.rect(
                key + ("panel",),
                w=right - left,
                h=bottom - top,
                at=(CENTRE[0], (top + bottom) / 2 + dy),
            )
            back.fill(PANEL[name], edge=theme.line, edge_w=2).round(22)
            size = self._size()
            advance = cm.measure("0" * 20, size, MONO)[0] / 20
            for row, line in enumerate(self.code.split("\n")):
                col = 0
                y = top + 40 + (row + 0.5) * size * 1.6 + dy
                for text, kind in spans(line, self.language):
                    colour = SYNTAX[name].get(kind, theme.ink)
                    for char in text:
                        if not char.isspace():
                            at = (left + 60 + (col + 0.5) * advance, y)
                            scene.text(
                                key + ("c", row, col), char, size=size, font=MONO, at=at
                            ).fill(colour)
                        col += 1

        def caption(scene, key, theme, dy):
            _, _, _, bottom = self._box()
            write(
                scene,
                key + ("cap",),
                self.caption,
                Setting(SMALL, theme, 1300),
                (CENTRE[0], bottom + 60 + dy),
            )

        parts = [Part(panel, lines[0])]
        if self.caption:
            parts.append(Part(caption, lines[1]))
        return parts
