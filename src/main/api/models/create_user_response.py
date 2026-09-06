from typing import Any

from src.main.api.models.base_model import BaseModel


class CreateUserResponse(BaseModel):
    id: int
    username: str
    # Backend may omit password (e.g. GET /admin/users). Keep it optional for parsing lists.
    password: str | None = None
    name: str | None
    role: str
    accounts: list[dict[str, Any]]
