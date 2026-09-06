from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserDao:
    id: int
    username: str
    password: str
    name: str | None
    role: str
    created_at: datetime
    updated_at: datetime
