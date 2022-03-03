
from dataclasses import dataclass

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
    orientation: Orientation
    status: dict
