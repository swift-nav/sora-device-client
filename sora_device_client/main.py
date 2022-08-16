import logging
import os
import pathlib
import sys
import tomlkit
import typer
import uuid

from rich.logging import RichHandler
from typing import Optional

from .exceptions import ConfigValueError, DataFileNotFound
from .paths import CONFIG_FILE_PATH, DATA_FILE_PATH
from .auth0 import Auth0Client

app = typer.Typer()
log = logging.getLogger(__name__)

AUTH0_DOMAIN = "nepa-test.au.auth0.com"
AUTH0_CLIENT_ID = "rg4u984ZG8OKaMUL44geh397QpX1ozcr"
AUTH0_AUDIENCE = "http://localhost:10000:/sora.app.v1beta.AppService"


def read_config() -> tomlkit.TOMLDocument:
    with open(CONFIG_FILE_PATH, mode="r", encoding="utf8") as f:
        return tomlkit.load(f)


def read_data() -> tomlkit.TOMLDocument:
    try:
        with open(DATA_FILE_PATH, mode="r", encoding="utf8") as f:
            return tomlkit.load(f)
    except FileNotFoundError:
        raise DataFileNotFound(
            f"Data file not found at path: {DATA_FILE_PATH}. Please run sora-device-client login --device-id <DEVICE_ID> to create it."
        )


def setup_logger(verbose=False, debug=False):
    logging.basicConfig(
        level=(
            logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING
        ),
        format="%(message)s",
        handlers=[RichHandler()],
    )


def write_data(path: pathlib.Path, data: tomlkit.TOMLDocument):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with os.fdopen(
        os.open(path, os.O_CREAT | os.O_RDWR | os.O_TRUNC, 0o600), "w+", encoding="utf8"
    ) as f:
        f.write(tomlkit.dumps(data))


@app.callback()
def callback(verbose: bool = False, debug: bool = False):
    """
    Sora Device Client
    """
    setup_logger(verbose, debug)


@app.command()
def login(
    device_id: Optional[str] = typer.Option(None, help="Device Id to log into Sora as.")
):
    """
    Log into Sora Server with the provided device id.

    The behaviour depends on two things:
        1. Is there a data file?
        2. Has --device-id been specified?

    1 & 2:
        ignore device-id, print message that device_id is going to be used

    1 & ~2:
        print message that device_id is going to be used

    ~1 & 2:
        save device-id to data file

    ~1 & ~2:
        error
    """
    try:
        data = read_data()
    except DataFileNotFound:
        data = tomlkit.parse("")

    try:
        device_id = data["device-id"]
        typer.echo(f"Already logged in as device {device_id}.")
        return
    except KeyError:
        if not device_id:
            raise typer.Exit("--device-id must be specified if not already logged in.")

    client = Auth0Client(AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_AUDIENCE)
    res = client.register_device()
    typer.echo(res)

    data["device-id"] = str(uuid.UUID(device_id))

    write_data(DATA_FILE_PATH, data)

    typer.echo(f"Logged in as device {device_id}")


@app.command()
def logout():
    """
    Log the device out of Sora Server.
    """
    try:
        data = read_data()
    except DataFileNotFound:
        raise typer.Exit("Device not logged in.")

    try:
        del data["device-id"]
    except tomlkit.container.NonExistentKey:
        pass

    write_data(DATA_FILE_PATH, data)


@app.command()
def start():
    """
    Start the sora-device-client and stream location data to the Sora Server.
    """
    config = read_config()
    try:
        data = read_data()
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

    decimate = config["location"]["decimate"]

    try:
        from . import drivers
        from . import formats

        with drivers.driver_from_config(config["location"]) as driver:
            with formats.format_from_config(config["location"], driver) as source:
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
        raise typer.Exit(f"Error: {err}")
