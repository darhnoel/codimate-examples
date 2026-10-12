"""Every word on the screen, in English and in Khmer.

    python mathematics/coin_quiz/main.py       English
    python mathematics/coin_quiz/main.py km    Khmer

Only the words fork: the geometry, the timing and the layout are shared, so a fix
to the picture lands in both films. Numbers and formulas stay in LaTeX; words never
go into LaTeX, because Typst would draw Khmer in a different font from the rest.

Khmer puts no spaces between its words, so a line cannot be broken just anywhere:
the Khmer question says where its lines end, with a newline.
"""

import sys

WORDS = {
    "en": {
        "out": "results/coin_quiz.mp4",
        "question": (
            "Circle A's radius is 1/3 of circle B's. "
            "A rolls around B without slipping. "
            "How many times does A turn before it is back where it started?"
        ),
        "hook": "This question broke the SAT",
        "quiz": "QUIZ",
        "answer": "ANSWER",
        "why": "WHY 4?",
        "comment": "Comment your answer!",
        "most_pick": "Most people pick 3. Are they right?",
        "watch_count": "Watch the red line. Count the turns.",
        "rescored": "4 wasn't even an option. The test was rescored.",
        "watch": "Watch the red line.",
        "gives": "Rolling gives 3. Going round gives 1 more.",
        "turns": "Turns",
        "not_back": "...and it's not back yet!",
        "back": "Back where it started. 4 turns!",
        "road_title": "1. Rolling along B's edge",
        "road_sub": "B's edge laid out straight",
        "carry_title": "2. Carried once round B, glued",
    },
    "km": {
        "out": "results/coin_quiz_km.mp4",
        "question": (
            "កាំរង្វង់ A ស្មើ 1/3 នៃកាំរង្វង់ B។\n"
            "A រមៀលទៅជុំវិញ B 1 ជុំ ដោយមិនរអិល។\n"
            "តើ A វិលជុំវិញខ្លួនបានប៉ុន្មានជុំ?"
        ),
        "hook": "សំណួរ SAT ដែលស្ទើរគ្រប់គ្នាឆ្លើយខុស!",
        "quiz": "សាកឆ្លើយ!",
        "answer": "ចម្លើយ",
        "why": "ហេតុអ្វីបានជាទៅជា 4?",
        "comment": "ខំមិន្តចែករំលែកមតិរបស់អ្នក!",
        "most_pick": "ភាគច្រើនរើស 3។ ត្រូវអត់?",
        "watch_count": "រាប់ថារង្វង់តូចវិលជុំវិញខ្លួនបានប៉ុន្មានជុំ ដោយយកខ្សែក្រហមជាគោល។",
        "rescored": "គ្មានជម្រើស 4 ទេ! SAT ត្រូវដាក់ពិន្ទុឡើងវិញ។",
        "watch": "សូមយកចិត្តទុកដាក់លើខ្សែក្រហម",
        "gives": "វិលជុំវិញខ្លួន៖ រមៀលបាន 3 ទៅជុំវិញ B ថែម 1!",
        "turns": "វិលជុំវិញខ្លួន",
        "not_back": "វិលជុំវិញខ្លួន 3 ជុំហើយ តែមិនទាន់ដល់កន្លែងដើមនៅឡើយ!",
        "back": "វិលជុំវិញខ្លួនឯង 4 ជុំហើយទើបដល់កន្លែងដើមវិញ។",
        "road_title": "1. រមៀលតាមគែម B",
        "road_sub": "លាតគែម B ឲ្យត្រង់",
        "carry_title": "2. A ជាប់នឹង B៖ ទៅជុំវិញ B 1 ជុំ មិនរមៀល!",
    },
}

_args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
LANG = _args[0] if _args else "en"
if LANG not in WORDS:
    raise SystemExit(f"no words for {LANG!r}; have {sorted(WORDS)}")
# A missing key would only fail at the moment that needs it, deep into a render.
assert WORDS[LANG].keys() == WORDS["en"].keys(), "Khmer and English differ in keys"
SAY = WORDS[LANG]
