"""A loose cluster of balls, the kind a microscope sees as cell nuclei.

Nothing here draws. Balls are dropped at random into a tall egg-shaped region
and kept only if they do not sink far into one already there: touching is fine,
and a little overlap, but not one ball swallowing another. That matters for the
drawing as much as for the look: Codimate paints far to near with no depth
buffer, which is right for balls that only touch and wrong for balls that pass
deep into each other.
"""

import math
import random

REGION = (170.0, 170.0, 260.0)  # the cluster's half-widths: x, y, and z (up)
SIZES = (30.0, 46.0)  # the smallest and largest radius
CLOSEST = 0.9  # two balls' centres stay this fraction of their radii apart, or more


def cluster(count=40, seed=3):
    """`count` balls: [(centre, radius)]. The same every run for a seed."""
    rng = random.Random(seed)
    balls = []
    while len(balls) < count:
        centre = tuple(rng.uniform(-h, h) for h in REGION)
        if sum((c / h) ** 2 for c, h in zip(centre, REGION)) > 1:
            continue  # outside the egg
        r = rng.uniform(*SIZES)
        if all(math.dist(centre, c) >= CLOSEST * (r + s) for c, s in balls):
            balls.append((centre, r))
    return balls
