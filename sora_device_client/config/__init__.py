import os
import pathlib
import tomlkit


from appdirs import AppDirs

from ..exceptions import DataFileNotFound

dirs = AppDirs("sora-device-client", "SwiftNav")
CONFIG_FILE_PATH = pathlib.Path(dirs.user_config_dir).joinpath("config.toml")
DATA_FILE_PATH = pathlib.Path(dirs.user_data_dir).joinpath("data.toml")


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


def delete_data_file():
    DATA_FILE_PATH.unlink(missing_ok=True)


def write_data(data: tomlkit.TOMLDocument):
    DATA_FILE_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with os.fdopen(
        os.open(DATA_FILE_PATH, os.O_CREAT | os.O_RDWR | os.O_TRUNC, 0o600),
        "w+",
        encoding="utf8",
    ) as f:
        f.write(tomlkit.dumps(data))
