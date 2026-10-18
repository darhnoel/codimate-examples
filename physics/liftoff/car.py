"""A low-poly angular car in 3D, and where its four thrusters are.

Nothing here knows about the smoke. The car is a wedge of flat steel panels;
glass windscreen, rear window and side windows; a white light bar across the
nose, a red one across the tail; an inside mirror; four solid wheels; and four
thrusters that slide out of its belly. It is drawn with a `science.Camera`:
each face is shaded by how it faces the light, and drawn far first. The
thrusters light the panels near them. It is not any real car.

Space is z up, metres. The car points along +x; its middle is at x = y = 0.
Car-local points have z = 0 at the belly. A pose lifts the car and tips it:
`pitch` raises the nose, `roll` raises the right side, both in radians.
"""

import math
from dataclasses import dataclass

LENGTH, WIDTH = 4.4, 1.9
BELLY = 0.45  # the underside's height above the ground when parked
WHEEL_R = 0.42  # a wheel's radius: its centre is this high off the ground
STEEL, GLASS = (200, 205, 212), (24, 30, 40)
TREAD, SIDEWALL = (52, 52, 58), (30, 30, 34)
RIM, RECESS, HUB = (168, 174, 184), (40, 42, 48), (205, 210, 218)
JET_BLUE = (90, 170, 255)
NOZZLES = [(x, y) for x in (-1.45, 1.45) for y in (-0.62, 0.62)]  # inside each tyre
BELL = 0.05  # how far a thruster's bell hangs below the belly: a short lip
METAL = (110, 116, 126)
UNDER = (62, 66, 74)  # the underbody: dark, matte, unlike the steel above
_TILES = (24, 10)  # the belly is drawn in tiles, so the jets' glow pools on it
JET_WIDTH = 1.5  # metres across a jet's picture, where it is widest
JET_ASPECT = 4  # a jet picture's height over its width (see jets.paint_jet)
JET_REACH = 0.45  # how far a thruster's light reaches over the panels, in metres
SKY = (0.26, 0.35, 0.9)  # light from above, a little in front (made unit below)

_X, _Y = LENGTH / 2, WIDTH / 2
_PIVOT = 0.5  # the car tips about a point this high above its belly
# The body's corners, car-local. Names: b belly, s shoulder, p peak; f front,
# k back; l left (+y), r right (-y).
_POINTS = {
    "bkr": (-_X, -_Y, 0.0),
    "bfr": (_X, -_Y, 0.0),
    "bfl": (_X, _Y, 0.0),
    "bkl": (-_X, _Y, 0.0),
    "skr": (-_X, -_Y, 0.85),
    "sfr": (_X + 0.05, -_Y, 0.5),
    "sfl": (_X + 0.05, _Y, 0.5),
    "skl": (-_X, _Y, 0.85),
    "pr": (-0.25, -0.72, 1.25),
    "pl": (-0.25, 0.72, 1.25),
}
# Panels, each wound counter-clockwise seen from outside.
_PANELS = [
    ("bkr", "bkl", "bfl", "bfr"),  # belly
    ("bkr", "bfr", "sfr", "skr"),  # right side
    ("bkl", "skl", "sfl", "bfl"),  # left side
    ("bfr", "bfl", "sfl", "sfr"),  # nose
    ("bkr", "skr", "skl", "bkl"),  # tail
    ("sfr", "sfl", "pl", "pr"),  # bonnet and windscreen slope
    ("skr", "pr", "pl", "skl"),  # rear roof slope
    ("sfr", "pr", "skr"),  # right cabin side: closes the body above the shoulder
    ("sfl", "skl", "pl"),  # left cabin side
]
_SCREEN_BASE = 0.5  # where the windscreen starts, up the slope from the nose
_WHEEL_X = 1.45
_TREAD_IN, _TREAD_OUT = _Y - 0.02, _Y + 0.14  # a tyre's two faces, |y|


def _lerp(a, b, t):
    return tuple(p + (q - p) * t for p, q in zip(a, b))


