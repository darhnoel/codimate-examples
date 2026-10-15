"""The beats of the film: what is written, and what the mail does.

Each beat names the words on screen, slot by slot. A slot whose words change is
wiped first, then the new words are written on as the picture moves.
"""

from mail import MAIL

SCORES = {"plabel": r"\text{precision}", "rlabel": r"\text{recall}"}

WORDS = {
    "sealed": {"caption": r"\text{20 sealed emails}"},
    "decides": {"caption": r"\text{The detector decides}"},
    "inside": {"caption": r"\text{Now look inside}"},
    "names": {
        "caption": r"\text{Right and wrong calls}",
        "tag1": r"\text{4 caught (TP)}",
        "tag2": r"\text{1 false alarm (FP)}",
        "tag3": r"\text{1 missed (FN)}",
    },
    "precision": {
        "caption": r"\text{Precision}",
        "question": r"\text{When it says spam, is it?}",
        "value": r"= \frac{4}{5}",
    },
    "recall": {
        "caption": r"\text{Recall}",
        "question": r"\text{Of all the spam, how much is caught?}",
        "value": r"= \frac{4}{5}",
    },
    "slider": {"caption": r"\text{Move the threshold}"},
    "relaxed": {"caption": r"\text{Higher threshold}"},
    "relaxed_score": {
        "caption": r"\text{Higher threshold}",
        **SCORES,
        "pvalue": r"\frac{2}{2}",
        "rvalue": r"\frac{2}{5}",
    },
    "strict": {"caption": r"\text{Lower threshold}"},
    "strict_score": {
        "caption": r"\text{Lower threshold}",
        **SCORES,
        "pvalue": r"\frac{5}{10}",
        "rvalue": r"\frac{5}{5}",
    },
    "choose": {
        "caption": r"\text{You can't max both}",
        "question": r"\text{Choose the mistake that hurts less}",
        **SCORES,
        "pvalue": r"\frac{5}{10}",
        "rvalue": r"\frac{5}{5}",
    },
    "recap": {
        "caption": r"\text{Remember}",
        "recap1": r"\mathbf{Precision}",
        "recap2": r"\text{Of what I flagged, how much was right?}",
        "recap3": r"\mathbf{Recall}",
        "recap4": r"\text{Of what was there, how much did I find?}",
    },
}
SLOTS = sorted({slot for words in WORDS.values() for slot in words})

TIMING = {
    "erase": 0.5,
    "change": 1.0,
    "hold": 2.2,
    "rewind": 1.2,
    "step": 0.6,  # a slow email steps up into the gate
    "scan": 0.7,  # the scan line crosses it
    "exit": 0.5,  # it drops out of the bottom of the gate
    "drop": 0.6,  # and moves across into its pile
    "fast": 0.12,  # each of those, for the rest of the mail
}
SLOW = 3  # emails that go through slowly, so the rule reads


def initial_state():
    return {
        "stage": "sealed",
        "words": {slot: None for slot in SLOTS},
        "setting": "medium",
        "passed": 0,  # emails through the gate
        "at_gate": False,  # the next email is in the gate
        "out": None,  # the email just below the gate, on its way to a pile
        "scan": 0.0,  # the scan line: 0 at the top of the gate, 1 at the bottom
        "meter": 0.0,  # how suspicious the email being scanned looks
        "seen": False,  # the envelopes are see-through
        "sorted": False,  # spam first in each pile
        "focus": None,  # "spam": only the spam pile; "red": only the spam mail
        "fraction": None,  # "precision", "recall", or "both", small
        "slider": False,
    }


def story(state, emit):
    def say(stage):
        """Wipe the words that are about to change, then move on to `stage`."""
        words = {slot: WORDS[stage].get(slot) for slot in SLOTS}
        old = state["words"]
        if any(old[slot] not in (None, words[slot]) for slot in SLOTS):
            state["words"] = {
                slot: old[slot] if old[slot] == words[slot] else None for slot in SLOTS
            }
            emit("erase")
        state.update(stage=stage, words=words)

    def step(stage, **changes):
        say(stage)
        state.update(changes)
        emit("change")
        emit("hold")

    def beats(stage, *moves, words_at=0):
        """One frame change as separate beats, one kind of motion each: e.g.
        fold the old fraction, then move the piles, then build the new one.
        The words change with beat `words_at`."""
        for index, changes in enumerate(moves):
            if index == words_at:
                say(stage)
            state.update(changes)
            emit("change")
        emit("hold")

    def run(slow):
        """All the mail through the gate, the first `slow` of it slowly."""
        for number in range(len(MAIL)):
            pace = number < slow
            state["at_gate"] = True
            emit("step" if pace else "fast")
            # The laser sweeps down the email as the meter fills to its score.
            state.update(scan=1.0, meter=MAIL[number].score)
            emit("scan" if pace else "fast")
            state.update(at_gate=False, out=number, scan=0.0, meter=0.0)
            emit("exit" if pace else "fast")
            state.update(out=None, passed=number + 1)
            emit("drop" if pace else "fast")

    say("sealed")
    emit("change")
    run(SLOW)
    emit("hold")
    step("decides")
    step("inside", seen=True, sorted=True)
    step("names")
    # Inbox out and the spam pile to the middle, then its fraction below it.
    beats("precision", {"focus": "spam"}, {"fraction": "precision"})
    # Fold that fraction, keep only the spam mail, then build recall's.
    beats("recall", {"fraction": None}, {"focus": "red"}, {"fraction": "recall"})
    # Fold, put the piles back, and only then bring in the slider.
    beats("slider", {"fraction": None}, {"focus": None}, {"slider": True}, words_at=2)
    for setting in ("relaxed", "strict"):
        say(setting)
        if state["fraction"]:
            state["fraction"] = None  # fold the last fractions first
            emit("change")
        # The same mail goes round again, sealed, so the detector cannot peek.
        state.update(passed=0, seen=False)
        emit("rewind")
        state["setting"] = setting
        emit("change")
        run(0)
        state["seen"] = True  # then look inside again
        emit("change")
        step(setting + "_score", fraction="both")
    step("choose")
    beats("recap", {"fraction": None}, {"slider": False}, words_at=1)
