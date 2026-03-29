---
ticket: TB-17
type: feat
title: Transport Booking — Book a Transport Option
sprint: sprint-3
status: todo
component: server, salebot
depends_on: TB-14
---

# TB-17: Transport Booking — Book a Transport Option

## Context
Read `rules/base.md` before starting.
Read `rules/server.md` — adding a new model and endpoints to FastAPI.
Read `server/models/booking.py` from TB-14 — follow the same pattern.
Read `server/routers/bookings.py` — reuse `generate_booking_reference()`.
Read `server/models/transport.py` — `Transport` uses `capacity` (not `seats_available`).
Read `salebot/mcp_tools.py` — adding `book_transport` to the tool registry.
Read `salebot/prompts/system_prompt.md` — extending Section 9.

## Dependency
TB-14 must be complete.
`generate_booking_reference()` must already exist in `server/routers/bookings.py`.

---

## Goal
Allow the user to book a transport option through the Telegram bot.
After the agent presents a transport option, the user can confirm they want to book.
The agent collects passenger name, email, and number of passengers, then calls
`book_transport` which creates a `TransportBooking` record, decrements `capacity`
on the transport, and returns a booking confirmation.

**Key difference from flights:** Transport uses `capacity` (not `seats_available`).
The decrement and 422 check apply to `capacity`.

---

## Files to create / modify

| File | Action |
|------|--------|
| `server/models/booking.py` | modify — add TransportBooking, TransportBookingCreate |
| `server/routers/bookings.py` | modify — add transport booking endpoints |
| `salebot/mcp_tools.py` | modify — add book_transport tool + executor |
| `salebot/prompts/system_prompt.md` | modify — extend Section 9 with transport rules |
| `salebot/tests/test_mcp_tools.py` | modify — add TestBookTransport class |
| `server/tests/test_bookings.py` | modify — add transport booking test classes |

---

## What to build

### 1. Server — TransportBooking Model
Add to `server/models/booking.py`:

```python
class TransportBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transport_id: int = Field(foreign_key="transport.id")
    passenger_name: str
    contact_email: str
    passengers: int = 1
    booking_reference: str   # format: TB-YYYYMMDD-XXXX
    status: str = "confirmed"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TransportBookingCreate(SQLModel):
    transport_id: int
    passenger_name: str
    contact_email: str
    passengers: int = 1
```

### 2. Server — Transport Booking Endpoints
Add to `server/routers/bookings.py` with prefix `/bookings/transport`:

#### POST `/bookings/transport` — Create booking
- Look up transport by `transport_id` → 404 if not found
- Check `transport.capacity >= passengers` → 422 if insufficient:
  ```json
  {"detail": "Not enough capacity available. Requested: 3, Available: 2"}
  ```
- Decrement `transport.capacity` by `passengers`
- Generate `booking_reference` using `generate_booking_reference()`
- Persist and return the `TransportBooking` with status 201

#### GET `/bookings/transport/{booking_id}` — Get booking
- Return booking by id — 404 if not found

#### GET `/bookings/transport` — List bookings
- Optional query param: `email`
- Filter by `contact_email` when provided

### 3. MCP Tool — book_transport tool definition
Add to `salebot/mcp_tools.py`:

```python
book_transport_tool = {
    "name": "book_transport",
    "description": """Book a transport option for the user.
    Call this tool ONLY after:
    1. The user has explicitly confirmed they want to book.
    2. You have collected passenger_name and contact_email.
    Transport is optional in a package — only book if the user explicitly requests it.
    Never call this tool speculatively.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "transport_id": {
                "type": "integer",
                "description": "The id of the transport to book, from the search_transport result."
            },
            "passenger_name": {
                "type": "string",
                "description": "Full name of the primary passenger."
            },
            "contact_email": {
                "type": "string",
                "description": "Email address for the booking confirmation."
            },
            "passengers": {
                "type": "integer",
                "description": "Number of passengers. Default 1."
            }
        },
        "required": ["transport_id", "passenger_name", "contact_email"]
    }
}
```

### 4. MCP Tool — execute_book_transport executor
Add to `salebot/mcp_tools.py`:

```python
async def execute_book_transport(input: dict) -> str:
```

