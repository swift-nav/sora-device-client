import functools
import sys

eprint = functools.partial(print, file=sys.stderr)


def paths() -> None:
    from ..config import DATA_DIR, CONFIG_DIR

    eprint("Configuration folder: (your config.toml needs to go in here)")
    eprint(f"    {CONFIG_DIR}")
    eprint()
    eprint("Data folder: (other runtime data gets stored in here)")
    eprint(f"    {DATA_DIR}")
    eprint()
