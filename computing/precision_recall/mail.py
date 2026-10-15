"""The 20 emails, in the order they reach the detector, and the numbers shown.

Nothing here draws. Each email has a spam score the detector reads; it calls an
email spam when the score reaches its setting. The scores are chosen, not random,
so the film's fractions come out as planned:

    relaxed   2 called spam, both real       precision 2/2    recall 2/5
    medium    4 real, 1 good by mistake      precision 4/5    recall 4/5
    strict    all 5 spam and 5 good          precision 5/10   recall 5/5
"""

# (spam?, score), in arrival order. The first three show the rule slowly: good
# mail to the inbox, spam to spam, good mail to the inbox.
ARRIVALS = (
    (False, 0.10), (True, 0.90), (False, 0.05), (False, 0.40), (True, 0.70),
    (False, 0.15), (False, 0.65), (False, 0.20), (True, 0.95), (False, 0.08),
    (False, 0.35), (True, 0.30), (False, 0.12), (False, 0.38), (False, 0.03),
    (True, 0.80), (False, 0.18), (False, 0.33), (False, 0.06), (False, 0.22),
)  # fmt: skip

# How strict the detector is: the score at which it calls an email spam.
THRESHOLD = {"relaxed": 0.85, "medium": 0.6, "strict": 0.28}


class Email:
    def __init__(self, number, spam, score):
        self.number = number  # its place in the queue
        self.spam = spam
        self.score = score

    def flagged(self, setting):
        """Whether the detector calls it spam at this setting."""
        return self.score >= THRESHOLD[setting]


MAIL = [Email(number, spam, score) for number, (spam, score) in enumerate(ARRIVALS)]


def precision(setting):
    """Of what it called spam, how much was spam: (right, called)."""
    called = [m for m in MAIL if m.flagged(setting)]
    return sum(m.spam for m in called), len(called)


def recall(setting):
    """Of all the spam, how much it called spam: (caught, all spam)."""
    spam = [m for m in MAIL if m.spam]
    return sum(m.flagged(setting) for m in spam), len(spam)
