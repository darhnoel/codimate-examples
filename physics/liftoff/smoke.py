"""The thrusters' smoke, in 3D: puffs born where the jets hit the ground,
seen as a volume.

Nothing here draws with Codimate. The smoke's shape comes from a crowd of
particles in space, so a camera can go all the way round it:

1. **Born at the jets' feet.** Each jet, as hard as it is firing, sheds puffs
   where it hits the ground, in gusts flung outward along it, the way a jet
   spreads when it lands; a few more are torn off its lower length.
2. **Carried by the air.** The air swirls: a sum of a few slow waves of a
   flow that cannot be squeezed (the curl of a smooth field), so puffs roll
   and curl round each other instead of drifting apart. A puff's own speed
   dies away into it, and a light wind leans the whole cloud.
3. **Warm, then cool.** A young puff is warm and rises, some far more than
   others; it cools and stops. It spreads and fades as it mixes.

`paint` turns a moment of it into pictures, the way smoke is rendered for film:

- The puffs are poured into a 3D grid of density fitted round them, older
  ones spread wider.
- A drifting 3D noise carves it into wisps and billows finer than any puff.
- Light from above, the moon's and the street lamps', is dimmed by the smoke
  it passes through, so tops are bright and bellies dark; the jets light the
  smoke near them blue-white.
- Where a ray meets the ground it shows the road (`floor`): asphalt, its
  lines, the lamps' warm pools, the headlights and the jets' landing glow.
- A ray from the camera through each pixel gathers light and opacity through
  the volume, front to back: what lies nearer than the car is one picture,
  what lies beyond it another, and the car is drawn between them.
"""

import math
from functools import lru_cache

import numpy as np

EMIT = 60  # puffs a jet sheds each frame, at full strength
LIFE = (3.0, 6.5)  # seconds a puff lasts, shortest and longest
SPLASH = (3.0, 8.0)  # m/s a puff is flung along the ground, slowest and fastest
SETTLE = 0.6  # seconds for a puff's own speed to die into the air's
RISE = 0.7  # m/s² a fresh, warm puff rises with
COOLING = 1.8  # seconds for a puff to lose most of its warmth
SWIRL = 0.9  # m/s: how fast the air's eddies turn
WIND = (0.0, 0.7, 0.0)  # m/s: a breeze across the road, clearing it
SIZE, GROWTH = 0.12, 0.10  # a puff's radius when born, and its growth in m/s

CELL = 0.15  # metres per grid cell
MARGIN = 2.5  # metres of grid kept round the smoke, for its puffs to spread into
THICK = 0.6  # how much a puff's worth of smoke in a cell blocks, per metre
MOON = np.array([0.62, 0.66, 0.74])  # a dim light from above
JET_LIGHT = np.array([0.50, 0.75, 1.00])  # the jets' light, from below
LAMP_LIGHT = np.array([1.00, 0.72, 0.42])  # the street lamps', warm
STEP = 0.2  # metres between samples along a ray, through the smoke
SHRINK = 3  # rays are cast for one pixel in SHRINK each way, then scaled up
# The road: along x, centred on y = 0. Its half width, where its edge lines
# are, and the dashes down its middle (dash and gap, metres).
ROAD, EDGE, DASH = 3.6, (3.25, 3.4), (4.5, 4.5)


