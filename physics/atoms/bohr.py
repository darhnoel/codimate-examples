"""Atoms in the Bohr model: electrons on circular orbits, in shells.

Nothing here draws. This is the simple picture, and it is only a picture: real
electrons have no orbits. Each electron circles the nucleus in its own flat plane,
the inner shells faster.
"""

import math

IRON = (26, 30, [2, 8, 14, 2])  # protons, neutrons, electrons in each shell
HYDROGEN = (1, 0, [1])
RADII = [170.0, 250.0, 330.0, 410.0]  # orbit radius of each shell, in pixels
SPEED = 5.0  # radians per second for the innermost shell


def angular_speed(shell):
    """How fast an electron in `shell` (0 is innermost) goes round: faster nearer
    the nucleus, as the Bohr model has it, falling off with the shell number."""
    return SPEED / (shell + 1) ** 1.5


class Electron:
    def __init__(self, shell, index, count):
        self.shell = shell
        self.radius = RADII[shell]
        self.omega = angular_speed(shell)
        self.phase = 2 * math.pi * index / count
        # Spread the orbital planes over the sphere, so a shell looks like a shell.
        self.tilt = math.acos(1 - 2 * (index + 0.5) / count)
        self.turn = index * math.pi * (3 - math.sqrt(5)) + shell * 0.7

    def at_angle(self, angle):
        """The point on this electron's orbit at `angle`: (x, y, z) in pixels."""
        x = self.radius * math.cos(angle)
        y = self.radius * math.sin(angle)
        # Tip the orbit's plane, then turn it about the vertical.
        y, z = y * math.cos(self.tilt), y * math.sin(self.tilt)
        x, z = (
            x * math.cos(self.turn) + z * math.sin(self.turn),
            -x * math.sin(self.turn) + z * math.cos(self.turn),
        )
        return x, y, z

    def position(self, t):
        return self.at_angle(self.phase + self.omega * t)


def electrons(shells):
    """The electrons of an atom whose shells hold `shells` electrons each."""
    return [
        Electron(shell, index, count)
        for shell, count in enumerate(shells)
        for index in range(count)
    ]


if __name__ == "__main__":
    assert len(electrons(IRON[2])) == 26 and len(electrons(HYDROGEN[2])) == 1
    print("ok: iron has 26 electrons, hydrogen 1")
