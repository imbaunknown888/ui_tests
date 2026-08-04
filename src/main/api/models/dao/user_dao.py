from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserDao:
    id: int
    username: str
    password: str
    name: Optional[str]
    role: str
    created_at: datetime
    updated_at: datetime
