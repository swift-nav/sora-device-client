import logging

from ..exceptions import ConfigValueError

log = logging.getLogger(__name__)


class DriverConfigValueError(Exception):
    pass


def tcp_driver_from_config(config):
    tcp_host = str(config["host"])
    tcp_port = int(config["port"])
    log.info(f"Using TCP driver: {tcp_host}:{tcp_port}")
    from sbp.client.drivers.network_drivers import TCPDriver

    return TCPDriver(tcp_host, tcp_port)


def serial_driver_from_config(config):
    port = config["port"]
    baud = config["baud"]
    log.info(f"Using Serial driver: {port} @ {baud}")
    from sbp.client.drivers.pyserial_driver import PySerialDriver

    return PySerialDriver(port, baud)


DRIVERS = {"tcp": tcp_driver_from_config, "serial": serial_driver_from_config}


def driver_from_config(config):
    drivers_cfg = config["driver"]
    if len(drivers_cfg) != 1:
        raise ConfigValueError("Exactly one driver should be specified")

    driver_type = list(drivers_cfg.keys())[0]
    if driver_type not in DRIVERS:
        raise ConfigValueError(f'Unknown driver type "{driver_type}"')

    driver_config = config["driver"][driver_type]
    return DRIVERS[driver_type](driver_config)
