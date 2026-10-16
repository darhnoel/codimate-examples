"""Run the checks.

An example's own tests live in its folder, next to the code they check, so they
go when it goes: `physics/ripple/test_ripple.py`. The checks that cover every
example at once live here.

    python tests/run.py                       # fast: builds every film, no video
    python tests/run.py --render              # also renders every example
    python tests/run.py --render year         # ... or only those named

The fast checks need `typst`; the render needs `ffmpeg` as well.
"""

import importlib
import importlib.util
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import support  # noqa: E402

RENDERS = {"test_render"}
render = "--render" in sys.argv
only = [a for a in sys.argv[1:] if not a.startswith("-")]
if only:
    os.environ["CODIMATE_ONLY"] = ",".join(only)

def run_in_folder(path):
    """An example's test, run the way `python <its folder>/test_x.py` would: its
    folder importable, and whatever it imported from there forgotten afterwards,
    so two examples that both have a `story.py` do not see each other's."""
    folder = str(path.parent)
    sys.path.insert(0, folder)
    try:
        name = ".".join(path.relative_to(ROOT).with_suffix("").parts)
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return support.run(vars(module))
    finally:
        sys.path.remove(folder)
        for name, module in list(sys.modules.items()):
            if (getattr(module, "__file__", None) or "").startswith(folder + "/"):
                del sys.modules[name]


failed = skipped = 0
for path in sorted(HERE.glob("test_*.py")):
    if path.stem in RENDERS and not render:
        skipped += 1
        continue
    if only and path.stem != "test_render":
        skipped += 1       # naming examples is about rendering them
        continue
    failed += support.run(vars(importlib.import_module(path.stem)))

if not only:
    for path in sorted(ROOT.glob("*/*/test_*.py")):
        failed += run_in_folder(path)

if skipped and not render:
    print(f"\nskipped {skipped} file(s) that render video: add --render for those")
if failed:
    print(f"\n{failed} failed")
sys.exit(1 if failed else 0)
