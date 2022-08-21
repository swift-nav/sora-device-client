import tomlkit
import typer

from deepmerge import always_merger
from rich import print
from typing import Optional
from uuid import UUID

from ..auth0 import Auth0Client, AUTH0_AUDIENCE, AUTH0_CLIENT_ID, AUTH0_DOMAIN
from ..config import read_data, write_data
from ..exceptions import DataFileNotFound


def login():
    """
    Log into Sora Server.

    If there is already device login details in the data file, login will be skipped.
    """
    try:
        data = read_data()
    except DataFileNotFound:
        data = tomlkit.parse("")

    try:
        device = data["device"]
        device_uuid = UUID(device["id"])
        print(f"Already logged in as device {device_uuid}.")
        return
    except tomlkit.exceptions.NonExistentKey:
        client = Auth0Client(AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_AUDIENCE)
        device_uuid, device_access_token = client.register_device()
        always_merger.merge(data, {"device": {"access_token": device_access_token}})

    always_merger.merge(data, {"device": {"id": str(device_uuid)}})

    write_data(data)

    print(f"Logged in as device {device_uuid}")
