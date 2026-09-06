from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserDao:
    """
    Representation of a row in 'customers' table.
    Field names are expected to match DB columns (snake_case).
    """

    id: int
    username: str
    password: str
    name: str | None
    role: str

