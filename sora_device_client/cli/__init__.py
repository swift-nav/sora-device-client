import logging
import click
import os
import tomlkit
import sys


from .paths import CONFIG_FILE_PATH, DATA_FILE_PATH
from .run import run
from .login import login

logger = logging.getLogger("SoraDeviceClient")


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
        sys.exit(f"Error: not logged in. Please run sora login --device-id <DEVICE_ID>")

    ctx.obj = (config, data)

    setup_logger(verbose, debug)


main.add_command(run)
main.add_command(login)
