"""`physics/ripple/pool.py` against the wave it should make. Nothing renders here.

The water is checked, not the picture: a dropped stone's ring must be round and
must travel at the wave speed, and damping must take height away, never add it.
"""

import importlib.util
import math
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "pool", Path(__file__).resolve().parents[1] / "physics" / "ripple" / "pool.py")
pool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pool)


def test_the_grid_is_stable():
    # Above about 0.7 the leapfrog update blows up; the film must stay well under.
    assert pool.COURANT < 0.5, pool.COURANT


def test_the_ring_is_round():
    water = pool.Pool()
    water.impact()
    for _ in range(15):
        water.step()
    h = water.height
    n = pool.N
    for i in range(n):
        for j in range(n):
            assert abs(h[i][j] - h[j][n - 1 - i]) < 1e-9


def test_the_ring_travels_at_the_wave_speed():
    water = pool.Pool()
    water.impact()
    steps = 30
    for _ in range(steps):
        water.step()
    row = water.height[pool.N // 2]
    crest = max(range(pool.N), key=lambda j: row[j])
    travelled = abs(pool.point(crest))
    expected = pool.SPEED * steps * pool.DT
    assert abs(travelled - expected) < 2 * pool.DX, (travelled, expected)


def test_damping_only_removes_height():
    water = pool.Pool()
    water.impact()
    earlier = water.energy()
    for _ in range(60):
        water.step()
    assert water.energy() < earlier


def test_the_drop_falls_in_its_own_time():
    assert math.isclose(pool.fall_time(), math.sqrt(2 / 9.81), rel_tol=1e-9)


def test_the_landing_lifts_the_centre_gradually_to_the_full_dome():
    water = pool.Pool()
    steps = 9
    centre = pool.N // 2
    rises = []
    for k in range(steps):
        water.land((k + 1) / steps)
        water.step()
        rises.append(water.height[centre][centre])
    # Each frame lifts it higher, so the rise is gradual rather than one spike.
    assert all(later >= earlier for earlier, later in zip(rises, rises[1:])), rises
    # At the end of the landing it is the full impact height, as the dome says.
    full = pool.dome(centre, centre)
    assert abs(water.height[centre][centre] - full) < 0.5 * full, (rises[-1], full)


if __name__ == "__main__":
    import sys
    from pathlib import Path as _P

    sys.path.insert(0, str(_P(__file__).resolve().parent))
    import support
    raise SystemExit(support.run(globals()))
