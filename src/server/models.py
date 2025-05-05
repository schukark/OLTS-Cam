from pydantic import BaseModel
from enum import Enum
from typing import List


class SettingsInner(BaseModel):
    key: str
    value: str


class Receiver(str, Enum):
    Camera = "camera"
    Db = "db"
    Fs = "fs"


class Settings(BaseModel):
    receiver: Receiver
    settings: List[SettingsInner]


class ObjectPhoto(BaseModel):
    height: int
    width: int
    image: str
