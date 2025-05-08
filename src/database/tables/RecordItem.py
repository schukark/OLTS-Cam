from dataclasses import dataclass
from typing import Optional

@dataclass
class RecordItem:
    VideoID: Optional[int] = None
    StartTime: Optional[str] = None
    EndTime: Optional[str] = None
    VideoPath: Optional[str] = None