"""A deck of slides, made into a narrated film.

    deck = Deck([Title(...), Statement(...), ...], voice=Voice(cache))
    deck.render("talk.mp4", theme="dark")

How it moves, for every slide alike:

- a slide arrives on a **cut**: the previous one is gone, never faded;
- each part arrives as its narrated line starts: it **cuts in** a few pixels
  low and **settles** up into place, solid the whole time;
- a part holds until its line ends, plus a breath; with no line, long enough
  to read it;
- every beat is a whole number of frames (60 fps), so the voice and the words
  land on the same frame.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import codimate as cm
import numpy as np

from ..film import mux
from ..sound import soundtrack
from .look import HEIGHT, MEDIUM, THEMES, WIDTH, Type, face, gap, use

CAPTION = Type(36, MEDIUM)

FPS = 60
SETTLE = 0.45  # seconds a part takes to rise into place
DROP = 14  # pixels below its place a part arrives
BREATH = 0.5  # after a line ends, before the next part
BETWEEN = 0.9  # after a slide's last part, before the next slide
VOICE = 0.05  # a line starts this long after its part arrives
CAPTION_Y = 975  # captions sit here, below everything a slide draws
CAPTION_WIDTH = 1500
CAPTION_WORDS = 5  # the most words a caption shows at once


def frames(seconds: float) -> float:
    return round(seconds * FPS) / FPS


class Paced(cm.Timing):
    """Each beat says its own length; a beat without one is a cut."""

    def __init__(self):
        super().__init__(default=0.0, opening=frames(0.6), final_hold=frames(2.0))

    def for_event(self, event) -> float:
        return frames(float(event.data.get("seconds", 0.0)))


@dataclass
class Showing:
    slide: int = -1  # which slide is up
    parts: int = 0  # how many of its parts have arrived
    dy: float = 0.0  # how far below its place the newest part still is
    caption: tuple = ()  # the caption line on screen, word by word
    line: int = 0  # which caption line it is, so a new one is a new shape
    spoken: int = -1  # the word being said in it
    t: float = 0.0  # seconds since the newest part arrived, for one that moves


def _out(u: float) -> float:
    """The settle's ease: fast, then gently into place."""
    return 1 - (1 - min(max(u, 0.0), 1.0)) ** 3


def _caption_lines(words, measure):
    """The words of a line, broken into caption lines of at most
    ``CAPTION_WORDS`` words, each fitting the width."""
    lines, line = [], []
    for word in words:
        trial = gap().join(w for w, _, _ in line + [word])
        if line and (len(line) >= CAPTION_WORDS or measure(trial) > CAPTION_WIDTH):
            lines.append(line)
            line = []
        line.append(word)
    return lines + ([line] if line else [])


