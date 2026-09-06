
from src.main.api.models.base_model import BaseModel
from src.main.api.models.create_account_response import CreateAccountResponse


class UserProfileResponse(BaseModel):
    id: int
    username: str
    password: str
    name: str | None
    role: str
    accounts: list[CreateAccountResponse]
