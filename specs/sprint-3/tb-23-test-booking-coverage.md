---
ticket: TB-23
type: test
title: Test Coverage — Server & Bot Booking Tests
sprint: sprint-3
status: todo
component: server, salebot
depends_on: TB-14, TB-15, TB-16, TB-17
---

# TB-23: Test Coverage — Server & Bot Booking Tests

## Context
Read `rules/base.md` before starting.
Read `server/routers/bookings.py` — you will be testing these endpoints.
Read `salebot/mcp_tools.py` — you will be testing the booking executors.

## Dependency
TB-14 (flight booking), TB-15 (hotel booking), TB-16 (activity booking), TB-17 (transport booking) must be complete.

---

## Goal
Add comprehensive test coverage for all booking-related functionality:
1. Server-side tests for booking endpoints
2. Bot-side tests for booking tool executors

---

## Files to create / modify

| File | Action |
|------|--------|
| `server/pyproject.toml` | modify — add pytest dependencies |
| `server/tests/__init__.py` | create |
| `server/tests/conftest.py` | create — fixtures |
| `server/tests/test_bookings.py` | create — all server booking tests |
| `salebot/tests/conftest.py` | modify — add booking response fixtures |
| `salebot/tests/test_mcp_tools.py` | modify — add booking test classes |

---

## What to build

### 1. Server — Add pytest dependencies

Add to `server/pyproject.toml`:
```toml
[dependency-groups]
dev = [
    "ruff>=0.15.8",
    "pytest>=8.0.0",
    "httpx>=0.27.0",
]
```

### 2. Server — Fixtures (`server/tests/conftest.py`)

Create with:
- `client` - FastAPI TestClient with app
- `seeded_flight` - flight with seats_available=10
- `full_flight` - flight with seats_available=0
- `seeded_hotel`, `full_hotel`
- `seeded_activity`
- `seeded_transport`, `full_transport`
- `seeded_flight_booking`, `seeded_hotel_booking`, etc.

### 3. Server — Booking Tests

Create `server/tests/test_bookings.py` with:

```python
# TestCreateFlightBooking
- test_creates_booking_with_valid_data
- test_decrements_seats_available_on_booking
- test_returns_booking_reference
- test_booking_reference_format
- test_returns_404_for_unknown_flight
- test_returns_422_when_no_seats_available
- test_422_error_message_includes_seat_counts
- test_status_is_confirmed_on_creation
- test_seats_booked_defaults_to_one
- test_booking_multiple_seats

# TestGetFlightBooking
- test_returns_booking_by_id
- test_returns_404_for_unknown_booking

# TestListFlightBookings
- test_returns_all_bookings_without_filter
- test_filters_by_email
- test_returns_empty_list_for_unknown_email

# TestCreateHotelBooking (8 tests)
# TestGetHotelBooking (2 tests)
# TestListHotelBookings (3 tests)

# TestCreateActivityBooking (6 tests)
# TestGetActivityBooking (2 tests)
# TestListActivityBookings (2 tests)

# TestCreateTransportBooking (8 tests)
# TestGetTransportBooking (2 tests)
# TestListTransportBookings (3 tests)
```

### 4. Bot — Add fixtures to `salebot/tests/conftest.py`

```python
@pytest.fixture
def mock_booking_response():
    """TB-23: sample FlightBooking response from server."""
    return {
        "id": 1,
        "flight_id": 1,
        "passenger_name": "John Smith",
        "contact_email": "john@example.com",
        "booking_reference": "TB-20260328-A3F7",
        "status": "confirmed",
        "seats_booked": 1,
        "created_at": "2026-03-28T10:00:00"
    }

@pytest.fixture
def mock_hotel_booking_response():
    """TB-23: sample HotelBooking response from server."""
    return {
        "id": 1,
        "hotel_id": 1,
        "guest_name": "John Smith",
        "contact_email": "john@example.com",
        "check_in_date": "2026-03-28",
        "check_out_date": "2026-03-30",
        "nights": 2,
        "guests": 1,
        "booking_reference": "TB-20260328-B2K9",
        "status": "confirmed",
        "created_at": "2026-03-28T10:00:00"
    }

@pytest.fixture
def mock_activity_booking_response():
    """TB-23: sample ActivityBooking response from server."""
    return {
        "id": 1,
        "activity_id": 1,
        "participant_name": "John Smith",
        "contact_email": "john@example.com",
        "activity_date": "2026-03-29",
        "participants": 1,
        "booking_reference": "TB-20260328-C5T1",
        "status": "confirmed",
        "created_at": "2026-03-28T10:00:00"
    }

@pytest.fixture
def mock_transport_booking_response():
    """TB-23: sample TransportBooking response from server."""
    return {
        "id": 1,
        "transport_id": 1,
        "passenger_name": "John Smith",
        "contact_email": "john@example.com",
        "passengers": 1,
        "booking_reference": "TB-20260328-D7R3",
        "status": "confirmed",
        "created_at": "2026-03-28T10:00:00"
    }
```

### 5. Bot — Add test classes to `salebot/tests/test_mcp_tools.py`

```python
class TestBookFlight:
    - test_returns_confirmation_on_success
    - test_confirmation_contains_booking_reference
    - test_flight_id_is_required
    - test_passenger_name_is_required
    - test_contact_email_is_required
    - test_returns_seat_error_on_422
    - test_returns_not_found_on_404
    - test_returns_unavailable_on_connection_error
    - test_seats_booked_defaults_to_one
    - test_dispatcher_routes_book_flight
    - test_tools_list_contains_five_tools

class TestBookHotel (10 tests):
    - test_returns_confirmation_on_success
    - test_confirmation_contains_booking_reference
    - test_hotel_id_is_required
    - test_guest_name_is_required
    - test_contact_email_is_required
    - test_check_in_date_is_required
    - test_check_out_date_is_required
    - test_nights_is_required
    - test_returns_room_error_on_422
    - test_dispatcher_routes_book_hotel

class TestBookActivity (8 tests):
    - test_returns_confirmation_on_success
    - test_activity_id_is_required
    - test_participant_name_is_required
    - test_contact_email_is_required
    - test_activity_date_is_required
    - test_returns_not_found_on_404
    - test_no_capacity_limit
    - test_dispatcher_routes_book_activity

class TestBookTransport (10 tests):
    - test_returns_confirmation_on_success
    - test_transport_id_is_required
    - test_passenger_name_is_required
    - test_contact_email_is_required
    - test_returns_capacity_error_on_422
    - test_passengers_max_is_capacity
    - test_dispatcher_routes_book_transport
```

---

## Acceptance Criteria

### Server Tests
- [ ] All server booking tests pass
- [ ] Tests cover: create, get by id, list, list with email filter
- [ ] Tests cover: 404, 422 error cases
- [ ] Tests verify inventory decrement (flights, hotels, transport)
- [ ] Tests verify reference format

### Bot Tests
- [ ] All bot booking tests pass
- [ ] Tests verify success confirmation message
- [ ] Tests verify validation error messages
- [ ] Tests verify error handling (404, 422, connection)
- [ ] Tests verify dispatcher routing
- [ ] Tests verify TOOLS list has 8 tools

### General
- [ ] Run `pytest` and all tests pass
- [ ] No `pytest` warnings about missing fixtures

---

## Manual test

1. Install pytest in server: `cd server && uv add --dev pytest httpx`
2. Run server tests: `cd server && uv run pytest tests/ -v`
3. Run bot tests: `cd salebot && uv run pytest tests/test_mcp_tools.py -v`
4. Verify all booking tests pass

---

## When done
Print: ✅ TB-23 complete
