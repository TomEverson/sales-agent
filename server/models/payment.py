from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    booking_reference: str = Field(unique=True, index=True)
    amount: float
    status: str = "pending"
    payment_method: str = "qr"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None


class PaymentCreate(SQLModel):
    amount: float
    payment_method: str = "qr"


class PaymentResponse(SQLModel):
    id: int
    booking_reference: str
    amount: float
    status: str
    payment_method: str
    created_at: datetime
    paid_at: Optional[datetime]
