from typing import Optional
from sqlmodel import Field, SQLModel


class Hotel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    location: str
    city: str
    stars: int
    price_per_night: float
    rooms_available: int
    amenities: str  # comma-separated string


class HotelCreate(SQLModel):
    name: str
    location: str
    city: str
    stars: int
    price_per_night: float
    rooms_available: int
    amenities: str
