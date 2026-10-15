"""Draw one moment of the film: the detector, the mail, the fractions, the words.

Everything is placed from the state alone, so Codimate can move it between
moments. Nothing fades: the queue darkens by mixing toward the background, the
slider and fraction lines grow from nothing, and the words are written on.

Each email has four twins, drawn exactly on top of it, one for each place a
fraction can need it: precision's top and bottom row, recall's top and bottom.
A fraction is built by sending twins out of the piles, so it is made of the
mail itself and nothing has to appear from nowhere.
"""

import codimate as cm

from mail import MAIL, THRESHOLD
from story import WORDS

TEXT, DIM, TEAL = "#e8eef7", "#8d97ab", "#3fa7bb"
SPAM, GOOD, GOOD_FLAP = "#ef476f", "#dfe7f2", "#7d8799"
LASER, GLOW = "#ff2a2a", "#5c0d12"
SEALED, SEALED_FLAP, GATE_FILL = "#5b6b82", "#c9d3e0", "#15202b"
SLOT = "#24313f"  # an unlit segment of the meter
PEN = 2

W, H = 90, 64  # an envelope in a pile
BIG = 2.0  # an envelope in the gate is this many times bigger
GATE = (540, 620)
DEPTH = 0.62  # each place further back in the queue is this much smaller
PILES = {True: 290, False: 790}  # the middle of the spam pile and of the inbox
PILE_LABEL, PILE_TOP, ACROSS, PITCH_X, PITCH_Y = 930, 1020, 4, 110, 88
EXIT = (540, 770)  # just below the gate, where an email shrinks back to size
OFF = 700  # how far a pile slides to leave the screen
METER_X = 700  # the suspicion meter, right of the gate

# Where each slot's words go, and how big.
PLACES = {
    "caption": (64, (540, 140)),
    "question": (44, (540, 225)),
    "tag1": (30, (290, 1180)),
    "tag2": (30, (290, 1225)),
    "tag3": (30, (790, 1375)),
    "value": (64, (900, 1560)),
    "plabel": (32, (120, 1510)),
    "pvalue": (40, (985, 1510)),
    "rlabel": (32, (120, 1730)),
    "rvalue": (40, (985, 1730)),
    # The recap is a table: the word on the left, its question on the right.
    "recap1": (44, (190, 1530)),
    "recap2": (36, (670, 1530)),
    "recap3": (44, (190, 1650)),
    "recap4": (36, (670, 1650)),
}

# A fraction's rows: (centre x, top row y, line y, bottom row y, size, pitch).
BIG_ROWS = (520, 1490, 1560, 1630, 1.0, 110)
SMALL_ROWS = {
    "p": (560, 1470, 1510, 1550, 0.6, 62),
    "r": (560, 1690, 1730, 1770, 0.6, 62),
}


def write(where, key, latex, spec):
    """Words or a formula, written on by a pen and wiped off, never faded.
    `spec` is (size, where it goes, whether it shows)."""
    size, at, shown = spec
    where.formula(key, latex, size=size, at=at).fill(TEXT).write(
        reveal=1.0 if shown else 0.0, pen=PEN
    )


def mix(colour, dark):
    """`colour` sunk toward the black background by `dark` (0 none, 1 gone)."""
    return "#%02x%02x%02x" % tuple(
        round(int(colour[i : i + 2], 16) * (1 - dark)) for i in (1, 3, 5)
    )


def draw_envelope(scene, key, mail, place):
    """`place` is (x, y, size, darkness, layer, seen)."""
    x, y, size, dark, layer, seen = place
    w, h = W * size, H * size
    if not seen:
        body, flap = SEALED, SEALED_FLAP
    elif mail.spam:
        body, flap = SPAM, "#ffffff"
    else:
        body, flap = GOOD, GOOD_FLAP
    body, flap = mix(body, dark), mix(flap, dark)
    inset = 4 * size
    scene.rect((key, "body"), w=w, h=h, at=(x, y)).fill(body).round(8 * size).on(
        layer=layer
    )
    scene.curve(
        (key, "flap"),
        [
            (x - w / 2 + inset, y - h / 2 + inset),
            (x, y + inset),
            (x + w / 2 - inset, y - h / 2 + inset),
        ],
        w=4 * size,
    ).fill(flap).on(layer=layer)
    # The spam mark grows in as the envelope turns see-through.
    mark = 28 * size if seen and mail.spam else 0.1
    scene.text((key, "mark"), "!", size=mark, at=(x, y + 16 * size)).fill(flap).on(
        layer=layer
    )


