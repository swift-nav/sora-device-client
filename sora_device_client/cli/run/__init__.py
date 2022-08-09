import click
import sys
import logging

from ...exceptions import ConfigValueError

logger = logging.getLogger("SoraDeviceClient")


@click.command()
@click.pass_obj
def run(obj):
    config, data = obj

    from ... import client

    client = client.SoraDeviceClient(
        device_id=data["device-id"],
        host=config["server"]["host"],
        port=config["server"]["port"],
    )

    client.start()

    from sbp.navigation import SBP_MSG_POS_LLH

    decimate = config["decimate"]

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
    except ConfigValueError as err:
        sys.exit(f"Error: {err}")
