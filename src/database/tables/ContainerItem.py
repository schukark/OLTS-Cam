from dataclasses import dataclass


@dataclass
class ContainerItem:
    ContID: int
    Name: str
    PositionCoords: str
    PhotoPath: str