def _sub(a, b):
    return tuple(p - q for p, q in zip(a, b))


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _dot(a, b):
    return sum(p * q for p, q in zip(a, b))


def _unit(v):
    m = math.sqrt(_dot(v, v)) or 1.0
    return tuple(x / m for x in v)


def _mean(points):
    return tuple(sum(p[i] for p in points) / len(points) for i in range(3))


def _normal(corners):
    return _unit(_cross(_sub(corners[1], corners[0]), _sub(corners[2], corners[0])))


def _inset(points, t):
    """`points` pulled `t` of the way toward their middle: glass in a frame."""
    middle = _mean(points)
    return [_lerp(p, middle, t) for p in points]


def _windscreen():
    """The glass on the upper front slope, from the A-pillars to the peak, just
    in from the sides so it meets the side windows."""
    sfr, sfl, pr, pl = (_POINTS[k] for k in ("sfr", "sfl", "pr", "pl"))
    low_r, low_l = _lerp(sfr, pr, _SCREEN_BASE), _lerp(sfl, pl, _SCREEN_BASE)
    high_r, high_l = _lerp(sfr, pr, 0.96), _lerp(sfl, pl, 0.96)
    return [
        _lerp(low_r, low_l, 0.05),
        _lerp(low_r, low_l, 0.95),
        _lerp(high_r, high_l, 0.95),
        _lerp(high_r, high_l, 0.05),
    ]


def _rear_window():
    """The glass on the rear slope, from just behind the peak half way down
    toward the tail, a little in from the sides."""
    skr, skl, pr, pl = (_POINTS[k] for k in ("skr", "skl", "pr", "pl"))
    high_r, high_l = _lerp(pr, skr, 0.05), _lerp(pl, skl, 0.05)
    low_r, low_l = _lerp(pr, skr, 0.5), _lerp(pl, skl, 0.5)
    return [
        _lerp(low_r, low_l, 0.07),
        _lerp(high_r, high_l, 0.07),
        _lerp(high_r, high_l, 0.93),
        _lerp(low_r, low_l, 0.93),
    ]


def _side_window(side):
    """The glass in a cabin side, `side` "r" or "l": from the windscreen's base
    back along the roof to the rear pillar, above the waist, in a steel frame."""
    front, peak, back = _POINTS["sf" + side], _POINTS["p" + side], _POINTS["sk" + side]
    window = [
        _lerp(front, back, 0.22),
        _lerp(front, peak, _SCREEN_BASE),
        peak,
        _lerp(back, peak, 0.18),
    ]
    return _inset(window, 0.12)


def _ring(x, y, z, r, sides=24):
    """A circle in the x-z plane, at `y`, car-local."""
    return [
        (
            x + r * math.cos(2 * math.pi * k / sides),
            y,
            z + r * math.sin(2 * math.pi * k / sides),
        )
        for k in range(sides)
    ]


def _wheel(x, sign, spin=0.0):
    """A wheel at `x` on the side `sign` (-1 right, +1 left), car-local, as
    ((part, corners, colour, order), ...): a short cylinder of tread with a
    sidewall face at each end; on the outer face a rim with five spokes round
    a hub, and on the inner face the back of the wheel, a dark dish with a hub.
    Its centre is WHEEL_R above the ground; `spin` turns it, in radians, the
    way a wheel rolling forward turns."""
    z = WHEEL_R - BELLY
    outer, inner = sign * _TREAD_OUT, sign * _TREAD_IN
    o, i = _ring(x, outer, z, WHEEL_R), _ring(x, inner, z, WHEEL_R)
    parts = [
        (("tread", k), (o[k], o[k - 1], i[k - 1], i[k]), TREAD, 0)
        for k in range(len(o))
    ]
    parts.append(("outer", o, SIDEWALL, 1))
    parts.append(("inner", i, SIDEWALL, 1))
    face = outer + sign * 0.005  # the rim's details, a touch proud of the face
    parts.append(("rim", _ring(x, face, z, 0.27), RIM, 2))
    parts.append(("recess", _ring(x, face, z, 0.22), RECESS, 3))
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3 - spin
        spoke = []
        for r, da in ((0.07, -0.32), (0.225, -0.12), (0.225, 0.12), (0.07, 0.32)):
            spoke.append((x + r * math.cos(a + da), face, z + r * math.sin(a + da)))
        parts.append((("spoke", k), spoke, RIM, 4))
    parts.append(("hub", _ring(x, face, z, 0.08, 12), HUB, 5))
    back = inner - sign * 0.005
    parts.append(("inner dish", _ring(x, back, z, 0.25), RECESS, 6))
    parts.append(("inner hub", _ring(x, back, z, 0.11, 12), METAL, 7))
    return parts


