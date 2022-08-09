import logging
import click
import confuse
import sys

from .run import run
from .login import login

logger = logging.getLogger("SoraDeviceClient")


def show_log_output(verbose=False, debug=False):
    logging.basicConfig(
        stream=sys.stdout,
        level=(
            logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING
        ),
        format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    )


@click.group()
@click.option(
    "-c", "--config-file", help="Config file path", type=click.Path(), default=None
)
@click.option("-v", "--verbose", count=True)
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def main(ctx, config_file, verbose, debug):
    config = confuse.Configuration("sora-device-client")
    if config_file:
        try:
            config.set_file(config_file)
        except confuse.exceptions.ConfigReadError:
            sys.exit(f"Error: Configuration file not found: {config_file}")

    config.set_env()

    show_log_output(verbose, debug)
    ctx.obj = config


main.add_command(run)
main.add_command(login)
