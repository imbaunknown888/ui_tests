from typing import Any

from src.main.api.models.base_model import BaseModel


class DepositResponse(BaseModel):
    """
    Backend returns updated account + optional transaction metadata.
    Keep optional fields to be tolerant across backend builds.
    """

    id: int
    accountNumber: str
    balance: float

    depositAmount: float | None = None
    transactionId: int | None = None
    transaction: Any | None = None