def _split(points):
    """A car-local polygon cut by the belly's plane (z = 0): (the part below
    it, the part above it), either of which may be empty."""
    halves = ([], [])
    for k, p in enumerate(points):
        q = points[k - 1]
        if (q[2] < 0) != (p[2] < 0):  # the edge crosses the plane
            t = q[2] / (q[2] - p[2])
            cut = _lerp(q, p, t)
            halves[0].append(cut)
            halves[1].append(cut)
        halves[0 if p[2] < 0 else 1].append(p)
    return tuple(h if len(h) >= 3 else [] for h in halves)


def _flat_ring(x, y, z, r, sides=12):
    """A circle in the x-y plane, at height `z`, car-local."""
    return [
        (
            x + r * math.cos(2 * math.pi * k / sides),
            y + r * math.sin(2 * math.pi * k / sides),
            z,
        )
        for k in range(sides)
    ]


def _jet_light(points):
    """How much the four thrusters light a set of car-local points, 0 to 1:
    strong close to a nozzle, fading with distance, the nozzles on the belly."""
    total = 0.0
    for p in points:
        for x, y in NOZZLES:
            d2 = (p[0] - x) ** 2 + (p[1] - y) ** 2 + p[2] ** 2
            total += math.exp(-d2 / JET_REACH)
    return min(1.0, total / len(points))


def _belly(at, glow):
    """The underside as a grid of tiles, (key, corners, colour) each: dark
    underbody, lit blue-white close round each firing nozzle."""
    nx, ny = _TILES
    out = []
    for i in range(nx):
        for j in range(ny):
            xs = (-_X + LENGTH * i / nx, -_X + LENGTH * (i + 1) / nx)
            ys = (-_Y + WIDTH * j / ny, -_Y + WIDTH * (j + 1) / ny)
            local = [(xs[0], ys[0], 0.0), (xs[0], ys[1], 0.0)]
            local += [(xs[1], ys[1], 0.0), (xs[1], ys[0], 0.0)]
            cx, cy, _ = _mean(local)
            near = sum(
                math.exp(-((cx - x) ** 2 + (cy - y) ** 2) / 0.2) for x, y in NOZZLES
            )
            jet = 0.9 * min(1.0, near) * glow
            tone = [u + (b - u) * jet for u, b in zip(UNDER, (170, 210, 255))]
            out.append(((i, j), [at(p) for p in local], tone))
    return out


def _shade(normal):
    """How lit a face is, by how it turns to the sky."""
    return 0.42 + 0.58 * max(0.0, _dot(normal, _unit(SKY)))


def _hex(colour):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c))) for c in colour)


def pose(lift, pitch=0.0, roll=0.0, place=(0.0, 0.0), yaw=0.0):
    """A function taking a car-local point to space: tipped by `pitch` and
    `roll` about a point in the body, raised `lift` metres off its parked
    height, turned `yaw` (radians, to its left) and moved to `place` (x, y)."""
    cp, sp, cr, sr = math.cos(pitch), math.sin(pitch), math.cos(roll), math.sin(roll)
    cy, sy = math.cos(yaw), math.sin(yaw)

    def at(p):
        x, y, z = p[0], p[1], p[2] - _PIVOT
        x, z = x * cp - z * sp, x * sp + z * cp  # nose up
        y, z = y * cr + z * sr, -y * sr + z * cr  # right side (-y) up
        x, y = x * cy - y * sy, x * sy + y * cy  # turned
        return (x + place[0], y + place[1], z + _PIVOT + BELLY + lift)

    return at


