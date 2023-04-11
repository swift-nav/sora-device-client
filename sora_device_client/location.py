# Copyright (C) 2022 Swift Navigation Inc.
# Contact: Swift Navigation <dev@swiftnav.com>

# This source is subject to the license found in the file 'LICENCE' which must
# be be distributed together with this source. All other rights reserved.

from dataclasses import dataclass
from typing import *


@dataclass
class Position:
    lat: float
    lon: float
    height: Optional[float]


@dataclass
class Orientation:
    yaw: float
    pitch: float
    roll: float


@dataclass
class Location:
    position: Position
    orientation: Optional[Orientation]
    status: Dict[str, Any]
