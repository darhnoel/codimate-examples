"""Run the checks.

    python tests/run.py                       # fast: builds every film, no video
    python tests/run.py --render              # also renders every example
    python tests/run.py --render year         # ... or only those named

The fast checks need `typst`; the render needs `ffmpeg` as well.
"""

import importlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import support  # noqa: E402

RENDERS = {"test_render"}
render = "--render" in sys.argv
only = [a for a in sys.argv[1:] if not a.startswith("-")]
if only:
    os.environ["CODIMATE_ONLY"] = ",".join(only)

failed = skipped = 0
for path in sorted(HERE.glob("test_*.py")):
    if path.stem in RENDERS and not render:
        skipped += 1
        continue
    if only and path.stem != "test_render":
        skipped += 1       # naming examples is about rendering them
        continue
    failed += support.run(vars(importlib.import_module(path.stem)))

if skipped and not render:
    print(f"\nskipped {skipped} file(s) that render video: add --render for those")
if failed:
    print(f"\n{failed} failed")
sys.exit(1 if failed else 0)
