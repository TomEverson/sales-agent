import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel, select
from datetime import datetime

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from db import get_session
from models.flight import Flight
from models.hotel import Hotel
from models.activity import Activity
from models.transport import Transport
from models.booking import (
    FlightBooking,
    HotelBooking,
    ActivityBooking,
    TransportBooking,
)


TEST_DB_URL = "sqlite:///./test_travel.db"
test_engine = create_engine(TEST_DB_URL, echo=False)


def override_get_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True)
def setup_database():
    SQLModel.metadata.create_all(test_engine)
    yield
    with Session(test_engine) as session:
        for b in session.exec(select(FlightBooking)).all():
            session.delete(b)
        for b in session.exec(select(HotelBooking)).all():
            session.delete(b)
        for b in session.exec(select(ActivityBooking)).all():
            session.delete(b)
        for b in session.exec(select(TransportBooking)).all():
            session.delete(b)
        for f in session.exec(select(Flight)).all():
            session.delete(f)
        for h in session.exec(select(Hotel)).all():
            session.delete(h)
        for a in session.exec(select(Activity)).all():
            session.delete(a)
        for t in session.exec(select(Transport)).all():
            session.delete(t)
        session.commit()
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def seeded_flight():
    with Session(test_engine) as session:
        flight = Flight(
            origin="Bangkok",
            destination="Singapore",
            airline="AirAsia",
            departure_time=datetime(2026, 3, 28, 8, 0, 0),
            arrival_time=datetime(2026, 3, 28, 9, 30, 0),
            price=85.0,
            seats_available=10,
            class_type="economy",
        )
        session.add(flight)
        session.commit()
        session.refresh(flight)
        flight_id = flight.id
    with Session(test_engine) as session:
        return session.get(Flight, flight_id)


@pytest.fixture
def full_flight():
    with Session(test_engine) as session:
        flight = Flight(
            origin="Bangkok",
            destination="Singapore",
            airline="AirAsia",
            departure_time=datetime(2026, 3, 28, 8, 0, 0),
            arrival_time=datetime(2026, 3, 28, 9, 30, 0),
            price=85.0,
            seats_available=0,
            class_type="economy",
        )
        session.add(flight)
        session.commit()
        session.refresh(flight)
        flight_id = flight.id
    with Session(test_engine) as session:
        return session.get(Flight, flight_id)


@pytest.fixture
def seeded_hotel():
    with Session(test_engine) as session:
        hotel = Hotel(
            name="The Singapore Suites",
            location="Singapore",
            city="Singapore",
            stars=4,
            price_per_night=120.0,
            rooms_available=5,
            amenities="pool,wifi,gym",
        )
        session.add(hotel)
        session.commit()
        session.refresh(hotel)
        hotel_id = hotel.id
    with Session(test_engine) as session:
        return session.get(Hotel, hotel_id)


@pytest.fixture
def full_hotel():
    with Session(test_engine) as session:
        hotel = Hotel(
            name="Full Hotel",
            location="Singapore",
            city="Singapore",
            stars=3,
            price_per_night=80.0,
            rooms_available=0,
            amenities="wifi",
        )
        session.add(hotel)
        session.commit()
        session.refresh(hotel)
        hotel_id = hotel.id
    with Session(test_engine) as session:
        return session.get(Hotel, hotel_id)


@pytest.fixture
def seeded_activity():
    with Session(test_engine) as session:
        activity = Activity(
            name="Gardens by the Bay Tour",
            city="Singapore",
            description="Beautiful nature tour",
            duration_hours=3.0,
            price=25.0,
            category="nature",
            availability="daily",
        )
        session.add(activity)
        session.commit()
        session.refresh(activity)
        activity_id = activity.id
    with Session(test_engine) as session:
        return session.get(Activity, activity_id)


@pytest.fixture
def seeded_transport():
    with Session(test_engine) as session:
        transport = Transport(
            type="car",
            origin="Singapore Airport",
            destination="Singapore City",
            departure_time=datetime(2026, 3, 28, 10, 0, 0),
            arrival_time=datetime(2026, 3, 28, 10, 45, 0),
            price=30.0,
            capacity=4,
        )
        session.add(transport)
        session.commit()
        session.refresh(transport)
        transport_id = transport.id
    with Session(test_engine) as session:
        return session.get(Transport, transport_id)


@pytest.fixture
def full_transport():
    with Session(test_engine) as session:
        transport = Transport(
            type="car",
            origin="Singapore Airport",
            destination="Singapore City",
            departure_time=datetime(2026, 3, 28, 10, 0, 0),
            arrival_time=datetime(2026, 3, 28, 10, 45, 0),
            price=30.0,
            capacity=0,
        )
        session.add(transport)
        session.commit()
        session.refresh(transport)
        transport_id = transport.id
    with Session(test_engine) as session:
        return session.get(Transport, transport_id)


@pytest.fixture
def seeded_flight_booking(seeded_flight):
    with Session(test_engine) as session:
        booking = FlightBooking(
            flight_id=seeded_flight.id,
            passenger_name="John Smith",
            contact_email="john@example.com",
            booking_reference="TB-20260328-A3F7",
            status="confirmed",
            seats_booked=1,
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)
        booking_id = booking.id
    with Session(test_engine) as session:
        return session.get(FlightBooking, booking_id)


@pytest.fixture
def seeded_hotel_booking(seeded_hotel):
    with Session(test_engine) as session:
        booking = HotelBooking(
            hotel_id=seeded_hotel.id,
            guest_name="John Smith",
            contact_email="john@example.com",
            check_in_date="2026-03-28",
            check_out_date="2026-03-30",
            nights=2,
            guests=1,
            booking_reference="TB-20260328-B2K9",
            status="confirmed",
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)
        booking_id = booking.id
    with Session(test_engine) as session:
        return session.get(HotelBooking, booking_id)


@pytest.fixture
def seeded_activity_booking(seeded_activity):
    with Session(test_engine) as session:
        booking = ActivityBooking(
            activity_id=seeded_activity.id,
            participant_name="John Smith",
            contact_email="john@example.com",
            activity_date="2026-03-29",
            participants=1,
            booking_reference="TB-20260328-C5T1",
            status="confirmed",
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)
        booking_id = booking.id
    with Session(test_engine) as session:
        return session.get(ActivityBooking, booking_id)


@pytest.fixture
def seeded_transport_booking(seeded_transport):
    with Session(test_engine) as session:
        booking = TransportBooking(
            transport_id=seeded_transport.id,
            passenger_name="John Smith",
            contact_email="john@example.com",
            passengers=1,
            booking_reference="TB-20260328-D7R3",
            status="confirmed",
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)
        booking_id = booking.id
    with Session(test_engine) as session:
        return session.get(TransportBooking, booking_id)