@dataclass
class Deck:
    slides: list
    voice: object = None  # a studio.voice.Voice, or None for a silent deck
    language: str = "en"  # "ja" sets the deck in Japanese (see look.use)
    clips: dict = field(default_factory=dict)
    _cache: dict = field(default_factory=dict, repr=False)

    def _speak(self):
        lines = [
            part.say for slide in self.slides for part in slide.parts() if part.say
        ]
        if self.voice and lines and not self.clips:
            self.clips = self.voice.speak(lines)

    def _hold(self, part) -> float:
        clip = self.clips.get(part.say)
        if clip:
            return max(clip.seconds - SETTLE, 0) + BREATH
        return 1.4  # no narration: time to read a short line

    def _tell(self, showing, emit):
        """Every part of every slide, on one clock. Beats are lengths between
        frame-rounded moments on that clock, so however many there are, the
        captions never drift from the voice."""
        clock = [0.0]  # seconds from the first slide

        def until(at, name="hold", **changes):
            for key, value in changes.items():
                setattr(showing, key, value)
            emit(name, seconds=frames(at) - frames(clock[0]))
            clock[0] = at

        for k, slide in enumerate(self.slides):
            parts = slide.parts()
            for n, part in enumerate(parts, start=1):
                start = clock[0]
                showing.slide, showing.parts, showing.dy = k, n, DROP
                showing.caption, showing.spoken, showing.t = (), -1, 0.0
                emit("enter", kind=type(slide).__name__, first=n == 1)
                clip = self.clips.get(part.say)
                words = [] if clip is None else list(clip.words)
                # a part that moves is redrawn every frame, each frame a cut
                ticks = {k / FPS for k in range(1, round(part.moves * FPS) + 1)}
                moments = sorted({SETTLE} | {VOICE + w[1] for w in words} | ticks)
                for at in moments:  # the settle, cut wherever a word lands in it
                    name = "settle" if at <= SETTLE else "hold"
                    until(start + at, name, dy=DROP * (1 - _out(at / SETTLE)))
                    if at in ticks:
                        showing.t = at
                        emit("tick")
                    self._say(showing, emit, words, at - VOICE)
                end = (VOICE + clip.seconds) if clip else 1.4
                end = max(end, SETTLE, part.moves)
                if clip:
                    until(start + end)
                    showing.caption, showing.spoken = (), -1
                    emit("quiet")
                think = getattr(slide, "think", 0) if n == 1 and len(parts) > 1 else 0
                until(start + end + BREATH + think)
            until(clock[0] + BETWEEN)

    def _say(self, showing, emit, words, at):
        """Put the caption at the word said at ``at`` seconds into the line."""
        lines = self._lines(words)
        for number, line in enumerate(lines):
            for index, word in enumerate(line):
                if abs(word[1] - at) < 1e-6:
                    if showing.caption != tuple(w[0] for w in line):
                        showing.line += 1
                    showing.caption = tuple(w[0] for w in line)
                    showing.spoken = index
                    emit("word")
                    return

    def _lines(self, words):
        key = tuple(tuple(w) for w in words)
        if key not in self._cache:
            self._cache[key] = _caption_lines(
                words, lambda text: cm.measure(text, CAPTION.size, face(CAPTION.font))[0]
            )
        return self._cache[key]

    def film(self, theme: str = "light") -> cm.Explanation:
        """The deck as a film, in ``theme`` (light or dark)."""
        use(self.language)
        self._speak()
        cm.canvas(WIDTH, HEIGHT)
        colours = THEMES[theme]

        def view(frame):
            showing = frame.state
            scene = cm.Scene()
            back = scene.rect("page", w=WIDTH, h=HEIGHT, at=(WIDTH / 2, HEIGHT / 2))
            back.fill(colours.page).on(layer=-10)
            if showing.slide >= 0:
                parts = self.slides[showing.slide].parts()[: showing.parts]
                first = max((n for n, p in enumerate(parts) if p.alone), default=0)
                for n, part in enumerate(parts[first:], start=first + 1):
                    newest = n == len(parts)
                    key, dy = ("slide", showing.slide, n), showing.dy if newest else 0
                    if part.moves:  # an older part stays at its last frame
                        t = showing.t if newest else part.moves
                        part.draw(scene, key, colours, dy, t)
                    else:
                        part.draw(scene, key, colours, dy)
            _caption(scene, showing, colours)
            return scene

        motion = []  # the settle's ease is already in its steps
        return cm.explain(
            trace=cm.trace(self._tell, Showing()),
            view=view,
            motion=motion,
            timing=Paced(),
        )

    def _sheet(self):
        """Each part's line, said as it arrives. No cue sounds: only the voice."""
        lines = [part.say for slide in self.slides for part in slide.parts()]

        def sheet(track, beats, rng):
            enters = [(at, length) for at, length, name in beats if name == "enter"]
            for (at, _), say in zip(enters, lines):
                clip = self.clips.get(say)
                if clip:
                    track.add(at + 0.05, _read(clip.path), db=-2, wet=0.04)

        return sheet

    def render(self, out: Path, theme: str = "light") -> Path:
        """Render the film with its narration, mastered, to ``out``."""
        out = Path(out)
        film = self.film(theme)
        out.parent.mkdir(parents=True, exist_ok=True)
        film.render(str(out), fps=FPS, scale=1.0)
        track = soundtrack(
            film.timeline(),
            film.duration,
            self._sheet(),
            out.parent / f"{out.stem}-sound",
        )
        mux(out, track, film.duration, FPS)
        return out


def _read(path: Path) -> np.ndarray:
    import wave

    with wave.open(str(path)) as clip:
        pcm = np.frombuffer(clip.readframes(clip.getnframes()), "<i2")
    return pcm.astype(float) / 32768


def _caption(scene, showing, theme):
    """The caption line, word by word: said words in ink, the word being said
    in the accent colour, the words still to come muted."""
    if not showing.caption:
        return
    font = face(CAPTION.font)
    space = cm.measure("a a", CAPTION.size, font)[0]
    space -= cm.measure("aa", CAPTION.size, font)[0]
    space *= len(gap())  # no space between Japanese phrases
    widths = [cm.measure(word, CAPTION.size, font)[0] for word in showing.caption]
    left = WIDTH / 2 - (sum(widths) + space * (len(widths) - 1)) / 2
    for k, (word, width) in enumerate(zip(showing.caption, widths)):
        if k == showing.spoken:
            colour = theme.accent
        else:
            colour = theme.ink if k < showing.spoken else theme.muted
        at = (left + width / 2, CAPTION_Y)
        shape = scene.text(
            ("caption", showing.line, k),
            word,
            size=CAPTION.size,
            font=font,
            at=at,
        )
        shape.fill(colour)
        left += width + space