def nozzles(at):
    """The four thrusters' mouths in space, for a pose `at`."""
    return [at((x, y, -BELL)) for x, y in NOZZLES]


def _thruster(at, x, y, state, eye):
    """One thruster's bell and jet, as (order, key, kind, data): the bell's
    sides and mouth as polygons, then the jet, from its mouth out to the
    ground and a little past, where the smoke hides its end. `state` is
    (strength 0 to 1, deployed 0 to 1): a stowed thruster is inside the belly,
    and slides out of it as it deploys."""
    strength, deployed = state
    if deployed < 0.02:
        return []
    drop = BELL * deployed
    top = _flat_ring(x, y, 0.0, 0.11)
    mouth = _flat_ring(x, y, -drop, 0.11 + 0.05 * deployed)
    axis = at((x, y, -drop / 2))
    out = []
    for k in range(len(top)):
        quad = [at(p) for p in (top[k - 1], top[k], mouth[k], mouth[k - 1])]
        normal = _normal(quad)
        if _dot(normal, _sub(_mean(quad), axis)) < 0:
            normal = tuple(-c for c in normal)
        if _dot(normal, _sub(eye, _mean(quad))) > 0:
            tone = [c * _shade(normal) for c in METAL]
            out.append((0, ("bell", k), "poly", (quad, tone)))
    ring = [at(p) for p in mouth]
    if _dot(_sub(axis, _mean(ring)), _sub(_mean(ring), eye)) > 0:  # seen from below
        hot = [d + (h - d) * strength for d, h in zip(RECESS, (235, 245, 255))]
        out.append((1, "mouth", "poly", (ring, hot)))
    if strength > 0:
        start, foot = _jet_line(at, x, y)
        reach = 1.1 * min(1.0, 0.35 + strength)  # a little past the ground
        end = _lerp(start, foot, reach)
        out.append((2, "jet", "jet", (start, end, strength)))
    return out


def _jet_line(at, x, y):
    """A thruster's jet in space: from its mouth, along the car's down, to
    where it meets the ground."""
    start = at((x, y, -BELL))
    down = _unit(_sub(at((x, y, -BELL - 1.0)), start))
    ground = start[2] / max(-down[2], 0.2)  # metres to the ground along it
    return start, tuple(s + d * ground for s, d in zip(start, down))


def jet_lines(at):
    """Each thruster's jet in space, for a pose `at`: (mouth, foot)."""
    return [_jet_line(at, x, y) for x, y in NOZZLES]


def _place_jet(scene, cam, name, data, sprite):
    """Lay a jet's picture from its mouth to its end on screen, as wide as
    JET_WIDTH metres at its middle; returns the image's handle."""
    start, end, strength = data
    (sx, sy), (ex, ey) = cam.at(start), cam.at(end)
    middle = _lerp(start, end, 0.5)
    # A metre across the line of sight, at the jet's middle, in pixels.
    sight = _sub(middle, cam.position)
    side = _unit(_cross(sight, (0.0, 0.0, 1.0)))
    a, b = cam.at(middle), cam.at(tuple(m + c for m, c in zip(middle, side)))
    metre = math.hypot(b[0] - a[0], b[1] - a[1])
    wide = JET_WIDTH * (0.6 + 0.4 * strength) * metre
    length = max(math.hypot(ex - sx, ey - sy), 1.0)
    angle = math.degrees(math.atan2(-(ex - sx), ey - sy))  # from straight down
    return (
        scene.image(name, sprite, size=(wide, wide * JET_ASPECT), at=cam.at(middle))
        .grow((1.0, length / (wide * JET_ASPECT)))
        .turn(angle)
    )


