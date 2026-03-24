from typing import Optional
from sqlmodel import Field, SQLModel


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    city: str
    description: str
    duration_hours: float
    price: float
    category: str  # adventure, culture, food, nature, etc.
    availability: str  # daily, weekends, specific dates


class ActivityCreate(SQLModel):
    name: str
    city: str
    description: str
    duration_hours: float
    price: float
    category: str
    availability: str
