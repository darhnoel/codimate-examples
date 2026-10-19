"""A film's sound, synthesised: no recordings anywhere.

- ``instruments``: each sound source: keys, wood, glass, paper, a felt tip.
- ``room``: the mix bus and the one small room every cue is sent to.
- ``master``: the WAV file, then -14 LUFS and -1 dB true peak for the web.
- ``timeline``: the film's beats, asked by name.
- ``dsp``: noise, filters, envelopes, panning, pitch names.

A film writes its own cue sheet: which instrument, at which beat, how loud.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .master import master, write_wav
from .room import Track
from .timeline import Beats


def soundtrack(timeline, duration: float, cue_sheet, out_dir: Path, seed: int = 4):
    """Run ``cue_sheet(track, beats, rng)`` over the film's timeline, mix it in
    the room, write it and master it. Returns the mastered WAV's path."""
    rng = np.random.default_rng(seed)
    track = Track(duration)
    cue_sheet(track, Beats(timeline), rng)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw, mastered = out_dir / "cues.raw.wav", out_dir / "cues.wav"
    write_wav(raw, track.mix(rng))
    master(raw, mastered)
    return mastered
