"""`physics/ellipse/orbit.py` against Kepler. Nothing renders here.

The planet must come back to where it started after one period, its distance
must swing between the closest and farthest points of the ellipse, and its
energy must not drift.
"""

import math

import orbit

STEPS = 20000


def one_period():
    planet = orbit.Planet()
    dt = orbit.PERIOD / STEPS
    distances = []
    energies = []
    for _ in range(STEPS):
        planet.step(dt)
        distances.append(planet.distance())
        energies.append(planet.energy())
    return planet, distances, energies


def test_the_planet_returns_after_one_period():
    planet, _, _ = one_period()
    assert math.hypot(planet.x - orbit.R_START, planet.y) < 0.01 * orbit.R_START


def test_the_distance_swings_between_closest_and_farthest():
    _, distances, _ = one_period()
    closest = orbit.R_START
    farthest = orbit.SEMI_MAJOR * (1 + orbit.ECCENTRICITY)
    assert abs(min(distances) - closest) < 0.01, min(distances)
    assert abs(max(distances) - farthest) < 0.01, max(distances)


def test_the_energy_does_not_drift():
    _, _, energies = one_period()
    assert max(energies) - min(energies) < 1e-4, (min(energies), max(energies))


def test_the_period_is_kepler_s():
    assert math.isclose(orbit.PERIOD, 2 * math.pi * 2.0**1.5)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
    import support

    raise SystemExit(support.run(globals()))
