from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Transport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str  # car, ferry, bus, train
    origin: str
    destination: str
    price: float
    capacity: int
    departure_time: datetime
    arrival_time: datetime


class TransportCreate(SQLModel):
    type: str
    origin: str
    destination: str
    price: float
    capacity: int
    departure_time: datetime
    arrival_time: datetime
