from __future__ import annotations

from typing import ClassVar

from src.main.api.models.create_user_request import CreateUserRequest


class SessionStorage:
    _users: ClassVar[list[CreateUserRequest]] = []

    @classmethod
    def add_users(cls, users: list[CreateUserRequest]) -> None:
        for user in list(users):
            cls._users.append(user)

    @classmethod
    def get_user(cls, index: int = 0) -> CreateUserRequest:
        if index >= len(cls._users):
            raise IndexError(
                f"User index (0-based) out of range: {index}; total={len(cls._users)}"
        )
        return cls._users[index]

    @classmethod
    def clear(cls) -> None:
        cls._users.clear()
