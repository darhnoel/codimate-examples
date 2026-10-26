"""The explainer template's locks, checked without rendering a frame.

The template is studio/slides, a narrated deck. Its theme, motion and timing are
locked; its layouts are free. A file that names a colour of its own on purpose is
listed in OVERRIDES. Run it with:

    python tests/test_slides.py
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT)]

import codimate as cm  # noqa: E402

import support  # noqa: E402

from studio.slides import (  # noqa: E402
    BigNumber,
    Code,
    Compare,
    Deck,
    List,
    Question,
    Quote,
    Race,
    Statement,
    Steps,
    Title,
)
from studio.slides import deck as engine  # noqa: E402
from studio.slides.look import THEMES  # noqa: E402
from studio.slides.money import coin  # noqa: E402

SLIDES = ROOT / "studio" / "slides"
# A colour is named in the theme. These files name their own on purpose: a gold coin,
# and the Xcode palette of a code panel.
OVERRIDES = {"look.py", "money.py", "code.py"}
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")


def kinds() -> list:
    """One slide of every kind, each with the content it needs."""
    return [
        Title("Thinking, Fast and Slow", by="Daniel Kahneman"),
        Statement("Your mind runs on *two systems.*"),
        Quote("Nothing in life is as important as you think it is.", by="D. K."),
        BigNumber("5¢", "the ball's real price"),
        Compare(("System 1", "fast, automatic"), ("System 2", "slow, effortful")),
        List("Takeaways", ["Two systems", "One brain"]),
        Steps("The peak-end rule", ["Live it", "Remember it"]),
        Question("How much is the ball?", "5 cents"),
        Code("Classitis", "def add(a, b):\n    return a + b"),
        Race(
            "Which is faster?",
            "A bat and a ball cost $1.10.",
            fast=("Fast", 2.0, [("Ball", "5 cents", 0.8), ("Bat", "$1.05", 0.2)]),
            slow=("Slow", 6.0, "The ball costs 5 cents."),
        ),
    ]


def test_nothing_fades():
    """A part cuts in or settles into place. Nothing in the template sets opacity."""
    for path in SLIDES.glob("*.py"):
        assert "opacity" not in path.read_text(), path.name


def test_colours_come_from_the_theme():
    """A colour is named in the theme, or in a file that names its own on purpose."""
    for path in SLIDES.glob("*.py"):
        if path.name not in OVERRIDES:
            assert not HEX.search(path.read_text()), path.name


def test_timing_is_whole_frames():
    """Every pause is a whole number of frames, so voice and text land together."""
    for name in ("SETTLE", "BREATH", "BETWEEN", "VOICE"):
        frames = getattr(engine, name) * engine.FPS
        assert abs(frames - round(frames)) < 1e-9, name


def test_every_kind_builds_a_film():
    """The deck builds into a film from every kind, without rendering a frame."""
    assert Deck(kinds()).film().duration > 0


def test_every_part_draws_in_both_themes():
    """Each part draws in the light and in the dark theme, and so does a coin."""
    for slide in kinds():
        for theme in THEMES.values():
            for part in slide.parts():
                if part.moves:  # an animated part draws its state at the end
                    part.draw(cm.Scene(), ("probe",), theme, 0, part.moves)
                else:
                    part.draw(cm.Scene(), ("probe",), theme, 0)
    for theme in THEMES.values():
        coin(cm.Scene(), "probe", (960, 540), theme)


if __name__ == "__main__":
    sys.exit(support.run(globals()))
