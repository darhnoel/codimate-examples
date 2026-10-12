"""Parts 2 and 3, the roll and the reveal: A goes all the way round B, and every
turn it makes is marked and counted."""

import math

from coins import (
    ORBIT,
    R_A,
    R_B,
    TURNS,
    a_centre,
    a_turned,
    badge_spot,
    flash,
    since_turn,
)
from style import BLUE, DIM, INK, ON_YELLOW, RED, TRACK, W, YELLOW, fit
from words import SAY


def figure(scene, st):
    """B, and A wherever it has rolled to, with its turning marker."""
    b = (st["bx"], st["by"])
    centre = a_centre(st["roll"], b)
    scene.circle("B", r=R_B, at=b).fill("none", edge=INK, edge_w=5).on(
        opacity=st["intro"]
    )
    scene.circle("A", r=R_A, at=centre).fill("none", edge=BLUE, edge_w=5).on(
        opacity=st["intro"]
    )
    for name, at in (("A", centre), ("B", b)):  # a centre dot and a label each
        scene.circle(("dot", name), r=6, at=at).fill(INK).on(opacity=st["intro"])
        scene.text(("label", name), name, size=34, at=(at[0], at[1] - 32)).fill(INK).on(
            opacity=st["intro"] * (1 - st["rolling"])
        )
    marker(scene, st, centre)
    turn_marks(scene, st, centre, b)
    # A faint trace of the path A's centre takes.
    scene.circle("path", r=ORBIT, at=b).fill("none", edge=TRACK, edge_w=2).on(
        opacity=st["rolling"] * (1 - st["reveal"]), layer=-1
    )


def marker(scene, st, centre):
    """A line from A's centre that starts pointing straight up and turns with A,
    and a faint upright to compare it with. Every time the red line lands on the
    upright again, A has made one more turn."""
    turn = 2 * math.pi * a_turned(st["roll"])
    tip = (centre[0] + R_A * math.sin(turn), centre[1] - R_A * math.cos(turn))
    scene.line("marker", start=centre, end=tip, w=6).fill(RED).on(
        opacity=st["rolling"], layer=5
    )
    scene.circle("marker/tip", r=10, at=tip).fill(RED).on(
        opacity=st["rolling"], layer=6
    )
    scene.line(
        "upright", start=centre, end=(centre[0], centre[1] - R_A - 14), w=3
    ).fill(DIM).on(opacity=0.6 * st["rolling"] * (1 - st["reveal"]), layer=4)


def turn_marks(scene, st, centre, b):
    """Each turn, marked as it completes: A flashes with a ring that spreads and
    fades, and a numbered badge is left beside the path where the turn finished."""
    done, _ = since_turn(st["roll"])
    glow = flash(st["roll"]) * (1 - st["reveal"])
    scene.circle("pulse", r=R_A + 24 * (1 - glow), at=centre).fill(
        "none", edge=YELLOW, edge_w=6
    ).on(opacity=glow, layer=3)
    for k in range(1, int(TURNS) + 1):
        spot = badge_spot(k / TURNS, b)
        shown = (1.0 if done >= k else 0.0) * st["rolling"] * (1 - st["reveal"])
        scene.circle(("badge", k), r=24, at=spot).fill(YELLOW).on(
            opacity=shown, layer=-1
        )
        scene.formula(("badge", k, "n"), str(k), size=30, at=spot).fill(ON_YELLOW).on(
            opacity=shown, layer=0
        )


def counter(scene, st):
    """The big turn count, under the figure, which jumps each time it goes up."""
    done = math.floor(a_turned(st["roll"]) + 1e-9)
    colour = YELLOW if done > 3 else INK
    y = 900 if st["reveal"] else 1360  # under the centred figure while A rolls
    scene.text("count/label", SAY["turns"], size=40, at=(W / 2, y - 70)).fill(DIM).on(
        opacity=st["rolling"]
    )
    pop = 1 + 0.4 * flash(st["roll"]) * (1 - st["reveal"])
    scene.formula("count/n", str(done), size=140, at=(W / 2, y + 40)).fill(colour).grow(
        pop
    ).on(opacity=st["rolling"])
    note = SAY["not_back"] if 3 <= done < 4 else ""
    if st["roll"] >= 1.0:
        note = SAY["back"]
    size = fit(note, 40)
    scene.text("count/note", note or " ", size=size, at=(W / 2, y + 160)).fill(
        YELLOW
    ).on(opacity=st["rolling"] if note else 0.0)
