"""The film's sound track: every cue synthesised, laid on the film's own
timeline, then mastered.

    path = sound.soundtrack(film.timeline(), film.duration, places, out_dir)

Nothing here is a recording, and nothing here imports Codimate: it is handed the
timeline as plain ``(start, length, name)`` beats and the layout as ``Places``.
One track laid on that timeline, rather than a clip per ``emit``, because a cue
often belongs *after* its beat starts (a word lands, a ball settles).

The parts, from the top down:

- ``cues``: the cue sheet. Which sound, at which beat, how loud, where.
- ``follow``: the picture's motion re-derived: the spring, the stagger, the sort.
- ``instruments``: each sound source: keys, wood, glass, paper, a felt tip, a ball.
- ``room``: the mix bus and the one small room every cue is sent to.
- ``master``: the WAV file, then loudness and peaks for the web.
- ``dsp``: noise, filters, envelopes, panning, pitch names.
"""

from __future__ import annotations

from pathlib import Path

from .cues import Places, score
from .master import master, write_wav

__all__ = ["Places", "score", "soundtrack"]


def soundtrack(timeline, duration: float, places: Places, out_dir: Path) -> Path:
    """Write the raw cue track and its mastered copy; return the master."""
    out_dir.mkdir(parents=True, exist_ok=True)
    raw, mastered = out_dir / "cues.raw.wav", out_dir / "cues.wav"
    write_wav(raw, score(timeline, duration, places))
    master(raw, mastered)
    return mastered
