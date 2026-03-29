---
ticket: TB-14
type: feat
title: Flight Booking — Purchase a Flight Ticket
sprint: sprint-3
status: todo
component: server, salebot
depends_on: TB-01, TB-05, TB-09
---

# TB-14: Flight Booking — Purchase a Flight Ticket

## Context
Read `rules/base.md` before starting.
Read `rules/server.md` — you will be adding a new model and router to the FastAPI backend.
Read `rules/bot.md` — you will be adding a new MCP tool and updating the agent.
Read `server/models/flight.py` — the `Flight` model is the source of truth for flight data.
Read `salebot/mcp_tools.py` — you will be adding `book_flight` to the tool registry.
Read `salebot/prompts/system_prompt.md` — you will be adding a booking section.

## Dependency
TB-01 (search_flights tool) must be complete.
TB-05 (agent loop) must be complete.
TB-09 (Telegram bot) must be complete.

---

## Goal
Allow the user to book a flight directly through the Telegram bot.

After the agent presents a flight option, the user can say "book it" or "I want to book this flight".
The agent collects the passenger name and email, confirms the details with the user, then
calls the `book_flight` tool which creates a booking record in the database, decrements
`seats_available` on the flight, and returns a booking confirmation with a reference number.

---

## Files to create / modify

| File | Action |
|------|--------|
| `server/models/booking.py` | create — FlightBooking model |
| `server/routers/bookings.py` | create — booking endpoints |
| `server/main.py` | modify — register bookings router |
| `salebot/mcp_tools.py` | modify — add book_flight tool + executor |
| `salebot/prompts/system_prompt.md` | modify — add booking flow rules |
| `salebot/tests/test_mcp_tools.py` | modify — add TestBookFlight class |
| `server/tests/test_bookings.py` | create — server-side booking tests |

---

## What to build

### 1. Server — FlightBooking Model
Create `server/models/booking.py`:

```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class FlightBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    flight_id: int = Field(foreign_key="flight.id")
    passenger_name: str
    contact_email: str
    booking_reference: str  # format: TB-YYYYMMDD-XXXX
    status: str = "confirmed"  # confirmed | cancelled
    seats_booked: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FlightBookingCreate(SQLModel):
    flight_id: int
    passenger_name: str
    contact_email: str
    seats_booked: int = 1
```

### 2. Server — Booking Reference Generator
Add a module-level helper in `server/routers/bookings.py`:

```python
def generate_booking_reference() -> str:
    """Generate a reference in the format TB-YYYYMMDD-XXXX."""
```

- Format: `TB-{YYYYMMDD}-{4 random uppercase alphanumeric}`
- Example: `TB-20260328-A3F7`
- Use `random.choices(string.ascii_uppercase + string.digits, k=4)` for the suffix
- Must be unique — if a collision occurs, regenerate (check against DB)

### 3. Server — Bookings Router
Create `server/routers/bookings.py` with prefix `/bookings/flights`:

#### POST `/bookings/flights` — Create booking
- Accept `FlightBookingCreate` as request body
- Look up the flight by `flight_id` — return 404 if not found
- Check `seats_available >= seats_booked` — return 422 if insufficient:
  ```json
  {"detail": "Not enough seats available. Requested: 1, Available: 0"}
  ```
- Decrement `flight.seats_available` by `seats_booked` atomically
- Generate a `booking_reference`
- Create and persist the `FlightBooking` record
- Return the created booking with status 201

#### GET `/bookings/flights/{booking_id}` — Get booking
- Return the booking by id — 404 if not found

#### GET `/bookings/flights` — List bookings by email
- Optional query param: `email`
- If `email` provided → filter by `contact_email`
- If no `email` → return all bookings
- Returns list of `FlightBooking`

### 4. Server — Register Router
In `server/main.py`, add:
```python
from routers import flights, hotels, activities, transport, bookings

app.include_router(bookings.router)
```

### 5. MCP Tool — book_flight tool definition
Add to `salebot/mcp_tools.py`:

