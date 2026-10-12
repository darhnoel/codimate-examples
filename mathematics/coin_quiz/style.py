"""The canvas and the colours: vertical 9:16 for Reels and TikTok."""

import codimate as cm

cm.canvas(1080, 1920)
W, H = cm.width(), cm.height()
FPS = 60

INK, DIM = "#f2f4f8", "#8d97ab"  # text, and quieter text
BLUE, GREEN, YELLOW, RED = "#58c4dd", "#3ccf7e", "#ffd166", "#ff5d5d"
BORDER, TRACK = "#5a6785", "#2f3a52"  # an answer letter's ring; A's faint path
TIMER_BACK, ON_YELLOW = "#3a4663", "#1a1a1a"  # the empty ring; text on a bright fill


def fit(text, size, room=W - 80):
    """The largest size at or below `size` that keeps `text` within `room`.
    Khmer often runs longer than English, so a line shrinks rather than overflows."""
    while size > 20 and cm.measure(text, size=size)[0] > room:
        size -= 1
    return size
