"""The 1982 SAT coin question, as a vertical quiz for Reels and TikTok.

    python mathematics/coin_quiz/main.py       English
    python mathematics/coin_quiz/main.py km    Khmer

Circle A, a third the size of circle B, rolls once around it. How many times does A
turn? Most people say 3. It is 4, which was not among the test's choices.

Where things are:

    story.py   what happens, in order, and how long each moment lasts
    coins.py   the geometry of the roll: where A is, how far it has turned
    quiz.py    part 1: the question, the answers, the countdown
    roll.py    parts 2 and 3: the roll, every turn marked, and the reveal
    why.py     part 4: rolling gives 3, being carried round gives 1 more
    words.py   every word on the screen, in English and Khmer
    style.py   the canvas and the colours

This file joins them: the header and the line along the bottom, which change with
the part, and the render call.
"""

import codimate as cm
import quiz
import roll
import why
from story import DURATIONS, START, TICK, story
from style import DIM, FPS, H, INK, ON_YELLOW, W, YELLOW, fit
from words import SAY


def header(scene, st):
    """The badge (QUIZ, ANSWER, WHY 4?) and the hook under it."""
    badge = SAY["why" if st["why"] else "answer" if st["reveal"] else "quiz"]
    wide = max(260, cm.measure(badge, size=36)[0] + 64)  # room either side of the word
    scene.rect("badge", w=wide, h=64, at=(W / 2, 120)).fill(YELLOW).round(32).on(
        opacity=st["intro"]
    )
    scene.text("badge/text", badge, size=36, at=(W / 2, 120)).fill(ON_YELLOW).on(
        opacity=st["intro"], layer=12
    )
    hook = st["intro"] * (1 - st["rolling"] + st["reveal"]) * (1 - st["why"])
    scene.text("hook", SAY["hook"], size=fit(SAY["hook"], 44), at=(W / 2, 220)).fill(
        INK
    ).on(opacity=hook)


def bottom_line(st):
    """The line along the bottom: what to look at, or what just happened."""
    if st["why"]:
        if st["sum"]:
            return SAY["gives"], YELLOW
        return SAY["watch"], YELLOW
    if quiz.running(st):
        return SAY["comment"], DIM
    if st["reveal"]:
        return SAY["rescored"], YELLOW
    if st["rolling"]:
        return SAY["watch_count"], DIM
    if st["picked"]:
        return SAY["most_pick"], YELLOW
    return " ", DIM


def view(frame):
    st = frame.state
    scene = cm.Scene()
    header(scene, st)

    if st["why"]:
        why.draw(scene, st)
        text, colour = bottom_line(st)
        scene.text("bottom", text, size=fit(text, 38), at=(W / 2, H - 90)).fill(colour)
        return scene

    roll.figure(scene, st)
    row = quiz.question(scene, st)
    quiz.buttons(scene, st, row)
    roll.counter(scene, st)
    quiz.countdown(scene, st)

    text, colour = bottom_line(st)
    scene.text("bottom", text, size=fit(text, 40), at=(W / 2, H - 90)).fill(colour)
    return scene


cm.explain(
    trace=cm.trace(story, START),
    view=view,
    motion=[cm.Rule("*", position="linear")],
    timing=cm.Timing(default=TICK, events=DURATIONS, opening=0.3, final_hold=3.0),
).render(SAY["out"], fps=FPS)

print(f"wrote {SAY['out']}")
