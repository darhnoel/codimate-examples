# Ripple — a drop in still water, on a grid

```bash
.venv/bin/python physics/ripple/main.py    # results/ripple.mp4
.venv/bin/python physics/ripple/pool.py    # the wave's own check, no video
```

A drop falls into a pool, lands in the middle, and the ripple spreads across a
40 x 40 grid, reaches the walls and turns back. The water is a grid of heights,
moved one step at a time by the wave equation.

## What it teaches

**The water is a grid of numbers, and only the numbers move.** `pool.py` holds
a height at every grid point and knows nothing about Codimate or pixels. Each
step gives every point a new height from its own last two heights and its four
neighbours:

    height_tt = c^2 (height_xx + height_zz) - gamma * height_t

A point pulls on its neighbours, and they pull back. That is all a wave is.

**Leapfrog is the step that keeps it stable.** Each new height is worked out
from the two before it, not from the one before it alone. It is cheap, and it
does not gain or lose energy by itself, so only the damping takes height away.
The step has to be small: `COURANT = c * dt / dx` must stay under about 0.7, or
the grid blows up. The film uses 1/3.

**Walls turn the ripple back.** A point beyond the edge is taken to be the edge
itself, so nothing flows out of the pool. A ripple that reaches a wall comes
back, which is why the second half of the film is busy.

**The drop lands as a dome, and the dome rises gradually.** The falling drop
is drawn on its own, under gravity. As it lands, the centre is lifted to a larger
share of the full dome on each frame while the ball shrinks, so the dome rises
steadily instead of appearing as a spike in one step. The wave equation then
carries the water out as a ripple.

**Codimate has no 3D, so the view does it.** `main.py` turns each grid point
into a screen point with a tilt, a turn and a perspective divide, then draws
each row and column as short pieces. Each piece takes its colour from the mean
height under it, so the crests read white and the troughs deep blue. Pieces
are drawn in no particular depth order, which is fine for a wireframe.

**Heights are exaggerated twenty times.** The dome at impact is four
centimetres high on a four-metre pool, and the rings are smaller than that, so
at true size they would be too flat to see. The label on screen says so.

## Things to try

- Change `DAMPING` to make the rings last longer or die quicker.
- Change `SPEED`, and watch the rings spread faster across the same grid.
- Change `N` to 24 or 60. The picture gets coarser or finer, and the render
  time moves with the number of lines.
