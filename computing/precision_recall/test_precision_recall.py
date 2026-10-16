"""`mail.py` against every fraction the film shows.

Nothing renders here.
"""

from mail import MAIL, precision, recall


def test_20_emails_of_which_5_are_spam():
    assert len(MAIL) == 20 and sum(m.spam for m in MAIL) == 5


def test_the_first_three_show_both_ways_out():
    first = [m.flagged("medium") for m in MAIL[:3]]
    assert first == [False, True, False]


def test_medium_is_four_out_of_five_both_ways():
    called = [m for m in MAIL if m.flagged("medium")]
    assert sum(m.spam for m in called) == 4 and len(called) == 5  # 1 false alarm
    assert sum(m.spam and not m.flagged("medium") for m in MAIL) == 1  # 1 missed
    assert precision("medium") == (4, 5) and recall("medium") == (4, 5)


def test_relaxed_is_always_right_but_misses_spam():
    assert precision("relaxed") == (2, 2) and recall("relaxed") == (2, 5)


def test_strict_catches_all_spam_but_blocks_good_mail():
    assert precision("strict") == (5, 10) and recall("strict") == (5, 5)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
    import support

    raise SystemExit(support.run(globals()))
