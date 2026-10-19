"""Putting a film's picture and sound together."""

from __future__ import annotations

import subprocess
from pathlib import Path


def mux(video: Path, track: Path, duration: float, fps: float) -> None:
    """Lay ``track`` under ``video`` in place, both cut to ``duration``."""
    out = video.with_name(f"{video.stem}.sound{video.suffix}")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(track)]
        + ["-map", "0:v", "-map", "1:a", "-frames:v", str(round(duration * fps))]
        + ["-t", f"{duration:.3f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k"]
        + ["-movflags", "+faststart", str(out)],
        check=True,
    )
    out.replace(video)
