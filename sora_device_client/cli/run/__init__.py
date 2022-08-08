import click
import confuse
import sys


@click.command()
@click.option("-i", "--device-id", help="Device Id")
def run(config):
    logger = logging.getLogger("SoraDeviceClient")

    from . import client

    try:
        device_id = config["device-id"].get()
    except confuse.exceptions.NotFoundError:
        sys.exit("Error: Device ID must be specified")

    client = client.SoraDeviceClient(
        device_id=config["device-id"].get(),
        host=config["host"].get(),
        port=config["port"].as_number(),
    )

    client.start()

    from sbp.navigation import SBP_MSG_POS_LLH

    decimate = config["decimate"].as_number()

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
    except confuse.exceptions.ConfigError as err:
        sys.exit(f"Error: {err}")
