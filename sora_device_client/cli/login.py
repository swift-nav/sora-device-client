import tomlkit
import typer

from deepmerge import always_merger
from rich import print
from typing import Optional

from sora_device_client.auth0 import Auth0Client
from sora_device_client.auth0.info import auth0_auth_server_info
from sora_device_client.client import device_service_channel
from sora_device_client.config import read_data, write_data
from sora_device_client.config.device import DeviceConfig
from sora_device_client.config.server import DEFAULT_SERVER_URL, ServerConfig
from sora_device_client.exceptions import DataFileNotFound

import sora.device.v1beta.service_pb2_grpc as device_grpc


def login(
    server_url: Optional[str] = typer.Option(
        None,
        help=f"""
        If --server-url is not provided, either the value on the data file, or
        the default value of {DEFAULT_SERVER_URL} be used.
        """,
    ),
) -> None:
    """
    Log into Sora Server.

    If there is already device login details in the data file,
    login will be skipped.
    """
    try:
        data = read_data()
    except DataFileNotFound:
        data = tomlkit.parse("")

    # server_url order of preference:
    # 1. Command line
    # 2. Data file
    # 3. DEFAULT_SERVER_URL in source
    if not server_url:
        server_url = data.get("server", {}).get("url")
    server_config = ServerConfig(server_url or DEFAULT_SERVER_URL)

    print(f"Using sora server: {server_config.target()}")

    access_token = data.get("device", {}).get("access_token")
    if access_token:
        device_config = DeviceConfig(access_token)
        print(f"Already logged in as device {device_config.device_name}.")
        return

    with device_service_channel(server_config) as channel:
        stub = device_grpc.DeviceServiceStub(channel)
        info = auth0_auth_server_info(stub)
        client = Auth0Client(info=info)
        registration = client.register_device()
        device_uuid = registration.device_id
        always_merger.merge(
            data,
            {
                "device": {
                    "access_token": registration.access_token,
                },
            },
        )

    always_merger.merge(data, {"server": {"url": f"{server_config}"}})

    write_data(data)
    print(f"Logged in as device {device_uuid}. ")
