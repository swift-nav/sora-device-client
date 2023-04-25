# Copyright (C) 2022 Swift Navigation Inc.
# Contact: Swift Navigation <dev@swiftnav.com>

# This source is subject to the license found in the file 'LICENCE' which must
# be be distributed together with this source. All other rights reserved.

from typing import *
from sbp.client import Handler, Framer
from sbp.navigation import SBP_MSG_POS_LLH, SBP_MSG_GPS_TIME
from sbp.orientation import SBP_MSG_ORIENT_EULER
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


def msg_euler_to_orientation(
    msg: SBPMsg,
) -> Tuple[Optional[location.Orientation], Dict[str, Any]]:
    ori = None
    meta: Dict[str, Any] = {}

    if not msg:
        return (ori, meta)

    if not _is_orientation_valid(msg.flags):
        return (ori, meta)

    ori = location.Orientation(
        yaw=msg.yaw / (1000 * 1000),
        pitch=msg.pitch / (1000 * 1000),
        roll=msg.roll / (1000 * 1000),
    )
    meta = {
        "roll_accuracy": msg.roll_accuracy,
        "pitch_accuracy": msg.pitch_accuracy,
        "yaw_accuracy": msg.yaw_accuracy,
        "flags": msg.flags,
    }
    return (ori, meta)


def _is_orientation_valid(flags: int) -> bool:
    """The orientation is invalid when the last 3 bits of the flags are 0"""
    navigation_mode = flags & 0x7
    return navigation_mode != 0


class SBPFormat(Format):
    def __init__(self, driver: BaseDriver, config: Dict[str, Any]):
        self._sbp_handler = Handler(Framer(driver.read, None, verbose=True))
        self._msg_set = {SBP_MSG_POS_LLH: None, SBP_MSG_GPS_TIME: None}
        self._tow = None
        self._sbp_iter = filter(
            lambda x: x[0].msg_type in self._msg_set.keys(), self._sbp_handler.filter()
        )
        self._apply_config(config)

    def __enter__(self) -> "SBPFormat":
        self._sbp_handler.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self._sbp_handler.__exit__(*args)

    def __iter__(self) -> "SBPFormat":
        return self

    def _apply_config(self, config: Dict[str, Any]) -> None:
        orientation = bool(config.get("orientation", False))
        if orientation:
            self._msg_set[SBP_MSG_ORIENT_EULER] = None

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
        ori, ori_meta = msg_euler_to_orientation(
            self._msg_set.get(SBP_MSG_ORIENT_EULER, None)
        )

        loc = location.Location(
            position=pos, orientation=ori, status={**pos_meta, **ori_meta}
        )

        # Reset the msg set for next time
        self._reset_msg_set()
        return loc
