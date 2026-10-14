"""A planet pulled by a star: the physics, with nothing drawn here.

Units: the star's pull GM is 1. The planet starts at distance 1 from the star,
moving sideways at the speed that makes its orbit an ellipse with eccentricity
0.5. The star sits at one focus of that ellipse.
"""

import math

GM = 1.0
ECCENTRICITY = 0.5
R_START = 1.0  # the planet's closest approach, where it starts
SPEED_START = math.sqrt((1 + ECCENTRICITY) * GM / R_START)  # sideways, there
SEMI_MAJOR = R_START / (1 - ECCENTRICITY)  # half the long axis: 2.0
PERIOD = 2 * math.pi * SEMI_MAJOR**1.5 / math.sqrt(GM)  # Kepler's third law


def pull(x, y):
    """The acceleration the star's gravity gives at (x, y): towards the star."""
    r = math.hypot(x, y)
    return -GM * x / r**3, -GM * y / r**3


class Planet:
    def __init__(self):
        self.x, self.y = R_START, 0.0
        self.vx, self.vy = 0.0, SPEED_START

    def copy(self):
        twin = Planet()
        twin.x, twin.y, twin.vx, twin.vy = self.x, self.y, self.vx, self.vy
        return twin

    def step(self, dt):
        """Advance by dt. Velocity Verlet: it keeps the energy steady over many
        orbits, where a plain Euler step would slowly drift."""
        ax, ay = pull(self.x, self.y)
        self.x += self.vx * dt + 0.5 * ax * dt * dt
        self.y += self.vy * dt + 0.5 * ay * dt * dt
        bx, by = pull(self.x, self.y)
        self.vx += 0.5 * (ax + bx) * dt
        self.vy += 0.5 * (ay + by) * dt

    def distance(self):
        return math.hypot(self.x, self.y)

    def speed(self):
        return math.hypot(self.vx, self.vy)

    def energy(self):
        return 0.5 * self.speed() ** 2 - GM / self.distance()
