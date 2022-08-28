import tomlkit
import typer

from deepmerge import always_merger
from rich import print
from typing import Optional
from uuid import UUID

from ..auth0 import Auth0Client
from ..auth0.info import auth0_auth_server_info
from ..client import device_service_channel
from ..config import read_data, write_data
from ..config.server import DEFAULT_SERVER_URL, ServerConfig
from ..exceptions import DataFileNotFound

import sora.device.v1beta.service_pb2_grpc as device_grpc


def login(
    server_url: Optional[str] = typer.Option(
        None,
        help=f"""
        If --server-url is not provided, either the value on the data file, or
        the default value of {DEFAULT_SERVER_URL} be used.
        """,
    ),
):

    f"""
    Log into Sora Server.

    If there is already device login details in the data file,
    login will be skipped.
    """
    try:
        data = read_data()
    except DataFileNotFound:
        data = tomlkit.parse("")

    print(f"Server url = {server_url}")

    # server_url order of preference:
    # 1. Command line
    # 2. Data file
    # 3. DEFAULT_SERVER_URL in source
    if not server_url:
        server_url = data.get("server", {}).get("url")
    server_config = ServerConfig(server_url or DEFAULT_SERVER_URL)

    print(f"Using sora server: {server_config.target()}")

    device_id = data.get("device", {}).get("id")
    if device_id:
        device_uuid = UUID(str(device_id))
        print(f"Already logged in as device {device_uuid}.")
        return

    with device_service_channel(server_config) as channel:
        stub = device_grpc.DeviceServiceStub(channel)
        info = auth0_auth_server_info(stub)
        client = Auth0Client(info=info)
        device_uuid, device_access_token = client.register_device()
        always_merger.merge(data, {"device": {"access_token": device_access_token}})
        always_merger.merge(data, {"device": {"id": str(device_uuid)}})

    always_merger.merge(data, {"server": {"url": f"{server_config}"}})

    write_data(data)
    print(f"Logged in as device {device_uuid}")
