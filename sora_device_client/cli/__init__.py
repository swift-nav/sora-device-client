import logging
import os
import tomlkit
import typer
import sys


from .paths import CONFIG_FILE_PATH, DATA_FILE_PATH

logger = logging.getLogger("SoraDeviceClient")
app = typer.Typer()


def setup_logger(verbose=False, debug=False):
    logging.basicConfig(
        stream=sys.stdout,
        level=(
            logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING
        ),
        format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    )


@app.callback()
def callback(ctx: typer.Context, verbose: bool = False, debug: bool = False):
    with open(CONFIG_FILE_PATH, mode="rt", encoding="utf8") as f:
        config = tomlkit.load(f)

    try:
        with open(DATA_FILE_PATH, mode="rt", encoding="utf8") as f:
            data = tomlkit.load(f)
    except FileNotFoundError:
        raise typer.Exit(
            f"Error: not logged in. Please run sora login --device-id <DEVICE_ID>"
        )

    ctx.obj = (config, data)

    setup_logger(verbose, debug)
