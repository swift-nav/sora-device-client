from dataclasses import dataclass
from typing import *


@dataclass
class Position:
    lat: float
    lon: float
    height: float


@dataclass
class Orientation:
    pitch: float
    roll: float
    yaw: float


@dataclass
class Location:
    position: Position
    orientation: Optional[Orientation]
    status: Dict[str, Any]
