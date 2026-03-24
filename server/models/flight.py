from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Flight(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    origin: str
    destination: str
    airline: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    seats_available: int
    class_type: str  # economy, business, first


class FlightCreate(SQLModel):
    origin: str
    destination: str
    airline: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    seats_available: int
    class_type: str
