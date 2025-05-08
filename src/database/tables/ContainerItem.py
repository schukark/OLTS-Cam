from dataclasses import dataclass
from typing import Optional

@dataclass
class ContainerItem:
    Name: str
    Position: Optional[str] = None
    PhotoPath: Optional[str] = None