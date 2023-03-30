# Copyright (C) 2022 Swift Navigation Inc.
# Contact: Swift Navigation <dev@swiftnav.com>

# This source is subject to the license found in the file 'LICENCE' which must
# be be distributed together with this source. All other rights reserved.

import os
import pathlib
import tomlkit


from appdirs import AppDirs

from ..exceptions import DataFileNotFound

dirs = AppDirs("sora-device-client", "SwiftNav")
CONFIG_DIR = pathlib.Path(dirs.user_config_dir)
DATA_DIR = pathlib.Path(dirs.user_data_dir)
CONFIG_FILE_PATH = CONFIG_DIR.joinpath("config.toml")
DATA_FILE_PATH = DATA_DIR.joinpath("data.toml")


def read_config() -> tomlkit.TOMLDocument:
    with open(CONFIG_FILE_PATH, mode="r", encoding="utf8") as f:
        return tomlkit.load(f)


def read_data() -> tomlkit.TOMLDocument:
    try:
        with open(DATA_FILE_PATH, mode="r", encoding="utf8") as f:
            return tomlkit.load(f)
    except FileNotFoundError:
        raise DataFileNotFound(
            f"Data file not found at path: {DATA_FILE_PATH}. Please run sora-device-client login to create it."
        )


def delete_data_file() -> None:
    DATA_FILE_PATH.unlink(missing_ok=True)


def write_data(data: tomlkit.TOMLDocument) -> None:
    DATA_FILE_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with os.fdopen(
        os.open(DATA_FILE_PATH, os.O_CREAT | os.O_RDWR | os.O_TRUNC, 0o600),
        "w+",
        encoding="utf8",
    ) as f:
        f.write(tomlkit.dumps(data))
