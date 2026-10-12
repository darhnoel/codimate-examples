"""Part 1, the quiz: the question, the five answers, and the countdown."""

import math

import codimate as cm
from style import BORDER, GREEN, INK, ON_YELLOW, RED, TIMER_BACK, W, YELLOW
from words import SAY

QUESTION = SAY["question"]
OPTIONS = [
    ("A", r"\frac{3}{2}"),
    ("B", "3"),
    ("C", "6"),
    ("D", r"\frac{9}{2}"),
    ("E", "9"),
]
PICKED = 1  # "3", the answer nearly everyone gives
COUNTDOWN = 10  # seconds: about 7 to read the question, and a few to think

QUESTION_TOP, QUESTION_PAD = 860, 40  # where the question starts, and space round it
QUESTION_LINES = 4  # room kept for the question, so the answers sit at one height
# The answers sit in one row: five columns, each a circled letter over its answer.
ANSWER_GAP = 190  # from one column's centre to the next
ANSWER_DROP = 120  # from the letter down to its answer


def wrap(text, size, room):
    """`text` broken into lines no wider than `room`, and always at a newline."""
    lines = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split():
            trial = f"{line} {word}".strip()
            if cm.measure(trial, size=size)[0] > room and line:
                lines.append(line)
                line = word
            else:
                line = trial
        lines.append(line)
    return lines


def question(scene, st):
    """The question, as plain text, while the quiz is on. Returns where the row
    of answers goes."""
    lines = wrap(QUESTION, 38, W - 120 - 2 * 48)
    assert len(lines) <= QUESTION_LINES, f"the question runs to {len(lines)} lines"
    height = QUESTION_LINES * 52 + 2 * QUESTION_PAD
    shift = (QUESTION_LINES - len(lines)) * 26  # a shorter question sits centred
    asking = st["intro"] * st["quiz"] * (1 - st["reveal"])
    for i, line in enumerate(lines):
        y = QUESTION_TOP + QUESTION_PAD + 26 + shift + i * 52
        scene.text(("q", i), line, size=40, at=(W / 2, y)).fill(INK).on(opacity=asking)
    return QUESTION_TOP + height + 100  # a clear gap under the question


def buttons(scene, st, row):
    """The answers in one row, with no boxes: a circled letter over each answer.
    The picked one's circle fills green, and red, with a ✕, once it is wrong."""
    for i, (letter, answer) in enumerate(OPTIONS):
        x = W / 2 + (i - 2) * ANSWER_GAP
        y = row + ANSWER_DROP
        on = (1.0 if i < st["shown"] else 0.0) * st["quiz"]
        chosen = st["picked"] and i == PICKED
        wrong = chosen and st["reveal"]
        mark = RED if wrong else GREEN
        scene.circle(("opt", i, "chip"), r=34, at=(x, row)).fill(
            mark if chosen else "none", edge=mark if chosen else BORDER, edge_w=3
        ).on(opacity=on, layer=11)
        scene.text(("opt", i, "letter"), letter, size=36, at=(x, row)).fill(
            ON_YELLOW if chosen else INK
        ).on(opacity=on, layer=12)
        size = 50 if "frac" in answer else 64  # a stacked fraction is tall
        scene.formula(("opt", i, "answer"), answer, size=size, at=(x, y)).fill(
            mark if chosen else INK
        ).on(opacity=on, layer=12)
        scene.formula(("opt", i, "wrong"), r"\times", size=56, at=(x, y + 100)).fill(
            RED
        ).on(opacity=on if wrong else 0.0, layer=12)


def running(st):
    """Whether the countdown is on: the answers are up and nothing is picked yet."""
    return st["shown"] == len(OPTIONS) and not st["picked"]


def countdown(scene, st):
    """A ring under the answers that empties, with the seconds left in it."""
    at = (W / 2, 1620)  # in the space under the row, where the eye already is
    on = 1.0 if running(st) else 0.0
    left = st["left"] / COUNTDOWN
    scene.circle("timer/back", r=80, at=at).fill("none", edge=TIMER_BACK, edge_w=12).on(
        opacity=on
    )
    scene.arc("timer/ring", r=80, sweep=(0, 360 * max(left, 0.001)), at=at).fill(
        "none", edge=YELLOW, edge_w=12
    ).on(opacity=on, layer=11)
    scene.formula("timer/n", str(math.ceil(st["left"] - 1e-9)), size=64, at=at).fill(
        INK
    ).on(opacity=on, layer=12)
