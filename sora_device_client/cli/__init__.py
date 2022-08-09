import logging
import click
import os
import tomlkit
import sys

from appdirs import AppDirs


from .run import run
from .login import login

logger = logging.getLogger("SoraDeviceClient")
dirs = AppDirs("sora-device-client", "SwiftNav")
CONFIG_FILE = os.path.join(dirs.user_config_dir, "config.toml")


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
    with open(CONFIG_FILE, mode="rt", encoding="utf8") as f:
        config = tomlkit.load(f)

    ctx.obj = config

    setup_logger(verbose, debug)


main.add_command(run)
main.add_command(login)
