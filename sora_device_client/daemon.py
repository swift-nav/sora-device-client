import logging
import argparse
import confuse
import sys


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-c", "--config", help="Config file path")
    parser.add_argument("-i", "--device-id", help="Device ID")
    parser.add_argument(
        "-v", "--verbose", help="Enable verbose output", action="store_true"
    )
    parser.add_argument(
        "-d", "--debug", help="Enable debugging output", action="store_true"
    )
    parser.add_argument("-s", "--host", help="Sora server hostname")
    parser.add_argument("-p", "--port", help="Sora server port")
    args = parser.parse_args()

    from . import client

    client.show_log_output(verbose=args.verbose, debug=args.debug)
    logger = logging.getLogger("SoraDeviceClient")

    config = confuse.Configuration("SoraDeviceClient", client.__name__)
    if args.config:
        try:
            config.set_file(args.config)
        except confuse.exceptions.ConfigReadError:
            sys.exit(f"Error: Configuration file not found: {args.config}")
    config.set_env()
    config.set_args(args)

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


if __name__ == "__main__":
    main()
