from datetime import datetime
from sqlmodel import SQLModel, Field


class InsurancePlan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    price_per_person: float
    coverage_types: str
    max_trip_value: float
    medical_coverage: float
    cancellation_coverage: float
    is_active: bool = True


class InsuranceBooking(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="insuranceplan.id")
    traveler_name: str
    contact_email: str
    booking_reference: str
    status: str = "confirmed"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InsurancePlanCreate(SQLModel):
    name: str
    description: str
    price_per_person: float
    coverage_types: str
    max_trip_value: float
    medical_coverage: float
    cancellation_coverage: float
    is_active: bool = True


class InsuranceBookingCreate(SQLModel):
    plan_id: int
    traveler_name: str
    contact_email: str