- Required: `transport_id`, `passenger_name`, `contact_email`
- Missing `transport_id` → `"transport_id is required to book transport."`
- Missing `passenger_name` → `"Passenger name is required to book transport."`
- Missing `contact_email` → `"Contact email is required to book transport."`
- `passengers` optional, default 1
- Call `POST http://localhost:8000/bookings/transport`
- On 201 → return formatted confirmation:
  ```
  ✅ Transport booking confirmed!
  Reference: TB-20260328-D7R3
  Route: {origin} → {destination} | {type}
  Passenger: {passenger_name}
  Passengers: {passengers}
  Email: {contact_email}
  Status: confirmed
  ```
- On 422 → `"Sorry, this transport option no longer has enough capacity. Please search for another option."`
- On 404 → `"Transport not found. Please search for transport again."`
- On server unreachable → `"Transport booking is currently unavailable. Please try again."`

### 5. MCP Tool — update TOOLS and dispatcher
Append `book_transport_tool` to `TOOLS` (now 8 tools):
```python
TOOLS = [
    search_flights_tool,
    search_hotels_tool,
    search_activities_tool,
    search_transport_tool,
    book_flight_tool,
    book_hotel_tool,
    book_activity_tool,
    book_transport_tool,    # ← added in TB-17
]
```

Add route in `execute_tool`:
```python
if tool_name == "book_transport":
    return await execute_book_transport(tool_input)
```

### 6. System Prompt — extend Section 9
Append to Section 9 in `salebot/prompts/system_prompt.md`:

```
### Transport booking flow
- Transport is optional — only offer to book it if it was included in the package
  or the user specifically asks for it.
- After presenting transport, ask: "Would you like me to book this transfer for you?"
- If yes, collect in order:
  1. Passenger name (reuse from earlier in the conversation if already collected)
  2. Contact email (reuse if already collected)
  3. Number of passengers (default 1)
- Confirm: "Booking [type] from [origin] to [destination] for [passenger_name]. Shall I go ahead?"
- Only after confirmation → call book_transport.
- If transport has no capacity → apologise and offer to search for alternatives.
- Transport booking is typically the last booking in a full package flow
  (after flight → hotel → activities → transport).
```

---

## File structure after TB-17
```
server/
├── models/
│   └── booking.py       ← modified (TransportBooking added)
├── routers/
│   └── bookings.py      ← modified (transport endpoints added)
└── tests/
    └── test_bookings.py ← modified (transport test classes added)

salebot/
├── mcp_tools.py          ← modified (book_transport added, TOOLS = 8)
├── prompts/
│   └── system_prompt.md  ← modified (Section 9 transport rules added)
└── tests/
    └── test_mcp_tools.py ← modified (TestBookTransport added)
```

---

## Tests to write first

### Server — add to `server/tests/test_bookings.py`
```python
class TestCreateTransportBooking:

    def test_creates_booking_with_valid_data(self, client, seeded_transport):
        """TB-17: valid transport booking request returns 201 with booking record."""

    def test_decrements_capacity_on_booking(self, client, seeded_transport):
        """TB-17: capacity on the transport is decremented after booking."""

    def test_returns_booking_reference(self, client, seeded_transport):
        """TB-17: response includes a booking_reference in TB-YYYYMMDD-XXXX format."""

    def test_returns_404_for_unknown_transport(self, client):
        """TB-17: booking with non-existent transport_id returns 404."""

    def test_returns_422_when_capacity_exceeded(self, client, full_transport):
        """TB-17: booking when capacity == 0 returns 422."""

    def test_422_message_includes_capacity_counts(self, client, full_transport):
        """TB-17: 422 detail message includes requested and available capacity."""

    def test_status_is_confirmed_on_creation(self, client, seeded_transport):
        """TB-17: newly created booking has status confirmed."""

    def test_passengers_defaults_to_one(self, client, seeded_transport):
        """TB-17: passengers defaults to 1 when not provided."""

    def test_booking_multiple_passengers(self, client, seeded_transport):
        """TB-17: booking 3 passengers decrements capacity by 3."""


class TestGetTransportBooking:

    def test_returns_booking_by_id(self, client, seeded_transport_booking):
        """TB-17: GET /bookings/transport/{id} returns the correct booking."""

    def test_returns_404_for_unknown_booking(self, client):
        """TB-17: unknown booking_id returns 404."""


class TestListTransportBookings:

    def test_returns_all_bookings_without_filter(self, client, seeded_transport_booking):
        """TB-17: GET /bookings/transport returns all bookings."""

    def test_filters_by_email(self, client, seeded_transport_booking):
        """TB-17: email query param filters by contact_email."""

    def test_returns_empty_list_for_unknown_email(self, client):
        """TB-17: unknown email returns empty list not 404."""
```

