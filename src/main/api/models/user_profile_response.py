from typing import List, Optional

from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.base_model import BaseModel


class UserProfileResponse(BaseModel):
    id: int
    username: str
    password: str
    name: Optional[str]
    role: str
    accounts: List[CreateAccountResponse]
