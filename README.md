# Codimate examples

Worked examples for [Codimate](https://github.com/darhnoel/codimate): explainer videos
made from Python. Each example is a folder, inside one of four subject folders: `physics/`,
`mathematics/`, `computing/` and `about-codimate/`. Each has one `main.py`, and a README saying
what that example teaches. The library, its guide and its reference are in the
[main repository](https://github.com/darhnoel/codimate), and
[the site](https://darhnoel.github.io/codimate/).

Small examples are a single `main.py`. Bigger ones split. See
[When to split](#when-to-split) below for the rule, which is not the one you might
expect.

## Set up

```bash
git clone https://github.com/darhnoel/codimate-examples && cd codimate-examples
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
brew install ffmpeg typst                     # ffmpeg encodes; typst typesets formulas
.venv/bin/python computing/bubble_sort/main.py          # writes results/bubble_sort.mp4
```

Run any example from the repository root. Each writes its video into `results/`, which
is not committed. Resolution is a render argument (`scale=1.5`), not something the views
know about. `requirements.txt` installs Codimate 0.2 from PyPI, a prebuilt wheel, so no Rust is needed.

Several examples have a Khmer narration. That needs a [Kiri TTS](https://www.kiritts.com)
key in `.env` (`KIRI_API_KEY=...`, never committed) and spends credits; without the audio
they render silent, and `--silent` forces that.

## Checks

```bash
.venv/bin/python tests/run.py             # builds every film, typesets every formula: no video
.venv/bin/python tests/run.py --render    # also renders every example (needs ffmpeg)
.venv/bin/python tests/run.py --render year maxwell    # or only those
```

Examples are found, not listed: a new folder with a `main.py` inside a subject folder is covered
the day it is added. An example's own tests sit in its folder, beside the code they check,
so removing the example removes them: `python physics/ripple/test_ripple.py` runs one on its
own, and `tests/run.py` finds them all. `ruff check` must pass too, including no function with more than five arguments.

## Start here

**[`computing/bubble_sort/`](computing/bubble_sort/)** — things that **move**.

Bars slide when they swap. Names follow the *thing*, so `cm.items()` gives each
value an identity of its own and the Engine can tell that bar 3 travelled
rather than that two bars changed height. Read this one first; everything else
assumes it.

## The one decision Codimate cannot make for you

**[`mathematics/galton_board/`](mathematics/galton_board/)** — both kinds of name, side by side.

Pegs and bins never move, so their names follow the *place*:
`("peg", row, i)`, no `cm.items()` anywhere. Balls do move, so each is named
after itself and travels because the trace says where it *is* at each moment —
the view never mentions movement. A dozen are in flight at once, each on its
own path, falling under a real ballistic simulation sampled at a fixed time
step, which is what lets balls at different depths move at different speeds.

Everything else is a consequence of choosing between those two.

## Motion you might think needs a new feature

**[`mathematics/dharma_wheel/`](mathematics/dharma_wheel/)** — a turning wheel, with no rotation in the
API.

The trace says where the spokes are every 15 degrees and the Engine fills in
the rest, exactly as it does for a sliding bar. Rotation is just position over
time. The README works through why 15 degrees and not 45.

## Continuous motion from sampled physics

**[`physics/pendulum/`](physics/pendulum/)** — gravity supplies the acceleration; Codimate
connects the moments.

The simulation advances angle and angular velocity at a fixed time step. The
view turns each sampled angle into a string and bob, and `linear` interpolation
keeps that already-continuous motion from stopping at every event.

## Getting it right when the famous version does not

**[`physics/helical_solar_system/`](physics/helical_solar_system/)** — the Sun moves, so every
orbit is a helix.

The popular "solar system is a vortex" video has the orbital plane square to
the direction of travel and the planets trailing behind like a comet's tail.
Neither is true. This one inclines the plane 60° and lets half of each orbit
run ahead of the Sun, which is what actually happens.

**[`physics/bernoulli_lift/`](physics/bernoulli_lift/)** — and the story that goes with it.

The air over a wing really is faster and really is at lower pressure. The
"equal transit time" reason for it is not true, and this measures the two
parcels to show it: the upper one arrives 1.35x sooner. The flow is the exact
Joukowski solution, so the speeds and the times are consequences rather than
choices.

## When the drawing already knows something

**[`mathematics/rubiks_cube/`](mathematics/rubiks_cube/)** — a cube solving itself, beside a drawing
that turned out to be the same cube.

Nine overlapping circles, twelve places on each, every place on exactly two.
That is not decoration, it is the cube's nine layers, and the example searches
for the pairing that proves it rather than assuming one. Turn a layer and its
twelve dots slide three places along their circle.

It is also where the drawing order had to be got right four separate times, and
each of those is written down where it happened.

## Drawing something with no library help at all

**[`physics/spacetime/`](physics/spacetime/)** — a lattice of space deformed by a mass inside
it, in wireframe 3D.

Codimate has no camera, no depth buffer and no 3D of any kind, so this one
writes its own projection and pays for it. It is here for what that cost: the
lattice flickered for four attempts, and the cause turned out to be that draw
order is resolved once per *segment* rather than per frame — so any layer that
changes is a hard cut at a scene boundary, sixteen times a second. The fix is
to freeze the order, which is free when nothing is filled.

## Explaining a physical thing, with a kit

**[`physics/orbits/`](physics/orbits/)** — the Sun, the Earth and the Moon, and a camera pulling
back from one to all three.

Built from [`codimate.science`](https://github.com/darhnoel/codimate/blob/main/docs/reference.md#the-science-kit) alone:
a camera, spheres, orbits, labels that stay clear of each other. It is here for what the kit made
easy and for what it did not: one moment per frame or the draw order tears, names
that follow bodies collide unless something moves them, and a pull-back is `dolly`,
not `moved`.

**[`physics/maxwell/`](physics/maxwell/)** — how did Maxwell find his equations? Nine scenes in Khmer,
from a compass and a wire to the number that matched light.

Every equation is LaTeX, written on the moment its discovery happens, and Maxwell's own
term is a separate formula so it can arrive alone. It is here for the narration: each
word is lined up with the voice by transcribing the recording, and for how a long film
splits into one module per scene.

**[`physics/cavendish/`](physics/cavendish/)** — how do you weigh the Earth? Two minutes of Khmer
captions, a torsion balance, and a zoom out through four scales to say how small the
twist was.

The long film the science kit was cut out of, drawn by hand and kept as it was. It is
here for the captions that pace the scenes, and for zoom levels nested round one point.

**[`physics/year/`](physics/year/)** — the same three bodies for a real 365 days, 2025.

The motion is taken from the sky and only the sizes are made up: true eccentricity
and closest approach, the equinoxes and solstices on their dates, a Moon whose
orbit turns and whose phases come from the light. `sky.py` is the astronomy and
knows nothing about drawing; its test checks it against the almanac.

## When the numbers have to be real

**[`physics/archimedes/`](physics/archimedes/)** — one box that becomes water, ice, steel and
then a ship.

It is one name the whole way through, so the Engine tweens between the four
rather than cutting. Nothing about the picture is placed by eye: the hull's
wall thickness is *solved* so that the ship holds exactly the steel the block
was made from, and the 821 kg/m³ that floats it is a consequence of the drawing
rather than a figure picked to make the point come out.

It is also the example that renders in two languages — `main.py km` gives the
Khmer one — and the README says what that took, which was less than you would
think everywhere except the title card that types itself on.

## An interface, not a diagram

**[`computing/keyboard/`](computing/keyboard/)** — a phone keyboard, typed on.

Keys never move, so each is named after its place and a press is a colour change; the
glow behind it is three faint plates whose opacity the Engine tweens; the typed letters
are named by position, so a new one fades in and a deleted one fades out. It also draws
every icon from lines, since there is no emoji font.

## If you are coming from Manim

**[`about-codimate/manim/`](about-codimate/manim/)** — five of Manim's tutorial scenes, translated.

Not a fight Codimate wins: for two shapes and three verbs, a library built
around shapes-and-verbs is shorter, and the README says so. It is here because
two of them say the quiet part out loud. `DifferentRotations` — where
`.animate` and `Rotate` do different things from calls that look alike — is
the clearest statement of the rule this library runs on: what you put in the
payload decides what the motion is. And `TwoTransforms` asks for a distinction
that does not exist here, because the name *is* the identity.

## When to split

**Split where the knowledge splits, not by the four pieces.**

The temptation is `state.py` / `algorithm.py` / `view.py` / `motion.py` /
`timing.py`, mirroring the Rust examples. Don't. Those four pieces are short —
in `bubble_sort` they are 8, 20, 1 and 1 lines — and they are already named
where they are used:

```python
cm.explain(trace=..., view=..., motion=..., timing=...)
```

That call shows how the pieces *connect*, which a directory listing cannot.
Splitting there gives you five files of a dozen lines each and five import
blocks, which is the ceremony the Python surface exists to remove
([ADR 0008](https://github.com/darhnoel/codimate/blob/main/docs/adr/0008-python-authoring-surface.md)).

**A seam is worth having when the file on one side of it does not need
Codimate.** That is the test, and it is easy to apply:

```text
mathematics/rubiks_cube/
    main.py        the four pieces, together, plus the view
    cube.py        the cube as a permutation of 54 stickers — no drawing at all
    geometry.py    where a sticker is in space, and what a turn does to it
    graph.py       the traced drawing: places, lines, circles, colours
    places.py      which place holds which sticker — searched for, then checked
```

Only `main.py` imports `codimate`. The other four are plain Python that can be
run, checked and argued with on their own — and they are: `cube.py` verifies
that `(R U R' U')` has order 6, `places.py` verifies that a quarter turn slides
a circle's twelve places exactly three along it. Neither needs a video to say
whether it is right.

`galton_board` splits on the same test for one file: `physics.py` is the
ballistic simulation and imports nothing of ours.

**Rough threshold:** one `main.py` until it passes ~150 lines or grows a part
that could be checked without rendering anything. `bubble_sort` (57 lines) and
`galton_board`'s view (72) are single files and should stay that way.

## Adding one

```text
physics/your_example/          the subject folder it belongs in
    main.py       the whole explanation
    README.md     what it teaches, and what to try changing
    test_*.py     checks for any part split out of main.py, if there is one
```

Start with one file. Split a part out only when you could test it on its own.

See [Writing Your First Animation](https://github.com/darhnoel/codimate/blob/main/docs/tutorial.md) for the walkthrough
and [How Codimate Thinks](https://github.com/darhnoel/codimate/blob/main/docs/concepts.md) for why it is shaped this way.
