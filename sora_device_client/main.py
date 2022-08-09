import click
import logging
import sys
import tomlkit
import typer
import uuid

from .exceptions import ConfigValueError
from .paths import CONFIG_FILE_PATH, DATA_FILE_PATH

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
    """
    Sora Device Client
    """
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


@app.command()
def login(ctx: typer.Context, device_id: str):
    """
    Log into Sora Server with the provided device id
    """
    _, data = ctx.obj

    if not device_id:
        try:
            device_id = data["device-id"]
        except KeyError:
            sys.exit("Please specify a device-id")

    data["device-id"] = str(uuid.UUID(device_id))

    DATA_FILE_PATH.mkdir(mode=0o700, parents=True, exist_ok=True)
    with open(DATA_FILE_PATH, "w+", encoding="utf8") as f:
        f.write(tomlkit.dumps(data))


@app.command()
def start(ctx: typer.Context):
    """
    Start the sora-device-client and stream location data to the Sora Server
    """
    config, data = ctx.obj

    from ... import client

    client = client.SoraDeviceClient(
        device_id=data["device-id"],
        host=config["server"]["host"],
        port=config["server"]["port"],
    )

    client.start()

    from sbp.navigation import SBP_MSG_POS_LLH

    decimate = config["decimate"]

    try:
        from ... import drivers
        from ... import formats

        with drivers.driver_from_config(config) as driver:
            with formats.format_from_config(config, driver) as source:
                try:
                    for i, loc in enumerate(source):
                        if i % decimate == 0:
                            client.send_state(
                                loc.status,
                                lat=loc.position.lat,
                                lon=loc.position.lon,
                            )
                except KeyboardInterrupt:
                    pass
    except ConfigValueError as err:
        sys.exit(f"Error: {err}")
