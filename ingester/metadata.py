from dataclasses import dataclass
import datetime

@dataclass
class Metadata:
    link: str
    name: str
    author: str
    date: datetime