def pile_order(state, flagged):
    """The emails in one pile, in the order they sit."""
    setting = state["setting"]
    inside = [m for m in MAIL[: state["passed"]] if m.flagged(setting) == flagged]
    if state["sorted"]:
        inside.sort(key=lambda m: not m.spam)
    return inside


def pile_layout(state, flagged):
    """Where a pile's middle is, and which of its emails stay on screen.

    Precision keeps only the spam pile, in the middle. Recall keeps only the
    real spam: the caught on the left, the missed on the right, closer in.
    """
    members = pile_order(state, flagged)
    focus = state["focus"]
    if focus == "spam":
        return (540, members) if flagged else (PILES[flagged] + OFF, [])
    if focus == "red":
        return (400 if flagged else 845), [m for m in members if m.spam]
    return PILES[flagged], members


def places(state):
    """Where every email is: in the queue, in the gate, or in a pile."""
    where = {}
    passed, seen = state["passed"], state["seen"]
    for mail in MAIL[passed:]:
        if mail.number == state["out"]:  # out of the gate, back to pile size
            where[mail.number] = (*EXIT, 1.0, 0.0, 10, seen)
            continue
        depth = mail.number - passed + (0 if state["at_gate"] else 1)
        depth -= 1 if state["out"] is not None else 0
        shrink = DEPTH ** min(depth, 6)
        if depth == 0:  # in the gate, big and clear
            where[mail.number] = (*GATE, BIG, 0.0, 10, seen)
        else:  # further back is smaller, higher and darker
            y = GATE[1] - 130 - 290 * (1 - shrink)
            where[mail.number] = (GATE[0], y, BIG * shrink, 1 - shrink, 9 - depth, seen)
    for flagged in PILES:
        middle, shown = pile_layout(state, flagged)
        centred = state["focus"] is not None
        members = pile_order(state, flagged)
        for mail in members:
            if mail in shown:  # laid out among what stays on screen
                index = shown.index(mail)
                across = min(len(shown), ACROSS) if centred else ACROSS
                left = middle - PITCH_X * (across - 1) / 2
            else:  # slides off the side it is nearest
                index = members.index(mail)
                left = PILES[flagged] - PITCH_X * (ACROSS - 1) / 2
                left += -OFF if flagged else OFF
            x = left + PITCH_X * (index % ACROSS)
            y = PILE_TOP + PITCH_Y * (index // ACROSS)
            where[mail.number] = (x, y, 1.0, 0.0, 10, seen)
    return where


def fraction_rows(state):
    """Each fraction row in use: {(which, top?): (emails, row layout)}."""
    setting, mode = state["setting"], state["fraction"]
    called = [m for m in MAIL if m.flagged(setting)]
    spam = [m for m in MAIL if m.spam]
    rows = {
        ("p", True): [m for m in called if m.spam],
        ("p", False): sorted(called, key=lambda m: not m.spam),
        ("r", True): [m for m in spam if m.flagged(setting)],
        ("r", False): sorted(spam, key=lambda m: not m.flagged(setting)),
    }
    shown = {"precision": "p", "recall": "r", "both": "pr"}.get(mode, "")
    return {
        (which, top): (mail, BIG_ROWS if mode != "both" else SMALL_ROWS[which])
        for (which, top), mail in rows.items()
        if which in shown
    }


def draw_twins(scene, state, where):
    rows = fraction_rows(state)
    for which in "pr":
        for top in (True, False):
            in_row, layout = rows.get((which, top), ([], None))
            spot = {}
            if layout:
                middle, y_top, _, y_bottom, size, pitch = layout
                count = len(rows[(which, False)][0])  # the bottom row is longer
                left = middle - pitch * (count - 1) / 2
                for index, mail in enumerate(in_row):
                    y = y_top if top else y_bottom
                    spot[mail.number] = (left + pitch * index, y, size, 0.0, 12, True)
            for mail in MAIL:
                place = spot.get(mail.number, where[mail.number])
                draw_envelope(scene, ("twin", which, top, mail.number), mail, place)


def draw_fraction_lines(scene, state):
    rows = fraction_rows(state)
    for which in "pr":
        layout = rows.get((which, False), (None, SMALL_ROWS[which]))[1]
        middle, _, y_line, _, size, pitch = layout
        count = len(rows[(which, False)][0]) if (which, False) in rows else 0
        half = (pitch * (count - 1) + W * size) / 2 + 10 if count else 0
        scene.line(
            ("line", which),
            start=(middle - half, y_line),
            end=(middle + half, y_line),
            w=4 if count else 0,
        ).fill(TEXT)


def draw_table(scene, state):
    """The recap table's rules: three across and one down, grown from the
    middle when the recap is written."""
    grow = 1.0 if state["stage"] == "recap" else 0.0
    for row, y in enumerate((1470, 1590, 1710)):
        half = 480 * grow
        scene.line(
            ("rule", row), start=(540 - half, y), end=(540 + half, y), w=2 * grow
        ).fill(DIM)
    scene.line(
        "divider",
        start=(320, 1590 - 120 * grow),
        end=(320, 1590 + 120 * grow),
        w=2 * grow,
    ).fill(DIM)


def draw_gate(scene, state):
    """A window: its inside under the mail, its frame over it, so an email
    slides in at the top and out at the bottom. A red laser sweeps across."""
    w, h = W * BIG + 40, H * BIG + 40
    scene.rect("gate", w=w, h=h, at=GATE).fill(GATE_FILL).round(22).on(layer=-1)
    scene.rect("frame", w=w, h=h, at=GATE).fill("none", edge=TEAL, edge_w=4).round(
        22
    ).on(layer=15)
    y = GATE[1] - H * BIG / 2 + H * BIG * state["scan"]
    half = W * BIG / 2 + 14
    beam = ((GATE[0] - half, y), (GATE[0] + half, y))
    scene.line("glow", start=beam[0], end=beam[1], w=14).fill(GLOW).on(layer=19)
    scene.line("laser", start=beam[0], end=beam[1], w=3).fill(LASER).on(layer=20)


def draw_meter(scene, state):
    """How suspicious the scanned email looks, in a housing that matches the
    gate. The fill rises in ten segments; the red line is the setting, and any
    fill past it turns red, so the moment an email is called spam is seen."""
    top = GATE[1] - (H * BIG + 40) / 2
    bottom = top + H * BIG + 40
    # Layers, back to front: housing, unlit track, fill, red overflow, the gaps
    # that cut it into segments, the setting line.
    scene.rect("meter", w=48, h=bottom - top, at=(METER_X, (top + bottom) / 2)).fill(
        GATE_FILL, edge=TEAL, edge_w=3
    ).round(14).on(layer=-1)
    low, high = bottom - 14, top + 14  # the track inside the housing
    tall = low - high
    score, limit = state["meter"], THRESHOLD[state["setting"]]
    scene.rect("track", w=20, h=tall, at=(METER_X, low - tall / 2)).fill(SLOT).on(
        layer=1
    )
    fill = tall * score
    scene.rect("fill", w=20, h=fill, at=(METER_X, low - fill / 2)).fill(TEAL).on(
        layer=2
    )
    over = tall * max(0.0, score - limit)
    scene.rect("over", w=20, h=over, at=(METER_X, low - tall * limit - over / 2)).fill(
        LASER
    ).on(layer=3)
    for k in range(1, 10):  # gaps that cut the fill into segments
        y = low - tall * k / 10
        scene.line(
            ("gap", k), start=(METER_X - 11, y), end=(METER_X + 11, y), w=3
        ).fill(GATE_FILL).on(layer=4)
    y = low - tall * limit
    scene.line("setting", start=(METER_X - 16, y), end=(METER_X + 16, y), w=3).fill(
        LASER
    ).on(layer=5)
    x = METER_X + 30  # a pointer on the housing's edge, aimed at the line
    scene.polygon("pointer", [(x, y), (x + 14, y - 9), (x + 14, y + 9)]).fill(LASER)
    write(scene, "score", r"\text{spam score}", (22, (METER_X, bottom + 22), True))
    spec = (26, (x + 76, y), state["slider"])  # rides with the line
    write(scene, "threshold", r"\text{threshold}", spec)


def view(frame):
    state = frame.state
    scene = cm.Scene()
    hud = scene.overlay()
    for slot, (size, at) in PLACES.items():
        for latex in dict.fromkeys(w[slot] for w in WORDS.values() if slot in w):
            write(hud, (slot, latex), latex, (size, at, latex == state["words"][slot]))
    for flagged in PILES:
        name = r"\text{spam}" if flagged else r"\text{inbox}"
        at = (pile_layout(state, flagged)[0], PILE_LABEL)
        write(scene, ("pile", flagged), name, (38, at, True))

    draw_gate(scene, state)
    draw_meter(scene, state)
    where = places(state)
    for mail in MAIL:
        draw_envelope(scene, ("mail", mail.number), mail, where[mail.number])
    draw_twins(scene, state, where)
    draw_fraction_lines(scene, state)
    draw_table(scene, state)
    return scene
