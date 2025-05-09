from dataclasses import dataclass


@dataclass
class ObjectItem:
    ObjrecID: int
    Name: str
    Time: str
    PositionCoord: str
    ContID: int
    PhotoPath: str
