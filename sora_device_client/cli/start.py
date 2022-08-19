import typer

from ..exceptions import ConfigValueError, DataFileNotFound

app = typer.Typer()


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

    from ..client import SoraDeviceClient

    client = SoraDeviceClient(
        device_id=data["device"]["id"],
        device_access_token=data["device"]["access_token"],
        host=config["server"]["host"],
        port=config["server"]["port"],
    )

    client.start()

    from sbp.navigation import SBP_MSG_POS_LLH

    decimate = config["location"]["decimate"]

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
    except ConfigValueError as err:
        raise typer.Exit(f"Error: {err}")