```python
book_flight_tool = {
    "name": "book_flight",
    "description": """Book a flight for the user.
    Call this tool ONLY after:
    1. The user has explicitly confirmed they want to book (e.g. "book it", "yes book this")
    2. You have collected passenger_name and contact_email from the user.
    Never call this tool speculatively. Always confirm details with the user before booking.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "flight_id": {
                "type": "integer",
                "description": "The id of the flight to book, from the search_flights result."
            },
            "passenger_name": {
                "type": "string",
                "description": "Full name of the passenger as it should appear on the ticket."
            },
            "contact_email": {
                "type": "string",
                "description": "Email address for the booking confirmation."
            },
            "seats_booked": {
                "type": "integer",
                "description": "Number of seats to book. Default 1. Use number of travelers from conversation."
            }
        },
        "required": ["flight_id", "passenger_name", "contact_email"]
    }
}
```

### 6. MCP Tool — execute_book_flight executor
Add to `salebot/mcp_tools.py`:

```python
async def execute_book_flight(input: dict) -> str:
```

- Extract `flight_id`, `passenger_name`, `contact_email`, `seats_booked` (default 1)
- `flight_id` is required — if missing return `"flight_id is required to book a flight."`
- `passenger_name` is required — if missing return `"Passenger name is required to book a flight."`
- `contact_email` is required — if missing return `"Contact email is required to book a flight."`
- Call `POST http://localhost:8000/bookings/flights` with JSON body
- On 201 → return formatted confirmation string:
  ```
  ✅ Booking confirmed!
  Reference: TB-20260328-A3F7
  Flight: {origin} → {destination} | {airline}
  Passenger: {passenger_name}
  Email: {contact_email}
  Status: confirmed
  ```
- On 422 (insufficient seats) → return `"Sorry, this flight no longer has enough seats available. Please search for another flight."`
- On 404 (flight not found) → return `"Flight not found. Please search for flights again."`
- On server unreachable → return `"Booking is currently unavailable. Please try again."`

### 7. MCP Tool — update TOOLS and dispatcher
Append `book_flight_tool` to the `TOOLS` list:
```python
TOOLS = [
    search_flights_tool,
    search_hotels_tool,
    search_activities_tool,
    search_transport_tool,
    book_flight_tool,       # ← added in TB-14
]
```

Add route in `execute_tool`:
```python
if tool_name == "book_flight":
    return await execute_book_flight(tool_input)
```

### 8. System Prompt — Booking Flow Rules
Append a new **Section 9: Booking Flow** to `salebot/prompts/system_prompt.md`:

```
## Section 9: Booking Flow

You can now book flights for users using the book_flight tool.

### When to offer booking
- After presenting a flight as part of a tour package, always ask:
  "Would you like me to book this flight for you?"
- If the user says yes or confirms ("book it", "go ahead", "yes"), start the booking flow.

### Booking flow — collect in order
1. Ask: "What is the passenger's full name?"
2. Ask: "What email should I send the confirmation to?"
3. Confirm details back to the user:
   "Just to confirm — booking for [name], confirmation to [email]. Shall I go ahead?"
4. Only after explicit confirmation → call book_flight tool.

### Hard rules for booking
- NEVER call book_flight without collecting passenger_name and contact_email first.
- NEVER call book_flight without explicit user confirmation ("yes", "go ahead", "book it").
- If book_flight returns a seat error → apologise and offer to search for alternatives.
- If booking succeeds → display the full confirmation returned by the tool.
- Always show the booking reference number prominently.
- After a successful booking, ask if the user wants to continue building the rest of the package (hotel, activities).
```

---

## File structure after TB-14
```
server/
├── models/
│   ├── booking.py          ← created
│   ├── flight.py           ← unchanged
│   └── ...
├── routers/
│   ├── bookings.py         ← created
│   ├── flights.py          ← unchanged
│   └── ...
├── main.py                 ← modified (router registered)
└── tests/
    └── test_bookings.py    ← created

salebot/
├── mcp_tools.py            ← modified (book_flight added)
├── prompts/
│   └── system_prompt.md    ← modified (Section 9 added)
└── tests/
    └── test_mcp_tools.py   ← modified (TestBookFlight added)
```

---

## Tests to write first

