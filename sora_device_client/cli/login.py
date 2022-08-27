import tomlkit

from deepmerge import always_merger
from rich import print
from uuid import UUID

from ..auth0 import Auth0Client
from ..auth0.info import auth0_auth_server_info
from ..client import device_service_channel
from ..config import read_config, read_data, write_data
from ..exceptions import DataFileNotFound

import sora.device.v1beta.service_pb2_grpc as device_grpc


def login():
    """
    Log into Sora Server.

    If there is already device login details in the data file, login will be skipped.
    """
    try:
        data = read_data()
    except DataFileNotFound:
        data = tomlkit.parse("")

    device_id = data.get("device", {}).get("id")
    if device_id:
        device_uuid = UUID(str(device_id))
        print(f"Already logged in as device {device_uuid}.")
        return

    config = read_config()
    server = config["server"]
    with device_service_channel(
        server["host"], server["port"], server.get("disable_tls", False)
    ) as channel:
        stub = device_grpc.DeviceServiceStub(channel)
        info = auth0_auth_server_info(stub)
        client = Auth0Client(info=info)
        device_uuid, device_access_token = client.register_device()
        always_merger.merge(data, {"device": {"access_token": device_access_token}})
        always_merger.merge(data, {"device": {"id": str(device_uuid)}})

    write_data(data)
    print(f"Logged in as device {device_uuid}")
