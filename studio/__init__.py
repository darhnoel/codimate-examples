"""What every film here shares: the Inter fonts and the sound engine.

    from studio.sound import instruments, room, master
    FONTS = studio.FONTS

Not an example on its own; the films in ``showcase/`` use it.
"""

from pathlib import Path

FONTS = Path(__file__).resolve().parent / "fonts"
