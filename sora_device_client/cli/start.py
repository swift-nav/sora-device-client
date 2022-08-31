import typer

from rich import print

from sora_device_client.config import read_config, read_data
from sora_device_client.config.device import DeviceConfig
from sora_device_client.config.server import ServerConfig
from sora_device_client.exceptions import ConfigValueError, DataFileNotFound


def start():
    """
    Start the sora-device-client and stream location data to the Sora Server.
    """
    config = read_config()
    try:
        data = read_data()
    except DataFileNotFound:
        print("Could not find existing device credentials. Please login.")
        raise typer.Exit(code=1)

    from ..client import SoraDeviceClient

    device_config = DeviceConfig(data["device"]["access_token"])
    server_config = ServerConfig(data["server"]["url"])

    client = SoraDeviceClient(
        device_config=device_config,
        server_config=server_config,
    )

    client.start()

    decimate = int(config["location"]["decimate"])

    try:
        from .. import drivers
        from .. import formats

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
                    print("Terminating state stream.")
                    raise typer.Exit(code=0)
    except ConfigValueError as e:
        print(e)
        raise typer.Exit(code=1)
