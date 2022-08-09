import click
import confuse
import sys
import logging

logger = logging.getLogger("SoraDeviceClient")


@click.command()
@click.pass_obj
def run(config):
    from ... import client

    client = client.SoraDeviceClient(
        device_id=config["device-id"].get(),
        host=config["host"].get(),
        port=config["port"].as_number(),
    )

    client.start()

    from sbp.navigation import SBP_MSG_POS_LLH

    decimate = config["decimate"].as_number()

    try:
        from ... import drivers
        from ... import formats

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
