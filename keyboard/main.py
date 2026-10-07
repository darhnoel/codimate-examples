"""A phone keyboard, typed on: keys light up as they are pressed, a typo is made and
taken back with the delete key, and the text grows in the field above.

    python keyboard/main.py

Keys never move, so each is named after its place, `("key", "R")`: pressing one is a
colour change and a small shrink, not a trip across the screen. The letters typed are
named by their position in the text, `("char", 4)`, so a new one fades in and a deleted
one fades out. The glow behind a pressed key is three larger, fainter rectangles that
are always there and only become visible while the key is down; the Engine tweens their
opacity, so the glow rises and fades without a keyframe.
"""

import codimate as cm

cm.canvas(1280, 720)
W = cm.width()

# What is typed. "<" is the delete key: a typo (p for o), taken back, then the rest.
SCRIPT = "hellp<o codimate"

ROWS = ("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM")
KEY_W, KEY_H, GAP = 100, 108, 12
WIDTH = 10 * KEY_W + 9 * GAP  # the keyboard is as wide as its top row
LEFT, TOP = (W - WIDTH) / 2, 196
FIELD_Y, TEXT_SIZE = 92, 46

IDLE, IDLE_EDGE, PRESSED, PRESSED_EDGE = "#2c2c30", "#4a4a50", "#2f6bff", "#9dbcff"
INK, GLOW = "#f2f2f7", "#2f6bff"


def keyboard():
    """Every key as `label -> (x, y, w, h)`, centred, in the layout of the phone's."""
    y = [TOP + r * (KEY_H + GAP) + KEY_H / 2 for r in range(4)]
    step, keys = KEY_W + GAP, {}
    for i, label in enumerate(ROWS[0]):
        keys[label] = (LEFT + i * step + KEY_W / 2, y[0], KEY_W, KEY_H)
    for i, label in enumerate(ROWS[1]):
        keys[label] = (LEFT + step / 2 + i * step + KEY_W / 2, y[1], KEY_W, KEY_H)
    wide = (WIDTH - 7 * KEY_W - 8 * GAP) / 2  # the two ends of the bottom letter row
    keys["123"] = (LEFT + wide / 2, y[2], wide, KEY_H)
    for i, label in enumerate(ROWS[2]):
        keys[label] = (LEFT + wide + GAP + i * step + KEY_W / 2, y[2], KEY_W, KEY_H)
    keys["DEL"] = (LEFT + WIDTH - wide / 2, y[2], wide, KEY_H)
    globe, sparkle, lang, enter = 120, 100, 100, 170
    space = WIDTH - globe - sparkle - lang - enter - 4 * GAP
    x = LEFT
    for label, w in (
        ("globe", globe),
        ("sparkle", sparkle),
        ("space", space),
        ("EN", lang),
        ("return", enter),
    ):
        keys[label] = (x + w / 2, y[3], w, KEY_H)
        x += w + GAP
    return keys


KEYS = keyboard()


def pressed(ch):
    """The key a character is typed on."""
    return {" ": "space", "<": "DEL"}.get(ch, ch.upper())


def typing(state, emit):
    for ch in SCRIPT:
        state["down"] = pressed(ch)
        state["typed"] = state["typed"][:-1] if ch == "<" else state["typed"] + ch
        emit("press")
        state["down"] = ""
        emit("release")
        if ch == " ":
            emit("breath")


def icon(scene, key, x, y):
    """The keys that carry a picture instead of a word, drawn from lines and circles."""
    line = dict(w=4)
    if key == "globe":
        scene.circle(("icon", "globe"), r=20, at=(x, y)).fill(
            "none", edge=INK, edge_w=3
        )
        scene.arc(("icon", "globe", "m"), r=(9, 20), sweep=(0, 360), at=(x, y)).fill(
            "none", edge=INK, edge_w=2
        )
        scene.line(
            ("icon", "globe", "eq"), start=(x - 20, y), end=(x + 20, y), **line
        ).fill(INK)
    elif key == "sparkle":
        scene.polygon(("icon", "sparkle"), cm.star(4, r=22, at=(x, y))).fill(INK)
    elif key == "DEL":
        scene.polygon(
            ("icon", "del"),
            [
                (x - 30, y),
                (x - 12, y - 18),
                (x + 28, y - 18),
                (x + 28, y + 18),
                (x - 12, y + 18),
            ],
        ).fill("none", edge=INK, edge_w=3)
        for name, a, b in (("a", (-6, -8), (14, 8)), ("b", (-6, 8), (14, -8))):
            scene.line(
                ("icon", "del", name),
                start=(x + a[0], y + a[1]),
                end=(x + b[0], y + b[1]),
                w=3,
            ).fill(INK)
    elif key == "return":
        scene.line(
            ("icon", "ret", "a"), start=(x + 22, y - 16), end=(x + 22, y + 6), w=4
        ).fill(INK)
        scene.line(
            ("icon", "ret", "b"), start=(x + 22, y + 6), end=(x - 20, y + 6), w=4
        ).fill(INK)
        scene.polygon(
            ("icon", "ret", "head"),
            [(x - 28, y + 6), (x - 12, y - 8), (x - 12, y + 20)],
        ).fill(INK)


def draw_key(scene, label, down):
    x, y, w, h = KEYS[label]
    # the glow: three larger, fainter plates, always there, seen only while down
    for i, (grow, op) in enumerate(((26, 0.10), (16, 0.14), (8, 0.20))):
        scene.rect(("glow", label, i), w=w + grow, h=h + grow, at=(x, y)).fill(
            GLOW
        ).round(22).on(layer=-3 + i, opacity=op if down else 0.0)
    plate = scene.rect(("key", label), w=w, h=h, at=(x, y)).round(16).on(layer=1)
    plate.fill(
        PRESSED if down else IDLE, edge=PRESSED_EDGE if down else IDLE_EDGE, edge_w=2
    )
    if down:
        plate.grow(0.96)
    if label in ("globe", "sparkle", "DEL", "return"):
        icon(scene, label, x, y)
    elif label != "":
        size = 30 if len(label) > 1 else 44
        scene.text(("key", label, "txt"), label, size=size, at=(x, y)).fill(INK).on(
            layer=2, opacity=1.0
        ).grow(0.96 if down else 1.0)


def view(frame):
    scene = cm.Scene()
    down, typed = frame.state["down"], frame.state["typed"]
    for label in KEYS:
        draw_key(scene, label, label == down)

    scene.rect("field", w=WIDTH, h=84, at=(W / 2, FIELD_Y)).fill(
        "#17171a", edge="#34343a", edge_w=2
    ).round(20)
    start, run = LEFT + 28, 0.0
    for i, ch in enumerate(typed):
        wide = (
            cm.measure(ch, size=TEXT_SIZE)[0]
            if ch != " "
            else cm.measure(" ", size=TEXT_SIZE)[0]
        )
        if ch != " ":
            scene.text(
                ("char", i), ch, size=TEXT_SIZE, at=(start + run + wide / 2, FIELD_Y)
            ).fill(INK)
        run += wide
    scene.rect("caret", w=3, h=50, at=(start + run + 6, FIELD_Y)).fill(GLOW)
    return scene


cm.explain(
    trace=cm.trace(typing, {"down": "", "typed": ""}),
    view=view,
    motion=[cm.Rule("*", position="linear")],
    timing=cm.Timing(
        default=0.1,
        events={"press": 0.08, "release": 0.13, "breath": 0.25},
        opening=0.6,
        final_hold=1.6,
    ),
).render("results/keyboard.mp4", fps=60, scale=1.5)

print("wrote results/keyboard.mp4")
