"""The geometry of A rolling round B. Numbers in, positions out: nothing is drawn here.

A's centre stays R + r from B's, so it goes round a circle of radius R + r, and A
turns (R + r) / r times for each trip: 4, when r is a third of R.
"""

import math

from style import W

R_B, R_A = 189, 63  # A's radius is exactly a third of B's
ORBIT = R_B + R_A  # A's centre stays this far from B's
TURNS = ORBIT / R_A  # = 4: how many times A turns in one trip round B

B_AT = (W / 2 + 70, 600)  # where B sits beside the question
B_ROLLING = (W / 2, 820)  # in the middle of the screen while A rolls

ROLL_SECONDS = 8  # one trip round B
PULSE = 0.5  # seconds a turn's flash lasts


def a_centre(u, b=B_AT):
    """Where A's centre is after `u` of the trip (0 to 1). It starts on the left
    and goes clockwise on screen, up over the top first, as in the figure."""
    angle = math.pi - 2 * math.pi * u
    return (b[0] + ORBIT * math.cos(angle), b[1] - ORBIT * math.sin(angle))


def badge_spot(u, b=B_AT):
    """Just outside A's path, where A was after `u` of the trip: clear of A as it
    rolls past, so a badge is never hidden under it."""
    angle = math.pi - 2 * math.pi * u
    reach = ORBIT + R_A + 50
    return (b[0] + reach * math.cos(angle), b[1] - reach * math.sin(angle))


def a_turned(u):
    """How far A has turned, in turns, after `u` of the trip."""
    return TURNS * u


def since_turn(u):
    """(whole turns done, seconds since the last one) after `u` of the trip."""
    turned = a_turned(u)
    done = math.floor(turned + 1e-9)
    return done, (turned - done) * ROLL_SECONDS / TURNS


def flash(u):
    """1 the instant a turn completes, fading to 0 over PULSE seconds."""
    done, age = since_turn(u)
    return max(0.0, 1 - age / PULSE) if done >= 1 else 0.0


if __name__ == "__main__":
    # The answer the film is about, checked without drawing anything.
    assert TURNS == 4
    assert [since_turn(k / 4)[0] for k in range(5)] == [0, 1, 2, 3, 4]
    start, end = a_centre(0.0), a_centre(1.0)
    assert math.dist(start, end) < 1e-9, "A ends where it started"
    print("ok: A turns 4 times in one trip round B")
