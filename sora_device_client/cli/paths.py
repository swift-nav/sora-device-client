import pathlib

from appdirs import AppDirs

dirs = AppDirs("sora-device-client", "SwiftNav")
CONFIG_FILE_PATH = pathlib.Path(dirs.user_config_dir).joinpath("config.toml")
DATA_FILE_PATH = pathlib.Path(dirs.user_data_dir).joinpath("data.toml")
