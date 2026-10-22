"""Speaks lines with Kokoro. Run inside .venv-voice, by ``studio.voice``:

    .venv-voice/bin/python studio/voice_worker.py jobs.json

``jobs.json`` is ``{"voice": "af_heart", "speed": 1.0, "lines": {path: text}}``.
Each line is written to its path as a 24 kHz mono WAV. The model loads once.
"""

import json
import re
import sys

import numpy as np
import soundfile
from kokoro import KPipeline


def main(jobs_path):
    jobs = json.load(open(jobs_path))
    # A voice's first letter is its language: a = American, b = British, j = Japanese.
    pipeline = KPipeline(lang_code=jobs["voice"][0], repo_id="hexgrad/Kokoro-82M")
    for path, text in jobs["lines"].items():
        chunks, words, offset = [], [], 0.0
        for result in pipeline(text, voice=jobs["voice"], speed=jobs["speed"]):
            audio = np.asarray(result.audio)
            chunks.append(audio)
            seconds = len(audio) / 24_000
            if result.tokens is None:  # Japanese: Kokoro gives no timings
                words += _phrases(result.graphemes, offset, seconds)
            else:
                words += _words(result.tokens, offset)
            offset += seconds
        soundfile.write(path, np.concatenate(chunks), 24_000)
        with open(path.replace(".wav", ".json"), "w") as out:
            json.dump(words, out)
        print(f"spoke {path}", flush=True)


def _words(tokens, offset):
    """``[word, start, end]`` in seconds from the line's start. Tokens with no
    space between them are one word to a reader: "idea:", "I/O", "Kahneman's"."""
    words, joined = [], False
    for token in tokens:
        start = token.start_ts
        end = token.end_ts if token.end_ts is not None else start
        if words and (joined or not any(ch.isalnum() for ch in token.text)):
            words[-1][0] += token.text
            if end is not None:
                words[-1][2] = offset + end
        else:
            if start is None:
                start = words[-1][2] - offset if words else 0.0
                end = start
            words.append([token.text, offset + start, offset + end])
        joined = token.whitespace == ""
    return words


PHRASE = 8  # the most characters a phrase holds before it is split


def _phrases(text, offset, seconds):
    """``[phrase, start, end]`` for text with no word timings (Japanese): phrases
    end at punctuation or after ``PHRASE`` characters, and the chunk's seconds are
    shared out by how many characters each phrase has. An estimate, close enough
    for a caption to follow the voice."""
    pieces = []
    for part in re.findall(r"[^、。，．！？!?]+[、。，．！？!?」』）]*", text.strip()):
        pieces += [part[k:k + PHRASE] for k in range(0, len(part), PHRASE)]
    total = sum(len(p) for p in pieces) or 1
    words, at = [], offset
    for piece in pieces:
        length = seconds * len(piece) / total
        words.append([piece, at, at + length])
        at += length
    return words


if __name__ == "__main__":
    main(sys.argv[1])