### Server tests — create `server/tests/test_bookings.py`
```python
class TestCreateFlightBooking:

    def test_creates_booking_with_valid_data(self, client, seeded_flight):
        """TB-14: valid booking request returns 201 with booking record."""

    def test_decrements_seats_available_on_booking(self, client, seeded_flight):
        """TB-14: seats_available on the flight is decremented after booking."""

    def test_returns_booking_reference(self, client, seeded_flight):
        """TB-14: response includes a booking_reference in TB-YYYYMMDD-XXXX format."""

    def test_booking_reference_format(self, client, seeded_flight):
        """TB-14: booking_reference matches pattern TB-\\d{8}-[A-Z0-9]{4}."""

    def test_returns_404_for_unknown_flight(self, client):
        """TB-14: booking with non-existent flight_id returns 404."""

    def test_returns_422_when_no_seats_available(self, client, full_flight):
        """TB-14: booking when seats_available == 0 returns 422."""

    def test_422_error_message_includes_seat_counts(self, client, full_flight):
        """TB-14: 422 detail message includes requested and available seat counts."""

    def test_status_is_confirmed_on_creation(self, client, seeded_flight):
        """TB-14: newly created booking has status confirmed."""

    def test_seats_booked_defaults_to_one(self, client, seeded_flight):
        """TB-14: seats_booked defaults to 1 when not provided."""

    def test_booking_multiple_seats(self, client, seeded_flight):
        """TB-14: booking 2 seats decrements seats_available by 2."""


class TestGetFlightBooking:

    def test_returns_booking_by_id(self, client, seeded_booking):
        """TB-14: GET /bookings/flights/{id} returns the correct booking."""

    def test_returns_404_for_unknown_booking(self, client):
        """TB-14: unknown booking_id returns 404."""


class TestListFlightBookings:

    def test_returns_all_bookings_without_filter(self, client, seeded_booking):
        """TB-14: GET /bookings/flights returns all bookings."""

    def test_filters_by_email(self, client, seeded_booking):
        """TB-14: email query param filters bookings by contact_email."""

    def test_returns_empty_list_for_unknown_email(self, client):
        """TB-14: unknown email returns empty list not 404."""
```

### Bot tests — add to `salebot/tests/test_mcp_tools.py`
```python
class TestBookFlight:

    async def test_returns_confirmation_on_success(self, respx_mock):
        """TB-14: successful booking returns formatted confirmation string."""

    async def test_confirmation_contains_booking_reference(self, respx_mock):
        """TB-14: confirmation string includes the booking reference from response."""

    async def test_flight_id_is_required(self):
        """TB-14: missing flight_id returns clear error message."""

    async def test_passenger_name_is_required(self):
        """TB-14: missing passenger_name returns clear error message."""

    async def test_contact_email_is_required(self):
        """TB-14: missing contact_email returns clear error message."""

    async def test_returns_seat_error_on_422(self, respx_mock):
        """TB-14: 422 response returns no-seats-available message."""

    async def test_returns_not_found_on_404(self, respx_mock):
        """TB-14: 404 response returns flight-not-found message."""

    async def test_returns_unavailable_on_connection_error(self, respx_mock):
        """TB-14: connection error returns booking unavailable message."""

    async def test_seats_booked_defaults_to_one(self, respx_mock):
        """TB-14: seats_booked of 1 is sent when not in input dict."""

    async def test_dispatcher_routes_book_flight(self, respx_mock):
        """TB-14: execute_tool routes book_flight to execute_book_flight."""

    async def test_tools_list_contains_five_tools(self):
        """TB-14: TOOLS list contains exactly 5 tools after TB-14."""
```

Add to `conftest.py`:
```python
@pytest.fixture
def mock_booking_response():
    """TB-14: sample FlightBooking response from server."""
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
```

---

## Acceptance Criteria

### Server
- [ ] `FlightBooking` model exists with all required fields
- [ ] `FlightBookingCreate` schema exists
- [ ] `POST /bookings/flights` creates a booking and returns 201
- [ ] `POST /bookings/flights` decrements `flight.seats_available` by `seats_booked`
- [ ] `POST /bookings/flights` returns 404 when `flight_id` does not exist
- [ ] `POST /bookings/flights` returns 422 when `seats_available < seats_booked`
- [ ] 422 detail message includes both requested and available seat counts
- [ ] `booking_reference` matches format `TB-YYYYMMDD-XXXX`
- [ ] `status` defaults to `"confirmed"` on creation
- [ ] `seats_booked` defaults to `1`
- [ ] `GET /bookings/flights/{booking_id}` returns booking or 404
- [ ] `GET /bookings/flights?email=...` filters by `contact_email`
- [ ] Bookings router registered in `main.py`

