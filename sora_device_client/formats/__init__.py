import logging

from ..exceptions import ConfigValueError

logger = logging.getLogger("SoraDeviceClient")


class FormatConfigValueError(Exception):
    pass


def sbp_format_from_config(config, driver):
    from .sbp import SBPFormat

    return SBPFormat(driver)


FORMATS = {
    "sbp": sbp_format_from_config,
}


def format_from_config(config, driver):
    formats_cfg = config["format"].get()
    if len(formats_cfg) != 1:
        raise ConfigValueError("Exactly one format should be specified")

    format_type = list(formats_cfg.keys())[0]
    if format_type not in FORMATS:
        raise ConfigValueError(f'Unknown format type "{format_type}"')

    format_config = config["format"][format_type]
    return FORMATS[format_type](format_config, driver)
