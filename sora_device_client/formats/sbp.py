from typing import *
from sbp.client import Handler, Framer
from sbp.navigation import SBP_MSG_POS_LLH, SBP_MSG_GPS_TIME
from sbp.client.drivers.base_driver import BaseDriver
from .. import location
from . import Format

FIX_MODES = [
    "Invalid",
    "SPP",
    "DGNSS",
    "Float RTK",
    "Fixed RTK",
    "Dead Reckoning",
    "SBAS",
]

SBPMsg = Any


def pos_llh_to_position(msg: SBPMsg) -> Tuple[location.Position, Dict[str, Any]]:
    pos = location.Position(
        lat=msg.lat,
        lon=msg.lon,
        height=msg.height,
    )
    meta = {
        "n_sats": msg.n_sats,
        "h_accuracy": msg.h_accuracy,
        "v_accuracy": msg.v_accuracy,
        "flags": msg.flags,
        "fix_mode": FIX_MODES[msg.flags & 7],
    }
    return (pos, meta)


class SBPFormat(Format):
    def __init__(self, driver: BaseDriver):
        self._sbp_handler = Handler(Framer(driver.read, None, verbose=True))
        self._msg_set = {SBP_MSG_POS_LLH: None, SBP_MSG_GPS_TIME: None}
        self._tow = None
        self._sbp_iter = filter(
            lambda x: x[0].msg_type in self._msg_set.keys(), self._sbp_handler.filter()
        )

    def __enter__(self) -> "SBPFormat":
        self._sbp_handler.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self._sbp_handler.__exit__(*args)

    def __iter__(self) -> "SBPFormat":
        return self

    def _reset_msg_set(self) -> None:
        for key in self._msg_set.keys():
            self._msg_set[key] = None

    def _msg_set_complete(self) -> bool:
        return all(x is not None for x in self._msg_set.values())

    def __next__(self) -> location.Location:
        # Construct a complete msg set
        while not self._msg_set_complete():
            msg, meta = next(self._sbp_iter)
            if msg.tow != self._tow:
                self._reset_msg_set()
                self._tow = msg.tow
            self._msg_set[msg.msg_type] = msg

        # Got a complete set, convert to Location
        pos, pos_meta = pos_llh_to_position(self._msg_set[SBP_MSG_POS_LLH])
        loc = location.Location(position=pos, orientation=None, status=pos_meta)

        # Reset the msg set for next time
        self._reset_msg_set()
        return loc
