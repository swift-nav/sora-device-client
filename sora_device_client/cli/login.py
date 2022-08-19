import tomlkit
import typer

from deepmerge import always_merger
from rich import print
from typing import Optional
from uuid import UUID

from ..auth0 import Auth0Client, AUTH0_AUDIENCE, AUTH0_CLIENT_ID, AUTH0_DOMAIN
from ..config import read_data, write_data
from ..exceptions import DataFileNotFound

app = typer.Typer()


@app.command()
def login(
    device_id: Optional[str] = typer.Option(None, help="Device Id to log into Sora as.")
):
    """
    Log into Sora Server with the provided device id.

    The behaviour depends on two things:
        1. Is there a data file with a device.id key?
        2. Has --device-id been specified?

    1 & 2:
        ignore device-id from data file, print message that device_id is going to be used

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
        device_uuid = UUID(data["device"]["id"])
        print(f"Already logged in as device {device_uuid}.")
        return
    except tomlkit.exceptions.NonExistentKey:
        if not device_id:
            client = Auth0Client(AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_AUDIENCE)
            device_uuid, device_access_token = client.register_device()
            always_merger.merge(data, {"device": {"access_token": device_access_token}})
        else:
            device_uuid = UUID(device_id)

    always_merger.merge(data, {"device": {"id": str(device_uuid)}})

    write_data(data)

    print(f"Logged in as device {device_uuid}")
