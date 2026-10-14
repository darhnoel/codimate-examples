"""The water: a grid of heights that follows the wave equation, one step at a time.

Nothing here draws. `main.py` reads the heights and draws them.

    height_tt = c^2 (height_xx + height_zz) - gamma * height_t

Each step, every point's new height comes from its own last two heights and its
four neighbours. The pool's edges are walls, so a ripple that reaches one turns
back, as it does in a real tank.
"""

import math

N = 40  # points across the pool, in each direction
DX = 0.1  # metres between neighbouring points
DT = 1 / 30  # seconds per step: one step per film frame
SPEED = 1.0  # c, metres per second: how fast a ripple travels
DAMPING = 0.1  # gamma: how quickly a ripple loses its height

DROP_HEIGHT = 1.0  # metres above the water when the drop lets go
GRAVITY = 9.81
DENT = 0.04  # metres the water rises under the impact
SPLASH = 0.12  # metres: how wide the impact is

# Each step moves a ripple at most this many points. Above about 0.7 the grid
# blows up; at 1/3 the ripple is well resolved.
COURANT = SPEED * DT / DX


def point(i):
    """The x (or z) coordinate of grid index `i`, centred on zero."""
    return (i - (N - 1) / 2) * DX


def fall_time():
    return math.sqrt(2 * DROP_HEIGHT / GRAVITY)


def dome(i, j):
    """How far a full impact lifts grid point (i, j)."""
    r2 = point(i) ** 2 + point(j) ** 2
    return DENT * math.exp(-r2 / (2 * SPLASH**2))


class Pool:
    def __init__(self):
        self.height = [[0.0] * N for _ in range(N)]
        self.before = [[0.0] * N for _ in range(N)]  # the height one step ago

    def copy(self):
        twin = Pool()
        twin.height = [row[:] for row in self.height]
        twin.before = [row[:] for row in self.before]
        return twin

    def impact(self):
        """The whole dome at once, from rest. The checks start from this."""
        for i in range(N):
            for j in range(N):
                self.height[i][j] = dome(i, j)
                self.before[i][j] = dome(i, j)

    def land(self, fraction):
        """The drop lands and lifts the water to `fraction` of the full dome. Called
        once per frame while the drop shrinks, so the rise is a steady lift, not a
        spike in one step. The previous height is kept, so the water moves."""
        for i in range(N):
            for j in range(N):
                self.before[i][j] = self.height[i][j]
                self.height[i][j] = fraction * dome(i, j)

    def step(self):
        """Advance one DT. Edges are walls: a point beyond the edge is taken to
        be the edge itself, so nothing flows out and the wave turns back."""
        a = DAMPING * DT / 2
        s = COURANT**2
        h, old = self.height, self.before
        new = [[0.0] * N for _ in range(N)]
        for i in range(N):
            up, down = max(i - 1, 0), min(i + 1, N - 1)
            for j in range(N):
                left, right = max(j - 1, 0), min(j + 1, N - 1)
                here = h[i][j]
                neighbours = h[up][j] + h[down][j] + h[i][left] + h[i][right]
                laplacian = neighbours - 4 * here
                new[i][j] = (2 * here - (1 - a) * old[i][j] + s * laplacian) / (1 + a)
        self.before, self.height = h, new

    def energy(self):
        """Roughly how much water is out of place: the sum of squared heights."""
        return sum(v * v for row in self.height for v in row)


def _check():
    """A ripple from the centre should spread at the wave speed."""
    pool = Pool()
    pool.impact()
    steps = round(0.5 / DT)
    for _ in range(steps):
        pool.step()
    h = pool.height
    for i in range(N):
        for j in range(N):
            assert abs(h[i][j] - h[j][N - 1 - i]) < 1e-9, "not symmetric"
    mid = N // 2
    row = [h[mid][j] for j in range(N)]
    crest_j = max(range(N), key=lambda j: row[j])
    reached = abs(point(crest_j))
    expected = SPEED * steps * DT
    assert abs(reached - expected) < 2 * DX, (reached, expected)
    print(f"ok: crest at {reached:.2f} m after {steps * DT:.2f} s "
          f"(expected {expected:.2f} m)")


if __name__ == "__main__":
    _check()
