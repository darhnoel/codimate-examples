"""What happens, in order, and how long each moment lasts. Only state changes here;
the drawing reads it.

    1. the quiz       the question, the answers, a countdown, and "3" picked
    2. the roll       A goes once round B, one moment per frame
    3. the reveal     "3" was wrong: it is 4
    4. why            rolling gives 3, being carried round gives 1, together 4
"""

from coins import B_AT, B_ROLLING, ROLL_SECONDS
from quiz import COUNTDOWN, OPTIONS
from style import FPS
from why import CARRY_SECONDS, ROAD_SECONDS

TICK = 0.1  # seconds per moment during the countdown

START = {
    "intro": 0.0,
    "shown": 0,
    "left": float(COUNTDOWN),
    "picked": 0.0,
    "quiz": 1.0,  # the question and the answers
    "roll": 0.0,  # how far round B, 0 to 1
    "rolling": 0.0,  # the turning marker and the counter
    "reveal": 0.0,
    "why": 0.0,  # the explanation: the quiz and the roll make way for it
    "road": 0.0,  # A rolling along B's edge laid out straight, 0 to 1
    "carry": 0.0,  # A carried round B without rolling, 0 to 1
    "sum": 0.0,  # the two put together
    "bx": B_AT[0],  # where B is: it moves to the middle for the roll, and back after
    "by": B_AT[1],
}

# Seconds each event lasts. A "roll" is one frame, so the motion is sampled smoothly.
DURATIONS = {
    "intro": 0.8,
    "option": 0.35,
    "pick": 0.6,
    "clear": 1.0,
    "roll": 1 / FPS,
    "reveal": 0.8,
    "hold": 2.0,
    "why": 0.8,
    "sum": 0.8,
}


def sweep(state, emit, key, seconds):
    """Take `key` from 0 to 1 over `seconds`, one moment per frame."""
    frames = seconds * FPS
    for k in range(1, frames + 1):
        state[key] = k / frames
        emit("roll")


def story(state, emit):
    # 1. the quiz
    state["intro"] = 1.0
    emit("intro")
    state["shown"] = len(OPTIONS)  # all five answers appear together
    emit("option")
    steps = round(COUNTDOWN / TICK)
    for k in range(1, steps + 1):
        state["left"] = COUNTDOWN * (1 - k / steps)
        emit("tick")
    state["picked"] = 1.0
    emit("pick")
    emit("hold")  # time to read "Most people pick 3. Are they right?"

    # 2. the roll: the question clears, B moves to the middle, A goes round
    state.update(quiz=0.0, rolling=1.0, bx=B_ROLLING[0], by=B_ROLLING[1])
    emit("clear")
    sweep(state, emit, "roll", ROLL_SECONDS)

    # 3. the reveal
    state.update(quiz=1.0, reveal=1.0, bx=B_AT[0], by=B_AT[1])
    emit("reveal")
    emit("hold")

    # 4. why: rolling along B's edge gives 3, being carried round gives 1 more
    state["why"] = 1.0
    emit("why")
    sweep(state, emit, "road", ROAD_SECONDS)
    emit("hold")
    sweep(state, emit, "carry", CARRY_SECONDS)
    emit("hold")
    state["sum"] = 1.0
    emit("sum")