class Smoke:
    def __init__(self, seed=5, waves=14):
        self.rng = np.random.default_rng(seed)
        self.pos = np.zeros((0, 3))
        self.vel = np.zeros((0, 3))
        self.age = np.zeros(0)
        self.life = np.zeros(0)
        self.grow = np.zeros(0)
        self.tone = np.zeros(0)
        self.rise = np.zeros(0)
        self.time = 0.0
        # The air: plane waves k, each carrying a vector a, give a flow
        # sum (k x a) cos(k . p + w t + phase), which never squeezes.
        rng = np.random.default_rng(seed + 1)
        lengths = np.exp(rng.uniform(np.log(0.7), np.log(6.0), waves))
        dirs = _normalise(rng.standard_normal((waves, 3)))
        self.k = dirs * (2 * math.pi / lengths)[:, None]
        a = _normalise(rng.standard_normal((waves, 3)))
        self.ka = np.cross(self.k, a)
        self.ka *= SWIRL / np.sqrt((self.ka**2).sum(1).sum() / 2)
        self.w = rng.uniform(0.3, 1.0, waves)
        self.phase = rng.uniform(0, 2 * math.pi, waves)

    def air(self, points):
        """The air's velocity at `points`, (n, 3), m/s."""
        angle = points @ self.k.T + self.w * self.time + self.phase
        return np.cos(angle) @ self.ka + np.array(WIND)

    def step(self, jets, strengths, dt):
        """Move on `dt` seconds. `jets` are (mouth, foot) in space, the jets
        firing at `strengths`, 0 to 1."""
        rng = self.rng
        born = []
        for (mouth, foot), strength in zip(jets, strengths):
            n = rng.poisson(EMIT * strength) if strength > 0 else 0
            if n == 0:
                continue
            # A jet lands harder the nearer the ground it fires from.
            fall = math.dist(mouth, foot)
            hit = strength / (1 + (fall / 5.0) ** 2)
            # Puffs leave in gusts: a few clumps a frame, each puff of a clump
            # flung the same way, so they stay together and make a billow.
            clumps = max(1, n // 6)
            which = rng.integers(0, clumps, n)
            angle = rng.uniform(0, 2 * math.pi, clumps)[which]
            angle += rng.normal(0, 0.08, n)
            spread = rng.uniform(0, 0.3, n)
            pos = np.array(foot) + np.stack(
                [spread * np.cos(angle), spread * np.sin(angle), np.full(n, 0.08)], 1
            )
            # One puff in eight is torn off the jet's lower length instead.
            torn = rng.random(n) < 0.125
            up = rng.uniform(0.0, 0.4, n)
            pos[torn] = (
                np.array(foot) + (np.array(mouth) - np.array(foot)) * up[torn, None]
            )
            speed = rng.uniform(*SPLASH, clumps)[which] * rng.uniform(0.9, 1.1, n) * hit
            speed[torn] *= 0.25
            vel = np.stack(
                [
                    speed * np.cos(angle),
                    speed * np.sin(angle),
                    rng.uniform(0, 0.8, clumps)[which],
                ],
                1,
            )
            born.append((pos, vel))
        if born:
            n = sum(len(p) for p, _ in born)
            self.pos = np.concatenate([self.pos] + [p for p, _ in born])
            self.vel = np.concatenate([self.vel] + [v for _, v in born])
            self.age = np.concatenate([self.age, np.zeros(n)])
            self.life = np.concatenate([self.life, rng.uniform(*LIFE, n)])
            self.grow = np.concatenate([self.grow, GROWTH * rng.uniform(0.6, 1.5, n)])
            # Some puffs much thicker than others, and some much warmer: they
            # rise in columns while the rest roll along the ground.
            self.tone = np.concatenate([self.tone, rng.lognormal(-0.4, 0.9, n)])
            self.rise = np.concatenate([self.rise, RISE * rng.uniform(0.2, 2.4, n)])
        # The air carries everything; a puff's own speed dies into it.
        air = self.air(self.pos)
        keep = math.exp(-dt / SETTLE)
        self.vel = air + (self.vel - air) * keep
        self.vel[:, 2] += self.rise * np.exp(-self.age / COOLING) * dt
        self.pos += self.vel * dt
        under = self.pos[:, 2] < 0.05
        self.pos[under, 2] = 0.05
        self.vel[under, 2] = np.abs(self.vel[under, 2]) * 0.3
        self.age += dt
        self.time += dt
        alive = self.age < self.life
        for name in ("pos", "vel", "age", "life", "grow", "tone", "rise"):
            setattr(self, name, getattr(self, name)[alive])

    def snapshot(self):
        """What a picture of this moment needs: (positions, how much smoke each
        puff holds now, each puff's radius, the time)."""
        t = self.age / self.life
        mass = self.tone * np.minimum(1, self.age / 0.15) * (1 - t) ** 1.2
        return self.pos.copy(), mass, SIZE + self.grow * self.age, self.time


def _normalise(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def _basis(cam):
    """A `science.Camera`'s eye and its forward, right and up directions."""
    az, el = math.radians(cam.azimuth), math.radians(cam.elevation)
    view = np.array(
        [math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)]
    )
    right = np.array([-math.sin(az), math.cos(az), 0.0])
    return np.array(cam.position), -view, right, np.cross(right, -view)


def _to_segment(points, a, b):
    """How far each point is from the segment a to b."""
    ab = b - a
    t = np.clip(((points - a) @ ab) / max(ab @ ab, 1e-9), 0, 1)
    return np.linalg.norm(points - (a + t[:, None] * ab), axis=1)


@lru_cache(maxsize=2)
def _noise(seed, n=64):
    """A tiling 3D noise, 0 to 1, with most of its strength in big shapes and
    some in small: white noise shaped in frequency, the way turbulence is."""
    rng = np.random.default_rng(seed)
    k = np.fft.fftfreq(n)
    kk = np.sqrt(k[:, None, None] ** 2 + k[None, :, None] ** 2 + k[None, None, :] ** 2)
    spectrum = np.where(kk > 0, np.maximum(kk, 1e-9) ** -1.7, 0.0)
    spectrum *= np.exp(-((kk / 0.25) ** 2))
    field = np.fft.ifftn(np.fft.fftn(rng.standard_normal((n, n, n))) * spectrum).real
    field = (field - field.mean()) / field.std()
    return (0.5 + 0.22 * field).clip(0, 1).astype(np.float32)


def volume(snap, jets, strengths, lamps, seed=7):
    """The smoke as grids over a box fitted round it: how thick it is (per
    metre), and the colour of the light it sends on (moonlight from above and
    the street `lamps`, both dimmed by the smoke above; the jets' blue near
    them). Returns (thick, light, corner of the box), or None with no smoke."""
    from scipy.ndimage import gaussian_filter, map_coordinates

    pos, mass, radius, time = snap
    if len(pos) == 0:
        return None
    low = np.floor(pos.min(0) - MARGIN)
    low[2] = 0.0
    shape = tuple(np.ceil((pos.max(0) + MARGIN - low) / CELL).astype(int))
    cell = np.floor((pos - low) / CELL).astype(int)
    flat = np.ravel_multi_index(np.clip(cell, 0, np.array(shape) - 1).T, shape)
    thick = np.zeros(shape, np.float32)
    # Younger, smaller puffs stay tight; older ones are spread wider.
    for small, big, spread in ((0, 0.3, 0.8), (0.3, 0.7, 2.0), (0.7, 99, 3.8)):
        pick = (radius >= small) & (radius < big)
        if pick.any():
            pile = np.bincount(flat[pick], mass[pick], np.prod(shape))
            thick += gaussian_filter(pile.reshape(shape).astype(np.float32), spread)
    # Carve it with noise drifting with the wind and slowly rising: wisps.
    grid = np.stack(
        np.meshgrid(*[np.arange(n) for n in shape], indexing="ij"), -1
    ).reshape(-1, 3)
    centres = low + (grid + 0.5) * CELL
    detail = np.zeros(len(centres), np.float32)
    for size, weight in ((2.5, 0.55), (0.8, 0.45)):
        drift = np.array(WIND) * time + np.array([0.0, 0.0, 0.25]) * time
        coords = ((centres - drift) / size * 16).T
        detail += weight * map_coordinates(_noise(seed), coords, order=1, mode="wrap")
    thick *= np.clip(3.4 * detail - 1.2, 0, 2.2).reshape(shape)
    thick *= THICK / CELL**3 * 0.01
    # Light from above, the moon's and the lamps', dimmed by the smoke over it.
    above = np.cumsum(thick[..., ::-1], axis=2)[..., ::-1] - thick
    shade = np.exp(-above * CELL).reshape(-1)
    lamp = np.zeros(len(centres), np.float32)
    for head in lamps:
        d2 = ((centres - np.array(head)) ** 2).sum(1)
        lamp += 1.4 / (1 + d2 / 5.0**2)
    jet = np.zeros(len(centres), np.float32)
    for (mouth, foot), strength in zip(jets, strengths):
        d = _to_segment(centres, np.array(mouth), np.array(foot))
        jet += strength * 0.8 / (1 + (d / 0.7) ** 2)
    light = MOON * (0.06 + 0.94 * shade)[:, None]
    light += LAMP_LIGHT * (lamp * shade)[:, None]
    light += JET_LIGHT * (1 - np.exp(-jet))[:, None]
    return thick, light.reshape(*shape, 3).astype(np.float32), low


def floor(x, y, stage):
    """The ground's colour at points (x, y): the road, its lines and the dark
    verge either side, lit by the moon, the street lamps, the car's headlights
    and the jets where they land. `stage` is a dict of `lamps` (heads, in
    space), `car` (x, y, lift) and `pools` ((foot, strength) for each jet)."""
    on_road = np.abs(y) < ROAD
    line = (np.abs(y) > EDGE[0]) & (np.abs(y) < EDGE[1])
    line |= (np.abs(y) < 0.08) & (np.mod(x, sum(DASH)) < DASH[0])
    albedo = np.where(on_road, 0.12, 0.09)
    albedo = np.where(line, 0.7, albedo)[..., None]
    light = np.broadcast_to(MOON * 0.25, (*x.shape, 3)).copy()
    for hx, hy, hz in stage["lamps"]:
        r2 = (x - hx) ** 2 + (y - hy) ** 2
        light += LAMP_LIGHT * (4.0 * (hz**2 / (hz**2 + r2)) ** 1.5)[..., None]
    cx, cy, lift = stage["car"]
    ahead = np.exp(-(((x - cx - 7.0) / 5.0) ** 2 + ((y - cy) / 2.3) ** 2))
    beams = ahead * (x > cx + 2.2) * 5.0 * math.exp(-max(lift, 0.0) / 0.8)
    light += np.array([1.0, 0.97, 0.9]) * beams[..., None]
    # Under the car the ground is in its shadow: dark and tight on its wheels,
    # fainter and wider as it climbs.
    spread = 1 + 0.5 * max(lift, 0.0)
    under = np.exp(
        -(((x - cx) / (2.6 * spread)) ** 4) - ((y - cy) / (1.25 * spread)) ** 4
    )
    light *= (1 - 0.8 * under * math.exp(-max(lift, 0.0) / 2.0))[..., None]
    glow = np.zeros(x.shape)
    for foot, strength in stage["pools"]:
        r2 = (x - foot[0]) ** 2 + (y - foot[1]) ** 2
        glow += strength * 6.0 / (1 + r2 / 1.1**2)
    light += JET_LIGHT * glow[..., None]
    return albedo * light


def _ground(cam, size, stage):
    """The ground as `cam` sees it at full `size`: its colour where a pixel's
    ray meets it (black elsewhere), and whether it does, 1 or 0."""
    eye, forward, right, up = _basis(cam)
    cx, cy = cam.origin
    a = (((np.arange(size[0]) + 0.5) - cx) / cam.focal)[None, :, None]
    b = (-((np.arange(size[1]) + 0.5) - cy) / cam.focal)[:, None, None]
    ray = forward + a * right + b * up
    hit = ray[..., 2] < -1e-6
    depth = np.where(hit, -eye[2] / np.minimum(ray[..., 2], -1e-6), 0.0)
    spot = eye + depth[..., None] * ray
    far = np.exp(-depth / 70) * hit  # the ground fades into the night far off
    return floor(spot[..., 0], spot[..., 1], stage) * far[..., None], hit * 1.0


def render(volume_, cam, split, stage, size=(1080, 1920)):
    """Cast a ray through each pixel and gather the smoke along it, front to
    back, until it meets the ground, which is painted by `floor`: two RGBA
    pictures, 0 to 1, y down, at `size` / SHRINK, of the smoke beyond `split`
    (a depth) with all the ground, and the smoke nearer than it. The ground
    fades into the night far off."""
    from scipy.ndimage import map_coordinates

    w, h = size[0] // SHRINK, size[1] // SHRINK
    eye, forward, right, up = _basis(cam)
    cx, cy = cam.origin
    px = (np.arange(w) + 0.5) * SHRINK
    py = (np.arange(h) + 0.5) * SHRINK
    a = ((px - cx) / cam.focal)[None, :, None]
    b = (-(py - cy) / cam.focal)[:, None, None]
    ray = forward + a * right + b * up  # a point at depth d is eye + d * ray
    # Where each ray meets the ground, as a depth; rays going up never do.
    ground = np.where(
        ray[..., 2] < -1e-6, -eye[2] / np.minimum(ray[..., 2], -1e-6), np.inf
    )
    light = [np.zeros((h, w, 3)), np.zeros((h, w, 3))]  # behind, in front
    clear = [np.ones((h, w)), np.ones((h, w))]
    if volume_ is not None:
        thick, colour, low = volume_
        span = np.array(thick.shape) * CELL
        corners = (
            low + np.array(np.meshgrid([0, 1], [0, 1], [0, 1])).reshape(3, -1).T * span
        )
        depths = (corners - eye) @ forward
        near, far = max(depths.min(), 1.0), depths.max()
        steps = int(np.clip((far - near) / STEP, 24, 240))
        step = (far - near) / steps
        length = step * np.linalg.norm(ray, axis=-1)  # metres along a ray per step
        for k in range(steps):
            d = near + (k + 0.5) * step
            coords = ((eye + d * ray - low) / CELL - 0.5).reshape(-1, 3).T
            sample = map_coordinates(thick, coords, order=1, cval=0.0).reshape(h, w)
            if not sample.any():
                continue
            hue = np.stack(
                [
                    map_coordinates(colour[..., c], coords, order=1, cval=0.0)
                    for c in range(3)
                ],
                -1,
            ).reshape(h, w, 3)
            alpha = (1 - np.exp(-sample * length)) * (d < ground)
            n = int(d < split)
            light[n] += (clear[n] * alpha)[..., None] * hue
            clear[n] *= 1 - alpha
    # The ground is worked out at full size and each SHRINK by SHRINK block
    # averaged, so a thin road line comes out as the right mix of line and
    # asphalt instead of a staircase. It goes all in the picture behind the
    # car, however near: the car is above it, so it is never in front of the
    # car; split between the two pictures, the seam would show once scaled up.
    lit, cover = _ground(cam, (w * SHRINK, h * SHRINK), stage)
    lit = lit.reshape(h, SHRINK, w, SHRINK, 3).mean((1, 3))
    cover = cover.reshape(h, SHRINK, w, SHRINK).mean((1, 3))
    light[0] += clear[0][..., None] * lit
    clear[0] *= 1 - cover
    out = []
    for n in (0, 1):
        # Thin smoke in bright light gives off more than its opacity can carry
        # as a colour of at most 1; so it is made just opaque enough. Clipped
        # instead, thin smoke would dim, and step wherever the ground ends.
        alpha = np.clip(np.maximum(1 - clear[n], light[n].max(-1)), 0, 1)
        hue = light[n] / np.maximum(alpha, 1e-6)[..., None]
        out.append(np.concatenate([np.clip(hue, 0, 1), alpha[..., None]], -1))
    return out


def paint(job):
    """One frame's two pictures, painted and saved: `job` is (snapshot, jets,
    strengths, camera, split, stage, (back path, front path)), `stage` as for
    `floor`. Top-level, so frames can be painted side by side in other
    processes."""
    from PIL import Image

    snap, jets, strengths, cam, split, stage, paths = job
    grids = volume(snap, jets, strengths, stage["lamps"])
    for rgba, path in zip(render(grids, cam, split, stage), paths):
        # Saved at the size the rays were cast at; the film scales it up. A
        # full-size copy would hold nine times the memory for the same smoke.
        Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").save(path)
    return paths
