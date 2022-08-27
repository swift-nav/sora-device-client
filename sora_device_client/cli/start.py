import typer

from rich import print
from uuid import UUID

from ..config import read_config, read_data
from ..exceptions import ConfigValueError, DataFileNotFound


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

    client = SoraDeviceClient(
        device_uuid=UUID(data["device"]["id"]),
        access_token=data["device"]["access_token"],
        host=config["server"]["host"],
        port=config["server"]["port"],
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
                    pass
    except ConfigValueError as e:
        print(e)
        raise typer.Exit(code=1)
