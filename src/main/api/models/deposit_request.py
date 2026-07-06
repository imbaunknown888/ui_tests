from src.main.api.models.base_model import BaseModel


class DepositRequest(BaseModel):
    id: int
    accountNumber: str
    balance: float