@dataclass
class Look:
    """The car at a moment: its pose `at` (from `pose`); its four thrusters,
    `jets`, as (strength 0 to 1, picture of a jet or None) each in NOZZLES'
    order; how far its wheels have turned, `spin`, in radians; and how far its
    thrusters are out of its belly, `deploy`, 0 stowed to 1 out."""

    at: object
    jets: list
    spin: float = 0.0
    deploy: float = 1.0  # how far the thrusters are out of the belly, 0 to 1


def _mirror():
    """The rear-view mirror inside, hanging from the top of the windscreen:
    (housing, glass), car-local, seen through the windscreen."""
    c = _windscreen()
    low, high = _mean(c[:2]), _mean(c[2:])
    along, across = _unit(_sub(high, low)), _unit(_sub(c[1], c[0]))
    middle = _lerp(low, high, 0.84)

    def box(w, h):
        return [
            tuple(
                m + across[i] * sx * w + along[i] * sy * h for i, m in enumerate(middle)
            )
            for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))
        ]

    return box(0.17, 0.055), box(0.15, 0.038)


def draw(scene, cam, look, layer=10):
    """Draw the car as it is in `look` (a `Look`); the panels near its firing
    thrusters are lit blue. Returns the next free layer."""
    at, jets = look.at, look.jets
    eye = cam.position
    glow = sum(strength for strength, _ in jets) / len(jets)
    shade = _shade

    items = []  # (depth, order, key, kind, data): data is a polygon or a jet
    for n, names in enumerate(_PANELS):
        local = [_POINTS[k] for k in names]
        corners = [at(p) for p in local]
        normal = _normal(corners)
        middle = _mean(corners)
        if _dot(normal, _sub(eye, middle)) <= 0:
            continue  # facing away
        light = shade(normal)
        colour = [c * light for c in STEEL]
        jet = _jet_light(local) * glow
        colour = [c + (b - c) * 0.6 * jet for c, b in zip(colour, JET_BLUE)]
        depth = cam.project(middle)[1]
        if n == 0:  # the belly, in tiles, glowing blue round each nozzle
            for key, tile, tone in _belly(at, glow):
                items.append((depth, 0, ("belly", key), "poly", (tile, tone)))
            continue
        # Glass shares its panel's depth and draws just after it.
        items.append((depth, 0, ("panel", n), "poly", (corners, colour)))
        tint = [g * (0.6 + 0.6 * light) for g in GLASS]
        if n == 5:
            screen = [at(p) for p in _windscreen()]
            items.append((depth, 1, "windscreen", "poly", (screen, tint)))
            housing, glass = (
                [at(p) for p in part] for part in _mirror()
            )  # seen through the dark glass: dim
            items.append((depth, 2, "mirror", "poly", (housing, (48, 52, 60))))
            items.append((depth, 3, "mirror glass", "poly", (glass, (78, 86, 100))))
        if n == 6:
            back = [at(p) for p in _rear_window()]
            items.append((depth, 1, "rear window", "poly", (back, tint)))
        if n in (7, 8):
            glass = [at(p) for p in _side_window("r" if n == 7 else "l")]
            items.append((depth, 1, ("window", n), "poly", (glass, tint)))
    # The thrusters hang below the belly: over the body when the belly faces the
    # camera, under it when the camera is above it. Either way they sit between
    # the far wheels and the near ones, nearest thruster last.
    belly = [at(_POINTS[k]) for k in _PANELS[0]]
    below = _dot(_normal(belly), _sub(eye, _mean(belly))) > 0
    sprites = {}
    for k, ((x, y), (strength, sprite)) in enumerate(zip(NOZZLES, jets)):
        depth = cam.project(at((x, y, -BELL)))[1]
        depth += -5e8 if below else 5e8
        sprites[k] = sprite
        state = (strength, look.deploy)
        for order, part, kind, data in _thruster(at, x, y, state, eye):
            items.append((depth, order, ("thruster", k, part), kind, data))
    # The wheels stand out from the body's sides, so a wheel on a side facing the
    # camera shows whole, over the body. One on the far side hides behind the
    # body, except, seen from below, the part of it hanging below the belly,
    # which is in front of the belly: it sorts among the thrusters.
    # A wheel is convex: its faces turned to the camera never overlap.
    for x in (-_WHEEL_X, _WHEEL_X):
        for sign in (-1.0, 1.0):
            hub = at((x, sign * _TREAD_OUT, WHEEL_R - BELLY))
            middle = at((x, sign * (_TREAD_IN + _TREAD_OUT) / 2, WHEEL_R - BELLY))
            seen = _dot(_sub(hub, middle), _sub(eye, hub)) > 0
            for part, local, colour, order in _wheel(x, sign, look.spin):
                corners = [at(p) for p in local]
                if order <= 1:  # the cylinder's own faces: cull and shade
                    normal = _normal(corners)
                    if _dot(normal, _sub(_mean(corners), middle)) < 0:
                        normal = tuple(-c for c in normal)  # point it outward
                    if _dot(normal, _sub(eye, _mean(corners))) <= 0:
                        continue
                    colour = [c * (0.1 + 0.9 * shade(normal)) for c in colour]
                    # The jets light the tyre from beneath, so its curve shows.
                    under = max(0.0, -normal[2]) * glow * 0.55
                    colour = [c + (b - c) * under for c, b in zip(colour, JET_BLUE)]
                elif seen != (order <= 5):
                    continue  # details on the face we cannot see
                key = ("wheel", x, sign, part)
                if seen:
                    items.append((-1e9, order, key, "poly", (corners, colour)))
                    continue
                low, high = _split(local) if below else ([], local)
                if high:
                    pts = [at(p) for p in high]
                    items.append((1e9, order, key, "poly", (pts, colour)))
                if low:
                    depth = cam.project(hub)[1] - 5e8
                    pts = [at(p) for p in low]
                    items.append((depth, order, (*key, "low"), "poly", (pts, colour)))
    items.sort(key=lambda item: (-item[0], item[1]))  # far first, glass on its panel
    for rank, (_, _, key, kind, data) in enumerate(items):
        if kind == "jet":
            if sprites[key[1]] is not None:
                _place_jet(scene, cam, ("car", key), data, sprites[key[1]]).on(
                    layer=layer + rank, opacity=min(1.0, 1.2 * data[2])
                )
            continue
        corners, colour = data
        tone = _hex(colour)
        pts = [cam.at(p) for p in corners]
        seam = 1.5 if key[0] == "belly" else 0.6  # tiles must not show their seams
        scene.polygon(("car", key), pts).fill(tone, edge=tone, edge_w=seam).on(
            layer=layer + rank
        )
    # The light bar along the nose's top edge, with its glow: only when the nose
    # faces the camera, or it would float over the car from behind.
    nose = [at(_POINTS[k]) for k in ("bfr", "bfl", "sfl", "sfr")]
    if _dot(_normal(nose), _sub(eye, _mean(nose))) > 0:
        bar = [cam.at(at(_POINTS["sfr"])), cam.at(at(_POINTS["sfl"]))]
        scene.line(("car", "bar glow"), start=bar[0], end=bar[1], w=9).fill(
            "#bfe4ff"
        ).on(layer=layer + len(items), opacity=0.35)
        scene.line(("car", "bar"), start=bar[0], end=bar[1], w=3).fill("#ffffff").on(
            layer=layer + len(items) + 1
        )
    # The red tail-light bar along the tail's top edge, when the tail is seen.
    tail = [at(_POINTS[k]) for k in ("bkr", "skr", "skl", "bkl")]
    if _dot(_normal(tail), _sub(eye, _mean(tail))) > 0:
        bar = [cam.at(at(_POINTS["skr"])), cam.at(at(_POINTS["skl"]))]
        scene.line(("car", "tail glow"), start=bar[0], end=bar[1], w=10).fill(
            "#ff4040"
        ).on(layer=layer + len(items), opacity=0.4)
        scene.line(("car", "tail"), start=bar[0], end=bar[1], w=3).fill("#ff2020").on(
            layer=layer + len(items) + 1
        )
    return layer + len(items) + 2