### Salebot
- [ ] `book_flight_tool` dict exists in `mcp_tools.py` with valid Anthropic format
- [ ] `flight_id`, `passenger_name`, `contact_email` are required fields in input_schema
- [ ] `seats_booked` is optional, defaults to 1
- [ ] `execute_book_flight(input: dict) -> str` exists with exact signature
- [ ] Missing `flight_id` returns `"flight_id is required to book a flight."`
- [ ] Missing `passenger_name` returns `"Passenger name is required to book a flight."`
- [ ] Missing `contact_email` returns `"Contact email is required to book a flight."`
- [ ] Successful booking returns confirmation string containing the booking reference
- [ ] 422 response returns no-seats message
- [ ] 404 response returns flight-not-found message
- [ ] Server unreachable returns booking unavailable message
- [ ] `book_flight_tool` appended to `TOOLS` (now 5 tools total)
- [ ] `execute_tool` dispatcher routes `"book_flight"` correctly

### System Prompt
- [ ] Section 9 added with booking flow rules
- [ ] Prompt instructs agent to collect name and email before calling `book_flight`
- [ ] Prompt instructs agent to confirm details before booking
- [ ] Prompt instructs agent to NEVER call `book_flight` speculatively

### Tests
- [ ] All server tests in `test_bookings.py` pass
- [ ] All bot tests in `TestBookFlight` pass
- [ ] All previously passing tests still pass (no regression)
- [ ] `uv run ruff check .` passes with no errors

---

## Manual test script

### Server
```python
import httpx

base = "http://localhost:8000"

# Test 1: create booking
r = httpx.post(f"{base}/bookings/flights", json={
    "flight_id": 1,
    "passenger_name": "John Smith",
    "contact_email": "john@example.com"
})
print("Test 1 status:", r.status_code)  # 201
print("Test 1 body:", r.json())
ref = r.json()["booking_reference"]
booking_id = r.json()["id"]

# Test 2: seats decremented
r2 = httpx.get(f"{base}/flights/1")
print("Test 2 seats_available:", r2.json()["seats_available"])  # original - 1

# Test 3: get by id
r3 = httpx.get(f"{base}/bookings/flights/{booking_id}")
print("Test 3 reference:", r3.json()["booking_reference"])  # same as above

# Test 4: list by email
r4 = httpx.get(f"{base}/bookings/flights", params={"email": "john@example.com"})
print("Test 4 count:", len(r4.json()))  # 1

# Test 5: 404 unknown flight
r5 = httpx.post(f"{base}/bookings/flights", json={
    "flight_id": 9999,
    "passenger_name": "Jane",
    "contact_email": "jane@example.com"
})
print("Test 5 status:", r5.status_code)  # 404
```

### Bot (via Telegram)
```
User: I want to visit Singapore this weekend, budget $1000
→ Agent searches and presents package

User: Book the flight
→ Agent asks: "What is the passenger's full name?"

User: John Smith
→ Agent asks: "What email should I send the confirmation to?"

User: john@example.com
→ Agent confirms: "Booking for John Smith, confirmation to john@example.com. Shall I go ahead?"

User: Yes
→ Agent calls book_flight tool
→ Agent responds with:
   ✅ Booking confirmed!
   Reference: TB-20260328-XXXX
   Flight: Bangkok → Singapore | AirAsia
   Passenger: John Smith
   Email: john@example.com
   Status: confirmed
```

---

## Definition of Done
- [ ] All acceptance criteria checked off above
- [ ] All tests pass: `cd server && uv run pytest tests/ -v` and `cd salebot && uv run pytest tests/ -v`
- [ ] Lint clean: `uv run ruff check .` in both `server/` and `salebot/`
- [ ] Manual Telegram flow tested end-to-end with real tokens
- [ ] `seats_available` verified to decrement in the database after booking

## When done
Print: ✅ TB-14 complete
