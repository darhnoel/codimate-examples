"""The spoken and visual beats in the area lesson."""

from geometry import AreaLayout

CAPTIONS = {
    "ask": r"\text{Why is a rectangle } a \times b \text{?}",
    "stack": r"\text{Stack lines of length } a",
    "rect": r"\text{The stack is the area}",
    "slide": r"\text{Slide it, the area stays}",
    "cut": r"\text{Cut it in two}",
    "triangle": r"\text{Half is a triangle}",
    "trap": r"\text{Stop the lines at } c",
    "trap_copy": r"\text{Add a flipped copy}",
    "trap_area": r"\text{Half is a trapezoid}",
    "rings": r"\text{Lines of length } 2\pi r",
    "roll": r"\text{Roll each into a ring}",
    "circle": r"\text{The rings fill a circle}",
    "curve": r"\text{Now a curved edge}",
    "strips": r"\text{Strips under the curve}",
    "sum": r"\text{Add them up}",
    "thinner": r"\text{Thinner strips fit better}",
    "integral": r"\text{Infinitely thin strips}",
}

FORMULAS = {
    "rect": r"\text{area} = a \times b",
    "slide": r"\text{area} = \text{base} \times \text{height} = a \times b",
    "triangle": r"\text{triangle} = \frac{1}{2}\, a \times h",
    "trap_copy": r"\text{base} \times \text{height} = (a + c) \times h",
    "trap_area": r"\text{trapezoid} = \frac{1}{2}\,(a + c) \times h",
    "rings": r"\frac{1}{2} \times 2\pi r \times r",
    "circle": r"\text{circle} = \frac{1}{2} \times 2\pi r \times r = \pi r^{2}",
    "sum": r"\text{area} \approx \sum f(x)\,\Delta x",
    "thinner": r"\text{area} \approx \sum f(x)\,\Delta x",
    "integral": r"\text{area} = \int_a^b f(x)\,dx",
}

STACKED = (
    "stack",
    "rect",
    "slide",
    "cut",
    "triangle",
    "trap",
    "trap_copy",
    "trap_area",
)
CURVED = ("curve", "strips", "sum", "thinner", "integral")
COUNTS = (6, 12, 24, 48, 96)
ROLL_STEPS = 36
CURVE_STEPS = 30
TIMING = {"erase": 0.5, "change": 1.0, "hold": 2.4, "drop": 0.08, "bend": 0.05}


class AreaStory:
    """Produce the area lesson's states and named events."""

    def __init__(self, layout: AreaLayout = AreaLayout()):
        self.layout = layout

    def initial_state(self):
        """Return fresh state so each build starts at the first scene."""
        return {
            "stage": "ask",
            "caption": None,
            "formula": None,
            "placed": 1,
            "shear": 0.0,
            "top": self.layout.base_length,
            "copy": 0.0,
            "circle": 0.0,
            "unroll": 1.0,
            "drawn": 0.0,
            "count": 0,
        }

    def __call__(self, state, emit):
        self._step(state, emit, "ask")
        self._say(state, emit, "stack")
        emit("change")
        for placed in range(2, self.layout.line_count + 1):
            state["placed"] = placed
            emit("drop")
        emit("hold")
        self._step(state, emit, "rect")
        self._step(state, emit, "slide", shear=self.layout.shear)
        self._step(state, emit, "cut", top=0, copy=1.0)
        self._step(state, emit, "triangle", copy=0.0)
        self._step(state, emit, "trap", top=self.layout.top_length)
        self._step(state, emit, "trap_copy", copy=1.0)
        self._step(state, emit, "trap_area", copy=0.0)
        self._step(state, emit, "rings", circle=1.0)
        self._say(state, emit, "roll")
        emit("change")
        for index in range(1, ROLL_STEPS + 1):
            state["unroll"] = 1 - index / ROLL_STEPS
            emit("bend")
        emit("hold")
        self._step(state, emit, "circle")
        self._say(state, emit, "curve")
        emit("change")
        for index in range(1, CURVE_STEPS + 1):
            state["drawn"] = index / CURVE_STEPS
            emit("bend")
        emit("hold")
        self._step(state, emit, "strips", count=COUNTS[0])
        self._step(state, emit, "sum")
        for count in COUNTS[1:]:
            self._step(state, emit, "thinner", count=count)
        self._step(state, emit, "integral")

    def _say(self, state, emit, stage):
        """Erase changing words and set the words for the next moment."""
        caption = CAPTIONS[stage]
        formula = FORMULAS.get(stage)
        if state["caption"] not in (None, caption) or state["formula"] not in (
            None,
            formula,
        ):
            if state["caption"] != caption:
                state["caption"] = None
            if state["formula"] != formula:
                state["formula"] = None
            emit("erase")
        state.update(stage=stage, caption=caption, formula=formula)

    def _step(self, state, emit, stage, **changes):
        self._say(state, emit, stage)
        state.update(changes)
        emit("change")
        emit("hold")
