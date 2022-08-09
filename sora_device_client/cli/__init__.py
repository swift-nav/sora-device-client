import logging
import click
import os
import pathlib
import tomlkit
import sys

from appdirs import AppDirs


from .run import run
from .login import login

logger = logging.getLogger("SoraDeviceClient")
dirs = AppDirs("sora-device-client", "SwiftNav")
CONFIG_FILE_PATH = pathlib.Path(dirs.user_config_dir).joinpath("config.toml")
DATA_FILE_PATH = pathlib.Path(dirs.user_data_dir).joinpath("data.toml")


def setup_logger(verbose=False, debug=False):
    logging.basicConfig(
        stream=sys.stdout,
        level=(
            logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING
        ),
        format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    )


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def main(ctx, verbose, debug):
    with open(CONFIG_FILE_PATH, mode="rt", encoding="utf8") as f:
        config = tomlkit.load(f)

    try:
        with open(DATA_FILE_PATH, mode="rt", encoding="utf8") as f:
            data = tomlkit.load(f)
    except FileNotFoundError:
        sys.exit(f"Error: not logged in. Please run sora login")

    ctx.obj = (config, data)

    setup_logger(verbose, debug)


main.add_command(run)
main.add_command(login)
