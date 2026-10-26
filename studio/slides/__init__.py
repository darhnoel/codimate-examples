"""Slides: Apple-keynote-style presentation films, narrated, from a list of slides.

    from studio.slides import Deck, Title, Statement, Compare
    from studio.voice import Voice

    deck = Deck([
        Title("Thinking, Fast and Slow", by="Daniel Kahneman", say="..."),
        Statement("Your mind runs on *two systems.*", say="..."),
        Compare(("System 1", "fast, automatic"), ("System 2", "slow, effortful"),
                say=["...", "..."]),
    ], voice=Voice("results/voice"))
    deck.render("results/talk.mp4", theme="dark")

The template owns the type, the spacing, the motion and the timing; a deck is
only content. ``*word*`` puts a word in the accent colour.

- ``kinds``: the slides: Title, Statement, Quote, BigNumber, Compare,
  List, Steps, Question.
- ``code``: Code, a snippet on a panel, coloured like Xcode (Python, Java, C).
- ``race``: Race, one input to two models on a running clock: typed fields
  at once against an answer typed out token by token.
- ``look``: the themes (light, dark), the type scale, and measured layout.
- ``deck``: slides into a film: cuts between slides, each part settling into
  place as its line is spoken, voice and sound mixed and mastered.

The template's locks, for every explainer built on it:

- the theme and the type scale (``look``): the palette, the faces and the sizes;
- the motion (``deck``): a slide arrives on a cut, each part cuts in a few pixels
  low and settles into place, and nothing fades;
- the timing (``deck``): every pause is a whole number of frames, and each part
  arrives as its narrated line starts.

What stays free: any part's drawing, any new kind, and a colour a kind names on
purpose (``money`` and ``code`` do). The kinds are starters, not the only
layouts. ``tests/test_slides.py`` checks the locks.
"""

from .code import Code
from .deck import Deck
from .kinds import BigNumber, Compare, List, Question, Quote, Statement, Steps, Title
from .race import Race

__all__ = [
    "BigNumber",
    "Code",
    "Compare",
    "Deck",
    "List",
    "Question",
    "Quote",
    "Race",
    "Statement",
    "Steps",
    "Title",
]
