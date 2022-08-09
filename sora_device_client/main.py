import logging
import os
import sys
import tomlkit
import typer
import uuid

from rich import print
from typing import Optional, Tuple

from .exceptions import ConfigValueError, DataFileNotFound
from .paths import CONFIG_FILE_PATH, DATA_FILE_PATH

app = typer.Typer()


def read_config() -> tomlkit.TOMLDocument:
    with open(CONFIG_FILE_PATH, mode="rt", encoding="utf8") as f:
        return tomlkit.load(f)


def read_data() -> tomlkit.TOMLDocument:
    try:
        with open(DATA_FILE_PATH, mode="rt", encoding="utf8") as f:
            return tomlkit.load(f)
    except FileNotFoundError:
        raise DataFileNotFound(
            f"Data file not found at path: {DATA_FILE_PATH}. Please run sora-device-client login --device-id <DEVICE_ID> to create it."
        )


def setup_logger(verbose=False, debug=False):
    logging.basicConfig(
        stream=sys.stdout,
        level=(
            logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING
        ),
        format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    )


@app.callback()
def callback(verbose: bool = False, debug: bool = False):
    """
    Sora Device Client
    """
    setup_logger(verbose, debug)


@app.command()
def login(device_id: str = typer.Option(..., help="Device Id to log into Sora as.")):
    """
    Log into Sora Server with the provided device id.
    """
    try:
        data = read_data()
        print(f"Found existing data: {data}")
        return
    except DataFileNotFound as e:
        data = tomlkit.parse("")

    data["device-id"] = str(uuid.UUID(device_id))

    DATA_FILE_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with open(
        os.open(DATA_FILE_PATH, os.O_CREAT | os.O_WRONLY, 0o600), "w+", encoding="utf8"
    ) as f:
        f.write(tomlkit.dumps(data))


@app.command()
def start():
    """
    Start the sora-device-client and stream location data to the Sora Server.
    """
    config = read_config()
    try:
        data = read_config()
    except DataFileNotFound as e:
        raise typer.Exit(f"{e}")

    from .client import SoraDeviceClient

    client = SoraDeviceClient(
        device_id=data["device-id"],
        host=config["server"]["host"],
        port=config["server"]["port"],
    )

    client.start()

    from sbp.navigation import SBP_MSG_POS_LLH

    decimate = config["decimate"]

    try:
        from . import drivers
        from . import formats

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