# keyboard

```bash
.venv/bin/python computing/keyboard/main.py    # results/keyboard.mp4
```

A phone keyboard being typed on: each key lights up blue as it is pressed, a typo is
made and taken back with the delete key, and the text grows in the field above. About
six seconds.

## What it teaches

**A thing that does not move is named after its place.** Every key is `("key", "R")`.
Pressing one is a change of colour and a shrink to 96%, not a journey, so the Engine
tweens the colour and nothing else. Compare [`bubble_sort`](../bubble_sort/), where the
names follow the things because the things travel.

**A glow without a keyframe.** Behind each key are three larger, fainter plates, drawn
in every moment. Their opacity is 0 until the key is down and then 0.1, 0.14 and 0.2,
and the Engine tweens the opacity, so the glow rises on the press and fades on the
release. Nothing is added or removed, so nothing pops.

**Text that grows is named by position.** The typed letters are `("char", i)`. A new
letter is a name that was not there, so it fades in; a deleted one is a name that went,
so it fades out. The caret is the one shape that moves, along the text.

**Icons from lines.** The globe, the sparkle, delete and return carry pictures. They are
a circle and an ellipse, a four-pointed `cm.star`, and a few lines and polygons, because
the fonts compiled into Codimate have no emoji.

## Things to try

- Change `SCRIPT`. `<` is the delete key, so `"hellp<o"` types a typo and corrects it.
- Colours are the constants under the layout: make it light, or make the glow red.
- Add a row of numbers by extending `ROWS` and `keyboard()`.
