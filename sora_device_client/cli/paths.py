# Copyright (C) 2022 Swift Navigation Inc.
# Contact: Swift Navigation <dev@swiftnav.com>

# This source is subject to the license found in the file 'LICENCE' which must
# be be distributed together with this source. All other rights reserved.

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


def example_config() -> None:
    import sora_device_client
    import importlib.resources

    example_config = (
        importlib.resources.files(sora_device_client)
        .joinpath("config_example.toml")
        .read_text()
    )
    print(example_config)
