"""Part 4, why 4: rolling along B's edge gives 3 turns, and being carried once round
B gives 1 more. Drawn with smaller copies of A and B, in the same 1 to 3."""

import math

from style import BLUE, DIM, INK, RED, W, YELLOW, fit
from words import SAY

ROAD_SECONDS, CARRY_SECONDS = 6, 4

R_SMALL, r_SMALL = 120, 40
ROAD = 2 * math.pi * R_SMALL  # B's edge, laid out straight
ROAD_LEFT, ROAD_Y = (W - ROAD) / 2, 760
CARRY_AT = (W / 2, 1250)  # the small B the second part goes round


def toward(centre, turns, reach):
    """The point `reach` from `centre`, `turns` turns clockwise from straight up."""
    angle = 2 * math.pi * turns
    return (centre[0] + reach * math.sin(angle), centre[1] - reach * math.cos(angle))


def turning_marker(scene, key, centre, turns, op, start=0.0):  # noqa: PLR0913
    """A small A at `centre` with a red line in it that has turned `turns` times
    clockwise since it pointed `start` (in turns from straight up), and a faint
    guide where it started: each time the red line is back on it, one more turn."""
    r = r_SMALL
    tip = toward(centre, start + turns, r)
    scene.circle(key, r=r, at=centre).fill("none", edge=BLUE, edge_w=4).on(opacity=op)
    scene.line((key, "up"), start=centre, end=toward(centre, start, r + 12), w=2).fill(
        DIM
    ).on(opacity=0.6 * op, layer=4)
    scene.line((key, "marker"), start=centre, end=tip, w=5).fill(RED).on(
        opacity=op, layer=5
    )
    scene.circle((key, "tip"), r=8, at=tip).fill(RED).on(opacity=op, layer=6)


def count(scene, key, done, at, op):
    """A small turn count: the word above, the number in LaTeX below it. Returns
    the number, for the caller to colour."""
    scene.text((key, "label"), SAY["turns"], size=30, at=(at[0], at[1] - 36)).fill(
        DIM
    ).on(opacity=op)
    return scene.formula(key, str(done), size=56, at=(at[0], at[1] + 24)).on(opacity=op)


def road(scene, st):
    """Why 3 feels right: B's edge laid out as a straight road. A rolls along it
    without slipping, so it turns once for every one of its own circumferences:
    2πR ÷ 2πr = R/r = 3."""
    op = st["why"]
    title = SAY["road_title"]
    scene.text("road/title", title, size=fit(title, 40), at=(W / 2, 360)).fill(INK).on(
        opacity=op
    )
    scene.text("road/sub", SAY["road_sub"], size=30, at=(W / 2, 410)).fill(DIM).on(
        opacity=op
    )
    scene.line(
        "road", start=(ROAD_LEFT, ROAD_Y), end=(ROAD_LEFT + ROAD, ROAD_Y), w=5
    ).fill(INK).on(opacity=op)
    for k in range(4):  # one of A's circumferences between each pair of ticks
        x = ROAD_LEFT + k * ROAD / 3
        scene.line(
            ("road", "tick", k), start=(x, ROAD_Y - 12), end=(x, ROAD_Y + 12), w=4
        ).fill(INK).on(opacity=op)
    for k in range(3):
        x = ROAD_LEFT + (k + 0.5) * ROAD / 3
        scene.formula(
            ("road", "piece", k), r"2\pi r", size=26, at=(x, ROAD_Y + 40)
        ).fill(DIM).on(opacity=op)
    along = ROAD * st["road"]
    centre = (ROAD_LEFT + along, ROAD_Y - r_SMALL - 3)
    turns = along / (2 * math.pi * r_SMALL)
    turning_marker(scene, "road/A", centre, turns, op)
    done = math.floor(turns + 1e-9)
    count(scene, "road/count", done, (W / 2, 540), op).fill(
        YELLOW if done == 3 else INK
    )
    scene.formula(
        "road/eq",
        r"\frac{2\pi R}{2\pi r} = \frac{R}{r} = 3",
        size=46,
        at=(W / 2, 880),
    ).fill(INK).on(opacity=op * (1.0 if st["road"] >= 1 else 0.0))


def carry(scene, st):
    """Where the 4th turn comes from: A glued to B, not rolling, carried once round.
    It still faces every direction once, so it turns once."""
    op = st["why"] * (1.0 if st["road"] >= 1 else 0.0)
    title = SAY["carry_title"]
    scene.text("carry/title", title, size=fit(title, 40), at=(W / 2, 1010)).fill(
        INK
    ).on(opacity=op)
    scene.circle("carry/B", r=R_SMALL, at=CARRY_AT).fill("none", edge=INK, edge_w=4).on(
        opacity=op
    )
    reach = R_SMALL + r_SMALL
    # A starts on the left, a quarter turn before the top, glued on: a faint arm
    # from B's centre to A's, and A's red line pointing at B the whole way round.
    centre = toward(CARRY_AT, st["carry"] - 0.25, reach)
    scene.line("carry/arm", start=CARRY_AT, end=centre, w=3).fill(DIM).on(
        opacity=0.6 * op, layer=2
    )
    turning_marker(scene, "carry/A", centre, st["carry"], op, start=0.25)
    # A faint copy left at each quarter: its red line points right, down, left, up.
    # It has faced every way once, so it has turned once.
    for k in range(4):
        spot = toward(CARRY_AT, k / 4 - 0.25, reach)
        tip = toward(spot, 0.25 + k / 4, r_SMALL)
        left = op * 0.5 * (1.0 if st["carry"] > k / 4 else 0.0)
        scene.circle(("carry/ghost", k), r=r_SMALL, at=spot).fill(
            "none", edge=BLUE, edge_w=2
        ).on(opacity=left, layer=1)
        scene.line(("carry/ghost", k, "marker"), start=spot, end=tip, w=4).fill(RED).on(
            opacity=left, layer=1
        )
        scene.circle(("carry/ghost", k, "tip"), r=6, at=tip).fill(RED).on(
            opacity=left, layer=1
        )
    done = math.floor(st["carry"] + 1e-9)
    number = count(scene, "carry/count", done, (W / 2 + 330, CARRY_AT[1]), op)
    number.fill(YELLOW if done == 1 else INK)


def total(scene, st):
    """The two put together: R/r + 1 = 4, and the short way, by A's centre."""
    op = st["sum"]
    scene.formula(
        "sum/eq", r"\frac{R}{r} + 1 = 3 + 1 = 4", size=56, at=(W / 2, 1530)
    ).fill(YELLOW).on(opacity=op)
    scene.formula(
        "sum/eq2",
        r"\frac{2\pi(R+r)}{2\pi r} = \frac{R+r}{r} = 4",
        size=40,
        at=(W / 2, 1690),
    ).fill(INK).on(opacity=op)


def draw(scene, st):
    road(scene, st)
    carry(scene, st)
    total(scene, st)
