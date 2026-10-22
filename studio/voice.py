"""Narration, spoken by a local voice model (Kokoro), free and offline.

    voice = Voice(cache)               # af_heart, a warm American English voice
    clips = voice.speak(["Hello.", "Two systems."])   # {text: Clip}
    clips["Hello."].seconds, clips["Hello."].path

    Voice(cache, say_as={"NISA": "/nˈisɑ/"})   # a word said as these phonemes

``say_as`` fixes how a word is said (an acronym read as a word, a name) while
the captions still show it as written.

Kokoro needs PyTorch, so it lives in its own environment (``.venv-voice`` at
the top of this repository) and runs as a separate process; films never import
it. Lines are cached by their words, voice and speed: a film rebuilds without
speaking again unless a line changed.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv-voice" / "bin" / "python"
WORKER = Path(__file__).resolve().parent / "voice_worker.py"
RATE = 48_000
# Japanese words said the Japanese way, for say_as: にさ, つみたて, イデコ
JAPANESE = {
    "NISA": "/nˈisɑ/",
    "Tsumitate": "/ʦumitˈɑte/",
    "tsumitate": "/ʦumitˈɑte/",
    "iDeCo": "/idˈeko/",
}


@dataclass(frozen=True)
class Clip:
    path: Path  # 48 kHz mono WAV
    seconds: float
    words: tuple = ()  # (word, start, end): when each word is said, in seconds


class Voice:
    def __init__(
        self,
        cache: Path,
        name: str = "af_heart",
        speed: float = 1.0,
        say_as: dict = None,
    ):
        self.cache, self.name, self.speed = Path(cache), name, speed
        self.say_as = say_as or {}

    def _spoken(self, text: str) -> str:
        """``text`` as Kokoro is given it: each ``say_as`` word with its phonemes."""
        for word, phonemes in self.say_as.items():
            text = re.sub(rf"\b{re.escape(word)}\b", f"[{word}]({phonemes})", text)
        return text

    def _path(self, text: str) -> Path:
        spoken = self._spoken(text)
        key = hashlib.sha1(f"{self.name}|{self.speed}|{spoken}".encode()).hexdigest()[
            :16
        ]
        return self.cache / f"{key}.wav"

    def speak(self, lines) -> dict:
        """Every line as a Clip, speaking only the ones not already cached."""
        lines = [line for line in dict.fromkeys(lines) if line.strip()]
        self.cache.mkdir(parents=True, exist_ok=True)
        missing = [line for line in lines if not self._timings(line).exists()]
        if missing:
            self._run(missing)
        return {line: self._clip(line) for line in lines}

    def _timings(self, text: str) -> Path:
        return self._path(text).with_suffix(".json")

    def _clip(self, text: str) -> Clip:
        path = self._path(text)
        words = tuple(tuple(w) for w in json.loads(self._timings(text).read_text()))
        return Clip(path, _seconds(path), words)

    def _run(self, lines) -> None:
        if not PYTHON.exists():
            raise RuntimeError(
                "narration needs the voice environment: python -m venv .venv-voice && "
                ".venv-voice/bin/pip install kokoro soundfile"
            )
        with tempfile.TemporaryDirectory() as folder:
            raw = {str(Path(folder) / f"{k}.wav"): text for k, text in enumerate(lines)}
            jobs = Path(folder) / "jobs.json"
            jobs.write_text(
                json.dumps(
                    {
                        "voice": self.name,
                        "speed": self.speed,
                        "lines": {k: self._spoken(t) for k, t in raw.items()},
                    }
                )
            )
            subprocess.run(
                [str(PYTHON), str(WORKER), str(jobs)], check=True, capture_output=True
            )
            for source, text in raw.items():  # 24 kHz in, 48 kHz out, as the films use
                Path(source).with_suffix(".json").replace(self._timings(text))
                subprocess.run(
                    [
                        "ffmpeg",
                        "-v",
                        "error",
                        "-y",
                        "-i",
                        source,
                        "-ar",
                        str(RATE),
                        "-ac",
                        "1",
                    ]
                    + [str(self._path(text))],
                    check=True,
                )


def _seconds(path: Path) -> float:
    with wave.open(str(path)) as clip:
        return clip.getnframes() / clip.getframerate()