### Bot — add to `salebot/tests/test_mcp_tools.py`
```python
class TestBookTransport:

    async def test_returns_confirmation_on_success(self, respx_mock):
        """TB-17: successful booking returns formatted confirmation string."""

    async def test_confirmation_contains_booking_reference(self, respx_mock):
        """TB-17: confirmation includes the booking reference."""

    async def test_transport_id_is_required(self):
        """TB-17: missing transport_id returns clear error message."""

    async def test_passenger_name_is_required(self):
        """TB-17: missing passenger_name returns clear error message."""

    async def test_contact_email_is_required(self):
        """TB-17: missing contact_email returns clear error message."""

    async def test_passengers_defaults_to_one(self, respx_mock):
        """TB-17: passengers of 1 is sent when not in input dict."""

    async def test_returns_capacity_error_on_422(self, respx_mock):
        """TB-17: 422 response returns no-capacity message."""

    async def test_returns_not_found_on_404(self, respx_mock):
        """TB-17: 404 response returns transport-not-found message."""

    async def test_returns_unavailable_on_connection_error(self, respx_mock):
        """TB-17: connection error returns booking unavailable message."""

    async def test_tools_list_contains_eight_tools(self):
        """TB-17: TOOLS list contains exactly 8 tools after TB-17."""
```

Add to `conftest.py`:
```python
@pytest.fixture
def mock_transport_booking_response():
    """TB-17: sample TransportBooking response from server."""
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

---

## Acceptance Criteria

### Server
- [ ] `TransportBooking` model exists with all required fields
- [ ] `TransportBookingCreate` schema exists
- [ ] `POST /bookings/transport` creates booking and returns 201
- [ ] `POST /bookings/transport` decrements `transport.capacity` by `passengers`
- [ ] `POST /bookings/transport` returns 404 when `transport_id` not found
- [ ] `POST /bookings/transport` returns 422 when `capacity < passengers`
- [ ] 422 detail includes requested and available capacity counts
- [ ] `booking_reference` matches format `TB-YYYYMMDD-XXXX`
- [ ] `status` defaults to `"confirmed"`
- [ ] `passengers` defaults to `1`
- [ ] `GET /bookings/transport/{id}` returns booking or 404
- [ ] `GET /bookings/transport?email=...` filters by `contact_email`

### Salebot
- [ ] `book_transport_tool` dict exists with valid Anthropic format
- [ ] `transport_id`, `passenger_name`, `contact_email` are required
- [ ] `passengers` is optional, defaults to 1
- [ ] `execute_book_transport(input: dict) -> str` exists with exact signature
- [ ] Each required field missing returns its specific error message
- [ ] Successful booking returns confirmation string with reference
- [ ] 422 returns no-capacity message, 404 returns not-found message
- [ ] Server unreachable returns unavailable message
- [ ] `book_transport_tool` appended to `TOOLS` (now 8 tools total)
- [ ] `execute_tool` routes `"book_transport"` correctly

### System Prompt
- [ ] Section 9 extended with transport booking flow
- [ ] Prompt notes transport is optional and typically last in the booking flow

### Tests
- [ ] All server transport booking tests pass
- [ ] All bot `TestBookTransport` tests pass
- [ ] All previously passing tests still pass (no regression)
- [ ] `uv run ruff check .` passes with no errors

---

## Manual test script

```python
import httpx
base = "http://localhost:8000"

# Test 1: create transport booking
r = httpx.post(f"{base}/bookings/transport", json={
    "transport_id": 1,
    "passenger_name": "John Smith",
    "contact_email": "john@example.com"
})
print("Test 1 status:", r.status_code)   # 201
print("Test 1 ref:", r.json()["booking_reference"])

# Test 2: capacity decremented
r2 = httpx.get(f"{base}/transport/1")
print("Test 2 capacity:", r2.json()["capacity"])  # original - 1

# Test 3: 422 no capacity
r3 = httpx.post(f"{base}/bookings/transport", json={
    "transport_id": 1,
    "passenger_name": "X",
    "contact_email": "x@x.com",
    "passengers": 9999
})
print("Test 3 status:", r3.status_code)  # 422
```

---

## When done
Print: ✅ TB-17 complete
All 4 booking tools are now complete (TB-14 through TB-17).
Run the full test suite: `uv run pytest tests/ -v`
