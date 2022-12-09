import logging

from typing import *
from abc import ABCMeta
from ..exceptions import ConfigValueError
from ..location import Location

log = logging.getLogger(__name__)


class FormatConfigValueError(Exception):
    pass


if TYPE_CHECKING:
    from . import sbp as sbp_format
    from sbp.client.drivers.base_driver import BaseDriver

F = TypeVar("F")  # https://en.wikipedia.org/wiki/Curiously_recurring_template_pattern


class Format(ContextManager[F], Iterable[Location], metaclass=ABCMeta):
    pass


def sbp_format_from_config(config: Any, driver: "BaseDriver") -> "sbp_format.SBPFormat":
    from .sbp import SBPFormat

    return SBPFormat(driver)


FORMATS = {
    "sbp": sbp_format_from_config,
}


def format_from_config(config: Any, driver: "BaseDriver") -> Format[Any]:
    formats_cfg = config["format"]
    if len(formats_cfg) != 1:
        raise ConfigValueError("Exactly one format should be specified")

    format_type = list(formats_cfg.keys())[0]
    if format_type not in FORMATS:
        raise ConfigValueError(f'Unknown format type "{format_type}"')

    format_config = config["format"][format_type]
    return FORMATS[format_type](format_config, driver)
