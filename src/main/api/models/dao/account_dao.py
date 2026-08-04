from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class AccountDao:
    id: int
    account_number: str
    balance: Decimal
    customer_id: int
    created_at: datetime
    updated_at: datetime
