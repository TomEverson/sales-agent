from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class FlightBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    flight_id: int = Field(foreign_key="flight.id")
    passenger_name: str
    contact_email: str
    booking_reference: str
    status: str = "confirmed"
    seats_booked: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FlightBookingCreate(SQLModel):
    flight_id: int
    passenger_name: str
    contact_email: str
    seats_booked: int = 1


class HotelBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hotel_id: int = Field(foreign_key="hotel.id")
    guest_name: str
    contact_email: str
    check_in_date: str
    check_out_date: str
    nights: int
    guests: int = 1
    booking_reference: str
    status: str = "confirmed"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HotelBookingCreate(SQLModel):
    hotel_id: int
    guest_name: str
    contact_email: str
    check_in_date: str
    check_out_date: str
    nights: int
    guests: int = 1


class ActivityBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="activity.id")
    participant_name: str
    contact_email: str
    activity_date: str
    participants: int = 1
    booking_reference: str
    status: str = "confirmed"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ActivityBookingCreate(SQLModel):
    activity_id: int
    participant_name: str
    contact_email: str
    activity_date: str
    participants: int = 1


class TransportBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transport_id: int = Field(foreign_key="transport.id")
    passenger_name: str
    contact_email: str
    passengers: int = 1
    booking_reference: str
    status: str = "confirmed"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TransportBookingCreate(SQLModel):
    transport_id: int
    passenger_name: str
    contact_email: str
    passengers: int = 1
