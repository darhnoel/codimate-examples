"""A thruster's jet, painted as a picture.

Nothing here draws with Codimate. `paint_jet` paints one jet the way a camera
sees a rocket's exhaust at night: a white-hot core with faint shock diamonds
near the mouth, turning blue as it flares and breaks up, fading out at the far
end. `car.py` lays a picture along each thruster, stretched and turned to it in
3D; a few pictures, each a little different, shown in turn make it flicker.
`paint_glow` paints a street lamp's soft glow the same way.
"""

import numpy as np


def _box(a, r, axis):
    """A running mean of width 2r + 1 along `axis`, edges held."""
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return (hi - lo) / (2 * r + 1)


def blur(a, r):
    """Close to a Gaussian blur: three box blurs each way."""
    for _ in range(3):
        a = _box(_box(a, r, 0), r, 1)
    return a


def paint_jet(path, seed, wide=128, tall=512):
    """One jet as a picture, mouth at the top middle, `wide` by `tall` pixels:
    a white-hot core with shock diamonds near the mouth, turning blue as it
    flares and breaks up, fading out at the far end. Its shape is a little
    different for each `seed`, so a few of them shown in turn flicker. Painted
    at twice the size and shrunk, for a clean edge."""
    from PIL import Image

    rng = np.random.default_rng(seed)
    w, h = wide * 2, tall * 2
    v, u = np.mgrid[0:h, 0:w].astype(float)
    v = (v + 0.5) / h  # 0 at the mouth .. 1 at the far end
    u = (u + 0.5) / w * 2 - 1  # -1 .. 1 across
    # A wavering, broken edge: smooth noise, stretched along the jet, that grows
    # as the jet goes.
    noise = blur(rng.standard_normal((h // 8 + 2, w // 8 + 2)), 2)
    noise = np.kron(noise / (noise.std() + 1e-9), np.ones((8, 8)))[:h, :w]
    noise = blur(noise, 4)
    radius = 0.16 + 0.7 * v**0.85
    wobble = u + 0.10 * v * noise
    across = (wobble / radius) ** 2
    fade = np.clip(1 - v, 0, 1) ** 0.7
    core_r = 0.09 + 0.06 * v
    diamonds = 1 + 0.35 * np.cos(2 * np.pi * v / 0.075) ** 8 * np.exp(-v / 0.22)
    core = np.exp(-((u / core_r) ** 2)) * np.exp(-v / 0.28) * diamonds
    body = np.exp(-1.8 * across) * np.exp(-v / 1.3) * (0.75 + 0.35 * noise)
    halo = np.exp(-0.5 * across) * np.exp(-v / 1.1) * 0.35
    rgb = (
        np.clip(core, 0, 1.4)[..., None] * np.array([1.0, 1.0, 1.0])
        + np.clip(body, 0, 1)[..., None] * np.array([0.30, 0.60, 1.0])
        + halo[..., None] * np.array([0.10, 0.28, 0.75])
    ) * fade[..., None]
    rgb = np.clip(rgb, 0, 1)
    alpha = np.clip(rgb.max(-1, keepdims=True) * 1.15, 0, 1)
    rgba = np.concatenate([rgb / np.maximum(alpha, 1e-6), alpha], axis=-1)
    image = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), "RGBA")
    image.resize((wide, tall), Image.LANCZOS).save(path)
    return path


def paint_glow(path, size=256):
    """A street lamp's glow as a picture: warm, brightest in the middle and
    falling off softly, the way a lamp looks through damp night air."""
    from PIL import Image

    v, u = (np.mgrid[0:size, 0:size] + 0.5) / size * 2 - 1
    r = np.hypot(u, v)
    glow = np.exp(-((r / 0.16) ** 2)) * 0.9 + np.exp(-r / 0.32) * 0.35
    glow *= np.clip(1 - r, 0, 1) ** 2  # nothing at the picture's edge
    rgb = (
        np.array([1.0, 0.74, 0.46])
        + (1 - np.array([1.0, 0.74, 0.46])) * np.exp(-((r / 0.08) ** 2))[..., None]
    )
    alpha = np.clip(glow, 0, 1)[..., None]
    rgba = np.concatenate([np.clip(rgb, 0, 1), alpha], -1)
    Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").save(path)
    return path
