from dataclasses import dataclass
from typing import *


@dataclass
class Position:
    lat: float
    lon: float
    height: float


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
