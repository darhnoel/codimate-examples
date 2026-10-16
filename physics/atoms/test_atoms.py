"""`physics/atoms/bohr.py` against the Bohr picture. Nothing renders.

Iron-56 has 26 protons, 30 neutrons and 26 electrons, in shells of 2, 8, 14 and 2;
hydrogen has one proton and one electron. Each electron stays on its own circle,
and the inner shells go round faster.
"""

import math

import bohr


def test_iron_56_and_hydrogen_nuclei():
    assert bohr.IRON[:2] == (26, 30)
    assert bohr.HYDROGEN[:2] == (1, 0)


def test_electrons_match_the_protons():
    for protons, _, shells in (bohr.IRON, bohr.HYDROGEN):
        assert sum(shells) == protons == len(bohr.electrons(shells))


def test_iron_shells_hold_2_8_14_2():
    counts = [0] * len(bohr.IRON[2])
    for electron in bohr.electrons(bohr.IRON[2]):
        counts[electron.shell] += 1
    assert counts == [2, 8, 14, 2]


def test_each_electron_stays_on_its_circle():
    for electron in bohr.electrons(bohr.IRON[2]):
        for t in (0.0, 1.3, 7.7):
            distance = math.dist((0, 0, 0), electron.position(t))
            assert abs(distance - electron.radius) < 1e-6, (electron.shell, t)


def test_inner_shells_go_round_faster():
    speeds = [bohr.angular_speed(k) for k in range(4)]
    assert speeds == sorted(speeds, reverse=True)


def test_an_electron_comes_back_after_one_period():
    electron = bohr.electrons(bohr.IRON[2])[0]
    period = 2 * math.pi / electron.omega
    assert math.dist(electron.position(0.0), electron.position(period)) < 1e-6


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
    import support

    raise SystemExit(support.run(globals()))
