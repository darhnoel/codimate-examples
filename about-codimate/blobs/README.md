# A cluster of shaded balls, turning

Forty off-white balls, the way a microscope's software shows segmented cell
nuclei, with the camera walking once round them. A demonstration of what
`codimate.science` draws in 3D, on an Engine that is only 2D.

```bash
.venv/bin/python about-codimate/blobs/main.py          # stacked circles: results/blobs.mp4
.venv/bin/python about-codimate/blobs/main.py mesh     # meshes: results/blobs_mesh.mp4
```

One turn, 12 seconds, both ways. The camera, the cluster and the light are the
same; only how a ball is drawn differs.

## Two ways to draw a ball

Both use **`science.Camera`** to turn each point in space into a pixel, with a
little perspective. The light rides with the camera, up and to the left of the
viewer, so the shading stays put while the cluster turns, as on a turntable.

**Stacked circles** (the default) draw each ball as 32 circles, shrinking and
brightening toward the light, the last a small highlight. Because the light never
moves on screen, every ball is shaded the same way in every frame: only its place,
size and draw order change, and the balls are sorted far to near as whole balls.

**Meshes** (`mesh`) are the science kit's real 3D: **`science.Sphere`** is a mesh of
faces, **`science.Light`** shades each face by how squarely it meets the light,
and **`science.World`** paints every face of every ball far to near.

| | Stacked circles | Meshes |
|---|---|---|
| Shapes a frame | 1,280 | about 6,300 |
| Building the film (60 fps) | about 10 s | over a minute |
| Look | smooth | faint facets |
| Light that moves on screen | would need the rings recomputed | shaded right from any light |
| Balls sinking into each other | one simply in front | right only where faces sort cleanly |

Neither has a depth buffer, so both are right for balls that touch and wrong for
balls that sink deep into each other. `cluster.py` keeps every pair apart by at
least 90% of their radii.

## What it is not

- The balls are spheres; the blobs a microscope sees are often egg-shaped.
- Real voxel data has a stepped, staircase surface. These are smooth.

## The files

| File | What it does |
|---|---|
| `main.py` | the camera's walk, and a ball drawn as stacked circles or as a mesh |
| `cluster.py` | where the balls go and how big they are. No Codimate. |
| `test_blobs.py` | the same cluster every run, inside its region, no ball swallowing another |

## Try changing

- `cluster(40)`: more balls, at more cost per frame.
- `ELEVATION`: how far from above.
- `DISTANCE`: closer is more perspective; very far is flat.
- `IVORY`: the colour of the balls.
- `COUNT`: how many circles make a ball. 8 shows soft bands, like contour lines.
