"""A film's timeline, asked by beat name, so a cue sheet can say "when the
ball rolls" instead of a number of seconds."""

from __future__ import annotations


class Beats:
    """The film's timeline, asked by beat name."""

    def __init__(self, timeline):
        self._beats = list(timeline)

    def first(self, name) -> tuple:
        """(start, length) of the first beat called ``name``."""
        return next((start, length) for start, length, n in self._beats if n == name)

    def starts(self, name) -> list:
        """When every beat called ``name`` starts."""
        return [start for start, _, n in self._beats if n == name]

    def __iter__(self):
        """Every beat, in order, as ``(start, length, name)``."""
        return iter(self._beats)
