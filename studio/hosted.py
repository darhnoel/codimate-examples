"""Narration from a hosted voice, with the same Clips as Voice.

    voice = Hosted(cache, "edge", "km-KH-PisethNeural")   # Microsoft Edge, free
    voice = Hosted(cache, "kiri", "Oudom")                # Kiri TTS, needs a key
    clips = voice.speak(["សួស្តី។"])                       # {text: Clip}

Edge runs ``edge-tts`` in the voice environment (``.venv-voice``). Kiri's key
is ``KIRI_API_KEY`` from the environment, or from the gitignored ``.env`` of
codimate-examples next to this repository. Both send the words to the service.
Lines are cached by their words, service, voice and speed, so a line is
fetched once.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from .voice import PYTHON, RATE, Clip, _seconds, _valid_wav

ROOT = Path(__file__).resolve().parents[1]
KIRI = "https://api.kiritts.com/v1/audio/speech"


class Hosted:
    def __init__(self, cache: Path, service: str, name: str, speed: float = 1.0):
        if service not in ("edge", "kiri"):
            raise ValueError(f"no hosted voice {service!r}; use edge or kiri")
        self.cache, self.service = Path(cache), service
        self.name, self.speed = name, speed

    def _path(self, text: str) -> Path:
        key = f"{self.service}|{self.name}|{self.speed}|{text}"
        return self.cache / f"{hashlib.sha1(key.encode()).hexdigest()[:16]}.wav"

    def speak(self, lines) -> dict:
        """Every line as a Clip, fetching only the ones not already cached."""
        lines = [line for line in dict.fromkeys(lines) if line.strip()]
        self.cache.mkdir(parents=True, exist_ok=True)
        for line in lines:
            if not _valid_wav(self._path(line)):
                self._fetch(line)
        return {
            line: Clip(self._path(line), _seconds(self._path(line)))
            for line in lines
        }

    def _fetch(self, text: str) -> None:
        with tempfile.TemporaryDirectory(dir=self.cache) as folder:
            mp3 = Path(folder) / "line.mp3"
            if self.service == "edge":
                rate = f"{round((self.speed - 1) * 100):+d}%"
                command = [
                    str(PYTHON), "-m", "edge_tts", "--voice", self.name,
                    f"--rate={rate}", "--text", text, "--write-media", str(mp3),
                ]
                # Edge now and then sends no audio for a line it reads fine
                # a moment later, so try a few times before giving up.
                for attempt in range(4):
                    if subprocess.run(command, capture_output=True).returncode == 0:
                        break
                    time.sleep(1 + 2 * attempt)
                else:
                    raise RuntimeError(f"edge sent no audio for {text!r}")
            else:
                mp3.write_bytes(_kiri(text, self.name, self.speed))
            # Never cache an error page: the cache is keyed on the text.
            if not mp3.exists() or mp3.stat().st_size < 1024:
                raise RuntimeError(f"{self.service} sent almost nothing for {text!r}")
            converted = Path(folder) / "line.wav"
            subprocess.run(
                [
                    "ffmpeg", "-v", "error", "-y", "-i", str(mp3),
                    "-ar", str(RATE), "-ac", "1", str(converted),
                ],
                check=True,
            )
            if not _valid_wav(converted):
                raise RuntimeError(f"{self.service} sent invalid audio for {text!r}")
            converted.replace(self._path(text))


def _kiri(text: str, name: str, speed: float) -> bytes:
    body = {
        "model": "kiritts", "input": text, "voice": name,
        "response_format": "mp3", "speed": speed,
    }
    request = urllib.request.Request(
        KIRI,
        data=json.dumps(body).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {_kiri_key()}",
            "Content-Type": "application/json",
            # Cloudflare blocks urllib's own User-Agent with a 403 that reads
            # like a bad key.
            "User-Agent": "codimate-templates/1.0",
            "Accept": "*/*",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as reply:
            return reply.read()
    except urllib.error.HTTPError as failure:
        detail = failure.read()[:400].decode("utf8", "replace")
        raise RuntimeError(f"Kiri refused ({failure.code}): {detail}") from None


def _kiri_key() -> str:
    token = os.environ.get("KIRI_API_KEY")
    if token:
        return token
    env = ROOT.parent / "codimate-examples" / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "KIRI_API_KEY":
                return value.strip().strip("\"'")
    raise RuntimeError(f"no Kiri key: set KIRI_API_KEY, or put it in {env}")
