"""Precision and recall, with 20 sealed emails and a spam detector.

    .venv/bin/python computing/precision_recall/main.py

Sealed mail comes out of the background one email at a time. The detector scans
each and sends it to spam or the inbox. Then the envelopes turn see-through, and
the detector's calls can be checked: precision looks only at what it called spam,
recall only at the real spam. Making it more relaxed or more strict shows the two
pull against each other.

The numbers are in mail.py, the beats in story.py and the drawing in view.py.
"""

import codimate as cm

from story import TIMING, initial_state, story
from view import view

cm.canvas(1080, 1920)  # vertical, 9:16, for TikTok and Reels

cm.explain(
    trace=cm.trace(story, initial_state()),
    view=view,
    timing=cm.Timing(events=TIMING, opening=0.3, final_hold=1.5),
).render("results/precision_recall.mp4", fps=30, scale=1.0)

print("wrote results/precision_recall.mp4")
