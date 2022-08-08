import logging
import click
import confuse
import sys

from .cli.run import run
from .cli.login import login

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
# @click.option("-c", "--config-file", help="Config file path")
@click.option("-v", "--verbose", count=True)
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def main(ctx, config_file):
    click.echo(ctx)
    config = confuse.Configuration("SoraDeviceClient", __name__)
    if config_file:
        try:
            config.set_file(config_file)
        except confuse.exceptions.ConfigReadError:
            sys.exit(f"Error: Configuration file not found: {config_file}")
    config.set_env()
    config.set_args(ctx)


main.add_command(run)
main.add_command(login)

if __name__ == "__main__":
    main(None, None)
