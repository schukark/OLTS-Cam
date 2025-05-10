from enum import Enum
from typing import List

from pydantic import BaseModel


class SettingsInner(BaseModel):
    """
    Represents a single key-value pair for settings.

    Attributes:
        key (str): The setting's key.
        value (str): The value associated with the key.
    """
    key: str
    value: str


class Receiver(str, Enum):
    """
    Enum representing the possible receivers of the settings.
    
    - Camera: The settings apply to a camera.
    - Model: The settings apply to a model.
    """
    Camera = "camera"
    Model = "model"


class Settings(BaseModel):
    """
    Represents a configuration set for a specific receiver.

    Attributes:
        receiver (Receiver): The type of receiver (either Camera or Model).
        settings (List[SettingsInner]): A list of settings (key-value pairs) for the receiver.
    """
    receiver: Receiver
    settings: List[SettingsInner]


class ObjectPhoto(BaseModel):
    """
    Represents an image with associated metadata (height, width, and base64-encoded image).

    Attributes:
        height (int): The height of the image in pixels.
        width (int): The width of the image in pixels.
        image (str): The base64-encoded image in JPEG format.
    """
    height: int
    width: int
    image: str
