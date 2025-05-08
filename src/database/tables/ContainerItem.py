from dataclasses import dataclass
from typing import Optional

@dataclass
class ContainerItem:
    ContID: int
    Name: str
    Position: Optional[str] = None
    PhotoPath: Optional[str] = None