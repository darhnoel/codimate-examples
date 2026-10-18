# Launch film

A 30-second ad for Codimate 0.4, Apple-style: dark type on white, one blue,
words that spring into place, and a sound track synthesised to match every move.

```bash
python about-codimate/ads/main.py            # results/codimate-0.4-launch.mp4
python about-codimate/ads/main.py --audio    # only the sound track
python about-codimate/ads/main.py --stills   # a few frames, to check layout
```

## What it teaches

- **Text presets.** Each headline enters its own way (`cm.text.words_up`,
  `letters_down`, `words_up_blur`...) and its `rules()` give it a stagger.
- **Fonts by file.** Inter ships in `fonts/` and is set once with `cm.font`.
- **Sound that follows the picture.** The sound is not attached to `emit` calls.
  `sound/` reads the film's timeline, and recomputes the Engine's own spring and
  stagger to land each cue where the motion is: a ball's rumble pans with it, a
  glass tick lands on each letter, each swap's knock is pitched by its bar.

## The parts

```text
main.py      connects the parts; render, sound, stills
story.py     what happens, beat by beat, and how long each lasts
scenes.py    what each moment looks like, and where things sit
look.py      type, colour, and every headline
sound/       the sound track, which never imports Codimate
    cues.py         the cue sheet: which sound, when, how loud, where
    follow.py       the picture's motion re-derived: spring, stagger, the sort
    instruments.py  keys, wood, glass, paper, a felt tip, a rolling ball
    room.py         the mix bus and one small reverb
    master.py       the WAV, then -14 LUFS and -1 dB true peak via ffmpeg
    dsp.py          noise, filters, envelopes, panning, pitch names
fonts/       Inter (SIL Open Font License, see fonts/LICENSE.txt)
```

Needs a Codimate with `cm.text` (newer than 0.4.0) and `ffmpeg`.
