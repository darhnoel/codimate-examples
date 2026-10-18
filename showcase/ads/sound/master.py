"""Out to a file, then mastered: glue, loudness and true peak, the way
YouTube and Facebook expect them."""

from __future__ import annotations

import json
import subprocess
import wave
from pathlib import Path

import numpy as np

from .dsp import SR

LOUDNESS = "I=-14:TP=-1:LRA=11"  # -14 LUFS, true peaks under -1 dB
GLUE = "acompressor=threshold=-20dB:ratio=2:attack=8:release=120:makeup=1"


def write_wav(path: Path, stereo: np.ndarray, rng=None) -> None:
    """16-bit PCM with triangular dither, peaking at -3 dBFS."""
    rng = rng or np.random.default_rng(0)
    peak = np.abs(stereo).max() or 1.0
    scaled = stereo / peak * 10 ** (-3 / 20) * 32767
    scaled += rng.uniform(-0.5, 0.5, scaled.shape) + rng.uniform(
        -0.5, 0.5, scaled.shape
    )
    pcm = np.clip(np.round(scaled), -32768, 32767).astype("<i2")
    with wave.open(str(path), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(SR)
        out.writeframes(pcm.tobytes())


def master(raw: Path, out: Path, ffmpeg: str = "ffmpeg") -> dict:
    """Light compression, then loudness normalised in two passes, so the level
    is measured rather than guessed, then a limiter. Returns the measurement."""
    measured = _measure(raw, ffmpeg)
    normalise = (
        f"loudnorm={LOUDNESS}:linear=true"
        f":measured_I={measured['input_i']}:measured_TP={measured['input_tp']}"
        f":measured_LRA={measured['input_lra']}"
        f":measured_thresh={measured['input_thresh']}"
        f":offset={measured['target_offset']}"
    )
    chain = f"{GLUE},{normalise},alimiter=limit=0.89:level=false,aresample={SR}"
    subprocess.run(
        [ffmpeg, "-v", "error", "-y", "-i", str(raw), "-af", chain]
        + ["-c:a", "pcm_s16le", str(out)],
        check=True,
    )
    return measured


def _measure(raw: Path, ffmpeg: str) -> dict:
    """ffmpeg's loudness reading of ``raw`` after the glue, as a dict."""
    report = subprocess.run(
        [ffmpeg, "-hide_banner", "-nostats", "-i", str(raw)]
        + ["-af", f"{GLUE},loudnorm={LOUDNESS}:print_format=json", "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stderr
    return json.loads(report[report.rindex("{") : report.rindex("}") + 1])
