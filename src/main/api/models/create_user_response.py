from typing import Optional, List, Dict, Any

from src.main.api.models.base_model import BaseModel


class CreateUserResponse(BaseModel):
    id: int
    username: str
    # Backend may omit password (e.g. GET /admin/users). Keep it optional for parsing lists.
    password: Optional[str] = None
    name: Optional[str]
    role: str
    accounts: List[Dict[str, Any]]