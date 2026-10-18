"""`cluster.py`: the balls stay in their region and never swallow each other.

Nothing renders here.
"""

import math

from cluster import CLOSEST, REGION, SIZES, cluster


def test_the_cluster_is_the_same_every_run():
    assert cluster(40) == cluster(40)
    assert len(cluster(40)) == 40


def test_every_ball_is_inside_the_region_and_a_sensible_size():
    for centre, r in cluster(40):
        assert sum((c / h) ** 2 for c, h in zip(centre, REGION)) <= 1
        assert SIZES[0] <= r <= SIZES[1]


def test_balls_touch_at_most_a_little():
    """Painting far to near is right only for balls that do not sink deep into
    each other, so no pair may come closer than CLOSEST of their radii."""
    balls = cluster(40)
    for i, (a, ra) in enumerate(balls):
        for b, rb in balls[i + 1 :]:
            assert math.dist(a, b) >= CLOSEST * (ra + rb)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
    import support

    raise SystemExit(support.run(globals()))
