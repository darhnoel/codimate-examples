"""A small, reusable entry point for building the area explainer."""

from pathlib import Path

import codimate as cm

from geometry import AreaLayout
from story import AreaStory, TIMING
from view import AreaView

FPS = 30
CANVAS = (1080, 1920)


class AreaFilm:
    """Build and render the complete area lesson from one cohesive interface."""

    def __init__(self, layout: AreaLayout = AreaLayout()):
        self.layout = layout
        self.story = AreaStory(layout)
        self.view = AreaView(layout)

    def build(self):
        """Return the Codimate explanation without rendering a video."""
        cm.canvas(*CANVAS)
        return cm.explain(
            trace=cm.trace(self.story, self.story.initial_state()),
            view=self.view,
            timing=cm.Timing(events=TIMING, opening=0.3, final_hold=1.5),
        )

    def render(self, output: str | Path = "results/area.mp4") -> str:
        """Build the lesson and write its video at 30 frames per second."""
        return self.build().render(str(output), fps=FPS, scale=1.0)
