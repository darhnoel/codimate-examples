"""Money, drawn: gold coins seen side on, the easings they move by, and yen.
For slides a talk builds itself, with parts that move (``Part(..., moves=)``).

    coin(scene, key, (x, y), theme)            # one coin in a stack
    y = top + (place - top) * drop(u)          # falling into place
    x = start + (end - start) * glide(u)       # moving across
    yen(55_200)                                # "¥55,200"
"""

from __future__ import annotations

from .look import BOLD, CENTRE, HEAD, MEDIUM, Setting, Type, write

GOLD = {"light": ("#f5b800", "#c99400"), "dark": ("#ffc83d", "#d99e00")}  # face, rim
AMOUNT = Type(52, BOLD)  # a sum of money, as a label
LABEL = Type(44, MEDIUM, "muted")  # what the sum is


def coin(scene, key, at, theme, size=(200, 26)):
    """A coin seen side on, as in a stack: ``size`` is its width and thickness."""
    face, rim = GOLD["dark" if theme.page == "#000000" else "light"]
    w, h = size
    shape = scene.rect(key, w=w, h=h, at=at)
    shape.fill(face, edge=rim, edge_w=3).round(h / 2).on(layer=1)


def clamp(u: float) -> float:
    return min(max(u, 0.0), 1.0)


def drop(u: float) -> float:
    """Falling: slow, then fast, as under gravity."""
    return clamp(u) ** 2


def glide(u: float) -> float:
    """Moving across: gently out, gently in."""
    u = clamp(u)
    return u * u * (3 - 2 * u)


def yen(amount: float) -> str:
    return f"¥{amount:,.0f}"


def title(scene, key, text, theme, dy):
    """A money slide's heading, at the top."""
    write(scene, key + ("title",), text, Setting(HEAD, theme), (CENTRE[0], 150 + dy))
