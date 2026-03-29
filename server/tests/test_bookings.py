"""TB-23: Server booking tests."""

import re
import pytest
from sqlmodel import Session, select

from models.flight import Flight
from models.hotel import Hotel
from models.activity import Activity
from models.transport import Transport
from tests.conftest import test_engine


def get_flight_seats(flight_id: int) -> int:
    with Session(test_engine) as session:
        flight = session.get(Flight, flight_id)
        return flight.seats_available if flight else 0


def get_hotel_rooms(hotel_id: int) -> int:
    with Session(test_engine) as session:
        hotel = session.get(Hotel, hotel_id)
        return hotel.rooms_available if hotel else 0


def get_transport_capacity(transport_id: int) -> int:
    with Session(test_engine) as session:
        transport = session.get(Transport, transport_id)
        return transport.capacity if transport else 0


# ============================================================================
# Flight Booking Tests
# ============================================================================


class TestCreateFlightBooking:
    def test_creates_booking_with_valid_data(self, client, seeded_flight):
        """TB-23: valid booking request returns 201 with booking record."""
        response = client.post(
            "/bookings/flights",
            json={
                "flight_id": seeded_flight.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
                "seats_booked": 1,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["passenger_name"] == "John Smith"
        assert data["contact_email"] == "john@example.com"
        assert data["seats_booked"] == 1

    def test_decrements_seats_available_on_booking(self, client, seeded_flight):
        """TB-23: seats_available on the flight is decremented after booking."""
        original_seats = get_flight_seats(seeded_flight.id)
        response = client.post(
            "/bookings/flights",
            json={
                "flight_id": seeded_flight.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
                "seats_booked": 2,
            },
        )
        assert response.status_code == 201
        assert get_flight_seats(seeded_flight.id) == original_seats - 2

    def test_returns_booking_reference(self, client, seeded_flight):
        """TB-23: response includes a booking_reference in TB-YYYYMMDD-XXXX format."""
        response = client.post(
            "/bookings/flights",
            json={
                "flight_id": seeded_flight.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "booking_reference" in data
        assert re.match(r"TB-\d{8}-[A-Z0-9]{4}", data["booking_reference"])

    def test_booking_reference_format(self, client, seeded_flight):
        """TB-23: booking_reference matches pattern TB-\\d{8}-[A-Z0-9]{4}."""
        response = client.post(
            "/bookings/flights",
            json={
                "flight_id": seeded_flight.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert response.status_code == 201
        data = response.json()
        ref = data["booking_reference"]
        assert re.match(r"^TB-\d{8}-[A-Z0-9]{4}$", ref)

    def test_returns_404_for_unknown_flight(self, client):
        """TB-23: booking with non-existent flight_id returns 404."""
        response = client.post(
            "/bookings/flights",
            json={
                "flight_id": 99999,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert response.status_code == 404

    def test_returns_422_when_no_seats_available(self, client, full_flight):
        """TB-23: booking when seats_available == 0 returns 422."""
        response = client.post(
            "/bookings/flights",
            json={
                "flight_id": full_flight.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert response.status_code == 422

    def test_422_error_message_includes_seat_counts(self, client, full_flight):
        """TB-23: 422 detail message includes requested and available seat counts."""
        response = client.post(
            "/bookings/flights",
            json={
                "flight_id": full_flight.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
                "seats_booked": 2,
            },
        )
        assert response.status_code == 422

    def test_status_is_confirmed_on_creation(self, client, seeded_flight):
        """TB-23: newly created booking has status confirmed."""
        response = client.post(
            "/bookings/flights",
            json={
                "flight_id": seeded_flight.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "confirmed"

    def test_seats_booked_defaults_to_one(self, client, seeded_flight):
        """TB-23: seats_booked defaults to 1 when not provided."""
        response = client.post(
            "/bookings/flights",
            json={
                "flight_id": seeded_flight.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["seats_booked"] == 1

    def test_booking_multiple_seats(self, client, seeded_flight):
        """TB-23: booking 2 seats decrements seats_available by 2."""
        response = client.post(
            "/bookings/flights",
            json={
                "flight_id": seeded_flight.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
                "seats_booked": 2,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["seats_booked"] == 2


class TestGetFlightBooking:
    def test_returns_booking_by_id(self, client, seeded_flight_booking):
        """TB-23: GET /bookings/flights/{id} returns the correct booking."""
        response = client.get(f"/bookings/flights/{seeded_flight_booking.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == seeded_flight_booking.id
        assert data["passenger_name"] == "John Smith"

    def test_returns_404_for_unknown_booking(self, client):
        """TB-23: unknown booking_id returns 404."""
        response = client.get("/bookings/flights/99999")
        assert response.status_code == 404


class TestListFlightBookings:
    def test_returns_all_bookings_without_filter(self, client, seeded_flight_booking):
        """TB-23: GET /bookings/flights returns all bookings."""
        response = client.get("/bookings/flights")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_filters_by_email(self, client, seeded_flight_booking):
        """TB-23: email query param filters bookings by contact_email."""
        response = client.get("/bookings/flights?email=john@example.com")
        assert response.status_code == 200
        data = response.json()
        assert all(b["contact_email"] == "john@example.com" for b in data)

    def test_returns_empty_list_for_unknown_email(self, client):
        """TB-23: unknown email returns empty list not 404."""
        response = client.get("/bookings/flights?email=unknown@example.com")
        assert response.status_code == 200
        data = response.json()
        assert data == []


# ============================================================================
# Hotel Booking Tests
# ============================================================================


class TestCreateHotelBooking:
    def test_creates_booking_with_valid_data(self, client, seeded_hotel):
        """TB-23: valid hotel booking returns 201."""
        response = client.post(
            "/bookings/hotels",
            json={
                "hotel_id": seeded_hotel.id,
                "guest_name": "John Smith",
                "contact_email": "john@example.com",
                "check_in_date": "2026-03-28",
                "check_out_date": "2026-03-30",
                "nights": 2,
                "guests": 1,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["guest_name"] == "John Smith"

    def test_decrements_rooms_available_on_booking(self, client, seeded_hotel):
        """TB-23: rooms_available decremented after hotel booking."""
        original_rooms = get_hotel_rooms(seeded_hotel.id)
        response = client.post(
            "/bookings/hotels",
            json={
                "hotel_id": seeded_hotel.id,
                "guest_name": "John Smith",
                "contact_email": "john@example.com",
                "check_in_date": "2026-03-28",
                "check_out_date": "2026-03-30",
                "nights": 2,
                "guests": 1,
            },
        )
        assert response.status_code == 201
        assert get_hotel_rooms(seeded_hotel.id) == original_rooms - 1

    def test_returns_booking_reference(self, client, seeded_hotel):
        """TB-23: hotel booking returns reference."""
        response = client.post(
            "/bookings/hotels",
            json={
                "hotel_id": seeded_hotel.id,
                "guest_name": "John Smith",
                "contact_email": "john@example.com",
                "check_in_date": "2026-03-28",
                "check_out_date": "2026-03-30",
                "nights": 2,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "booking_reference" in data

    def test_returns_404_for_unknown_hotel(self, client):
        """TB-23: booking non-existent hotel returns 404."""
        response = client.post(
            "/bookings/hotels",
            json={
                "hotel_id": 99999,
                "guest_name": "John Smith",
                "contact_email": "john@example.com",
                "check_in_date": "2026-03-28",
                "check_out_date": "2026-03-30",
                "nights": 2,
            },
        )
        assert response.status_code == 404

    def test_returns_422_when_no_rooms_available(self, client, full_hotel):
        """TB-23: booking full hotel returns 422."""
        response = client.post(
            "/bookings/hotels",
            json={
                "hotel_id": full_hotel.id,
                "guest_name": "John Smith",
                "contact_email": "john@example.com",
                "check_in_date": "2026-03-28",
                "check_out_date": "2026-03-30",
                "nights": 2,
            },
        )
        assert response.status_code == 422

    def test_status_is_confirmed_on_creation(self, client, seeded_hotel):
        """TB-23: hotel booking status is confirmed."""
        response = client.post(
            "/bookings/hotels",
            json={
                "hotel_id": seeded_hotel.id,
                "guest_name": "John Smith",
                "contact_email": "john@example.com",
                "check_in_date": "2026-03-28",
                "check_out_date": "2026-03-30",
                "nights": 2,
            },
        )
        assert response.status_code == 201
        assert response.json()["status"] == "confirmed"

    def test_guests_defaults_to_one(self, client, seeded_hotel):
        """TB-23: guests defaults to 1."""
        response = client.post(
            "/bookings/hotels",
            json={
                "hotel_id": seeded_hotel.id,
                "guest_name": "John Smith",
                "contact_email": "john@example.com",
                "check_in_date": "2026-03-28",
                "check_out_date": "2026-03-30",
                "nights": 2,
            },
        )
        assert response.status_code == 201
        assert response.json()["guests"] == 1


class TestGetHotelBooking:
    def test_returns_booking_by_id(self, client, seeded_hotel_booking):
        """TB-23: GET /bookings/hotels/{id} returns booking."""
        response = client.get(f"/bookings/hotels/{seeded_hotel_booking.id}")
        assert response.status_code == 200
        assert response.json()["id"] == seeded_hotel_booking.id

    def test_returns_404_for_unknown_booking(self, client):
        """TB-23: unknown hotel booking returns 404."""
        response = client.get("/bookings/hotels/99999")
        assert response.status_code == 404


class TestListHotelBookings:
    def test_returns_all_bookings(self, client, seeded_hotel_booking):
        """TB-23: GET /bookings/hotels returns all bookings."""
        response = client.get("/bookings/hotels")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_filters_by_email(self, client, seeded_hotel_booking):
        """TB-23: email param filters hotel bookings."""
        response = client.get("/bookings/hotels?email=john@example.com")
        assert response.status_code == 200
        data = response.json()
        assert all(b["contact_email"] == "john@example.com" for b in data)

    def test_returns_empty_for_unknown_email(self, client):
        """TB-23: unknown email returns empty list."""
        response = client.get("/bookings/hotels?email=noone@example.com")
        assert response.status_code == 200
        assert response.json() == []


# ============================================================================
# Activity Booking Tests
# ============================================================================


class TestCreateActivityBooking:
    def test_creates_booking_with_valid_data(self, client, seeded_activity):
        """TB-23: valid activity booking returns 201."""
        response = client.post(
            "/bookings/activities",
            json={
                "activity_id": seeded_activity.id,
                "participant_name": "John Smith",
                "contact_email": "john@example.com",
                "activity_date": "2026-03-29",
                "participants": 1,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["participant_name"] == "John Smith"

    def test_returns_booking_reference(self, client, seeded_activity):
        """TB-23: activity booking returns reference."""
        response = client.post(
            "/bookings/activities",
            json={
                "activity_id": seeded_activity.id,
                "participant_name": "John Smith",
                "contact_email": "john@example.com",
                "activity_date": "2026-03-29",
            },
        )
        assert response.status_code == 201
        assert "booking_reference" in response.json()

    def test_returns_404_for_unknown_activity(self, client):
        """TB-23: booking non-existent activity returns 404."""
        response = client.post(
            "/bookings/activities",
            json={
                "activity_id": 99999,
                "participant_name": "John Smith",
                "contact_email": "john@example.com",
                "activity_date": "2026-03-29",
            },
        )
        assert response.status_code == 404

    def test_status_is_confirmed(self, client, seeded_activity):
        """TB-23: activity booking status is confirmed."""
        response = client.post(
            "/bookings/activities",
            json={
                "activity_id": seeded_activity.id,
                "participant_name": "John Smith",
                "contact_email": "john@example.com",
                "activity_date": "2026-03-29",
            },
        )
        assert response.status_code == 201
        assert response.json()["status"] == "confirmed"

    def test_participants_defaults_to_one(self, client, seeded_activity):
        """TB-23: participants defaults to 1."""
        response = client.post(
            "/bookings/activities",
            json={
                "activity_id": seeded_activity.id,
                "participant_name": "John Smith",
                "contact_email": "john@example.com",
                "activity_date": "2026-03-29",
            },
        )
        assert response.status_code == 201
        assert response.json()["participants"] == 1


class TestGetActivityBooking:
    def test_returns_booking_by_id(self, client, seeded_activity_booking):
        """TB-23: GET /bookings/activities/{id} returns booking."""
        response = client.get(f"/bookings/activities/{seeded_activity_booking.id}")
        assert response.status_code == 200
        assert response.json()["id"] == seeded_activity_booking.id

    def test_returns_404_for_unknown_booking(self, client):
        """TB-23: unknown activity booking returns 404."""
        response = client.get("/bookings/activities/99999")
        assert response.status_code == 404


class TestListActivityBookings:
    def test_returns_all_bookings(self, client, seeded_activity_booking):
        """TB-23: GET /bookings/activities returns all."""
        response = client.get("/bookings/activities")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_filters_by_email(self, client, seeded_activity_booking):
        """TB-23: email param filters activity bookings."""
        response = client.get("/bookings/activities?email=john@example.com")
        assert response.status_code == 200
        data = response.json()
        assert all(b["contact_email"] == "john@example.com" for b in data)


# ============================================================================
# Transport Booking Tests
# ============================================================================


class TestCreateTransportBooking:
    def test_creates_booking_with_valid_data(self, client, seeded_transport):
        """TB-23: valid transport booking returns 201."""
        response = client.post(
            "/bookings/transport",
            json={
                "transport_id": seeded_transport.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
                "passengers": 1,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["passenger_name"] == "John Smith"

    def test_decrements_capacity_on_booking(self, client, seeded_transport):
        """TB-23: capacity decremented after transport booking."""
        original_capacity = get_transport_capacity(seeded_transport.id)
        response = client.post(
            "/bookings/transport",
            json={
                "transport_id": seeded_transport.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
                "passengers": 2,
            },
        )
        assert response.status_code == 201
        assert get_transport_capacity(seeded_transport.id) == original_capacity - 2

    def test_returns_booking_reference(self, client, seeded_transport):
        """TB-23: transport booking returns reference."""
        response = client.post(
            "/bookings/transport",
            json={
                "transport_id": seeded_transport.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert response.status_code == 201
        assert "booking_reference" in response.json()

    def test_returns_404_for_unknown_transport(self, client):
        """TB-23: booking non-existent transport returns 404."""
        response = client.post(
            "/bookings/transport",
            json={
                "transport_id": 99999,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert response.status_code == 404

    def test_returns_422_when_no_capacity(self, client, full_transport):
        """TB-23: booking full transport returns 422."""
        response = client.post(
            "/bookings/transport",
            json={
                "transport_id": full_transport.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert response.status_code == 422

    def test_status_is_confirmed(self, client, seeded_transport):
        """TB-23: transport booking status is confirmed."""
        response = client.post(
            "/bookings/transport",
            json={
                "transport_id": seeded_transport.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert response.status_code == 201
        assert response.json()["status"] == "confirmed"

    def test_passengers_defaults_to_one(self, client, seeded_transport):
        """TB-23: passengers defaults to 1."""
        response = client.post(
            "/bookings/transport",
            json={
                "transport_id": seeded_transport.id,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert response.status_code == 201
        assert response.json()["passengers"] == 1


class TestGetTransportBooking:
    def test_returns_booking_by_id(self, client, seeded_transport_booking):
        """TB-23: GET /bookings/transport/{id} returns booking."""
        response = client.get(f"/bookings/transport/{seeded_transport_booking.id}")
        assert response.status_code == 200
        assert response.json()["id"] == seeded_transport_booking.id

    def test_returns_404_for_unknown_booking(self, client):
        """TB-23: unknown transport booking returns 404."""
        response = client.get("/bookings/transport/99999")
        assert response.status_code == 404


class TestListTransportBookings:
    def test_returns_all_bookings(self, client, seeded_transport_booking):
        """TB-23: GET /bookings/transport returns all."""
        response = client.get("/bookings/transport")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_filters_by_email(self, client, seeded_transport_booking):
        """TB-23: email param filters transport bookings."""
        response = client.get("/bookings/transport?email=john@example.com")
        assert response.status_code == 200
        data = response.json()
        assert all(b["contact_email"] == "john@example.com" for b in data)

    def test_returns_empty_for_unknown_email(self, client):
        """TB-23: unknown email returns empty list."""
        response = client.get("/bookings/transport?email=noone@example.com")
        assert response.status_code == 200
        assert response.json() == []
