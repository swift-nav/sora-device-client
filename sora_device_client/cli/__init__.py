import logging
import click
import confuse
import sys

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
    config = confuse.Configuration("sora-device-client")
    config.set_env()
def main(ctx, verbose, debug):
    ctx.obj = config

    setup_logger(verbose, debug)


main.add_command(run)
main.add_command(login)
