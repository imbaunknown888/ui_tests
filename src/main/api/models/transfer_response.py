
from src.main.api.models.base_model import BaseModel


class TransferResponse(BaseModel):
    status: str
    message: str

    amount: float
    senderAccountId: int
    receiverAccountId: int

    fraudRiskScore: float | None = None
    fraudReason: str | None = None
    requiresManualReview: bool | None = None
    requiresVerification: bool | None = None

