---
ticket: TB-15
type: feat
title: Hotel Booking — Reserve a Hotel Room
sprint: sprint-3
status: todo
component: server, salebot
depends_on: TB-14
---

# TB-15: Hotel Booking — Reserve a Hotel Room

## Context
Read `rules/base.md` before starting.
Read `rules/server.md` — adding a new model and router to FastAPI.
Read `rules/bot.md` — adding a new MCP tool to the agent.
Read `server/models/booking.py` from TB-14 — follow the same pattern.
Read `server/routers/bookings.py` from TB-14 — the `generate_booking_reference()` helper already exists there; import and reuse it.
Read `salebot/mcp_tools.py` — you will be adding `book_hotel` to the tool registry.
Read `salebot/prompts/system_prompt.md` — you will be extending Section 9.

## Dependency
TB-14 must be complete before starting this story.
`generate_booking_reference()` must already exist in `server/routers/bookings.py`.

---

## Goal
Allow the user to book a hotel room through the Telegram bot.
After the agent presents a hotel option, the user can confirm they want to book.
The agent collects passenger name, email, check-in/check-out dates, and number of guests,
then calls `book_hotel` which creates a `HotelBooking` record, decrements `rooms_available`
on the hotel, and returns a booking confirmation with a reference number.

---

## Files to create / modify

| File | Action |
|------|--------|
| `server/models/booking.py` | modify — add HotelBooking, HotelBookingCreate |
| `server/routers/bookings.py` | modify — add hotel booking endpoints |
| `salebot/mcp_tools.py` | modify — add book_hotel tool + executor |
| `salebot/prompts/system_prompt.md` | modify — extend Section 9 with hotel booking rules |
| `salebot/tests/test_mcp_tools.py` | modify — add TestBookHotel class |
| `server/tests/test_bookings.py` | modify — add hotel booking test classes |

---

## What to build

### 1. Server — HotelBooking Model
Add to `server/models/booking.py`:

```python
class HotelBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hotel_id: int = Field(foreign_key="hotel.id")
    guest_name: str
    contact_email: str
    check_in_date: str   # ISO date string: YYYY-MM-DD
    check_out_date: str  # ISO date string: YYYY-MM-DD
    nights: int
    guests: int = 1
    booking_reference: str  # format: TB-YYYYMMDD-XXXX
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
```

### 2. Server — Hotel Booking Endpoints
Add to `server/routers/bookings.py` with prefix `/bookings/hotels`:

#### POST `/bookings/hotels` — Create booking
- Look up hotel by `hotel_id` → 404 if not found
- Check `hotel.rooms_available >= guests` → 422 if insufficient:
  ```json
  {"detail": "Not enough rooms available. Requested: 2, Available: 1"}
  ```
- Decrement `hotel.rooms_available` by `guests`
- Generate a `booking_reference` using the existing `generate_booking_reference()`
- Persist and return the `HotelBooking` with status 201

#### GET `/bookings/hotels/{booking_id}` — Get booking
- Return booking by id — 404 if not found

#### GET `/bookings/hotels` — List bookings
- Optional query param: `email`
- Filter by `contact_email` when provided

### 3. MCP Tool — book_hotel tool definition
Add to `salebot/mcp_tools.py`:

```python
book_hotel_tool = {
    "name": "book_hotel",
    "description": """Book a hotel room for the user.
    Call this tool ONLY after:
    1. The user has explicitly confirmed they want to book.
    2. You have collected guest_name, contact_email, check_in_date, check_out_date, and nights.
    Never call this tool speculatively.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "hotel_id": {
                "type": "integer",
                "description": "The id of the hotel to book, from the search_hotels result."
            },
            "guest_name": {
                "type": "string",
                "description": "Full name of the primary guest."
            },
            "contact_email": {
                "type": "string",
                "description": "Email address for the booking confirmation."
            },
            "check_in_date": {
                "type": "string",
                "description": "Check-in date in YYYY-MM-DD format."
            },
            "check_out_date": {
                "type": "string",
                "description": "Check-out date in YYYY-MM-DD format."
            },
            "nights": {
                "type": "integer",
                "description": "Number of nights. Must match the difference between check-in and check-out."
            },
            "guests": {
                "type": "integer",
                "description": "Number of guests. Default 1."
            }
        },
        "required": ["hotel_id", "guest_name", "contact_email", "check_in_date", "check_out_date", "nights"]
    }
}
```

### 4. MCP Tool — execute_book_hotel executor
Add to `salebot/mcp_tools.py`:

```python
async def execute_book_hotel(input: dict) -> str:
```

- Required fields: `hotel_id`, `guest_name`, `contact_email`, `check_in_date`, `check_out_date`, `nights`
- Missing `hotel_id` → `"hotel_id is required to book a hotel."`
- Missing `guest_name` → `"Guest name is required to book a hotel."`
- Missing `contact_email` → `"Contact email is required to book a hotel."`
- Missing `check_in_date` → `"Check-in date is required to book a hotel."`
- Missing `check_out_date` → `"Check-out date is required to book a hotel."`
- Missing `nights` → `"Number of nights is required to book a hotel."`
- Call `POST http://localhost:8000/bookings/hotels`
- On 201 → return formatted confirmation:
  ```
  ✅ Hotel booking confirmed!
  Reference: TB-20260328-B2K9
  Hotel: {hotel name} | {stars}⭐
  Guest: {guest_name}
  Check-in: {check_in_date} → Check-out: {check_out_date} ({nights} nights)
  Email: {contact_email}
  Status: confirmed
  ```
- On 422 → `"Sorry, this hotel no longer has enough rooms available. Please search for another hotel."`
- On 404 → `"Hotel not found. Please search for hotels again."`
- On server unreachable → `"Hotel booking is currently unavailable. Please try again."`

### 5. MCP Tool — update TOOLS and dispatcher
Append `book_hotel_tool` to `TOOLS` (now 6 tools):
```python
TOOLS = [
    search_flights_tool,
    search_hotels_tool,
    search_activities_tool,
    search_transport_tool,
    book_flight_tool,
    book_hotel_tool,        # ← added in TB-15
]
```

Add route in `execute_tool`:
```python
if tool_name == "book_hotel":
    return await execute_book_hotel(tool_input)
```

### 6. System Prompt — extend Section 9
Append to the hotel subsection of Section 9 in `salebot/prompts/system_prompt.md`:

```
### Hotel booking flow
- After presenting a hotel, ask: "Would you like me to book this hotel for you?"
- If yes, collect in order:
  1. Guest name (full name)
  2. Contact email
  3. Check-in date (confirm from travel dates already in conversation if available)
  4. Check-out date / number of nights
- Confirm: "Booking [hotel name] for [guest_name], [check_in] to [check_out] ([N] nights). Shall I go ahead?"
- Only after confirmation → call book_hotel.
- After successful booking → ask if they want to continue booking activities or transport.
```

---

## File structure after TB-15
```
server/
├── models/
│   └── booking.py      ← modified (HotelBooking added)
├── routers/
│   └── bookings.py     ← modified (hotel endpoints added)
└── tests/
    └── test_bookings.py ← modified (hotel test classes added)

salebot/
├── mcp_tools.py         ← modified (book_hotel added, TOOLS = 6)
├── prompts/
│   └── system_prompt.md ← modified (Section 9 hotel rules added)
└── tests/
    └── test_mcp_tools.py ← modified (TestBookHotel added)
```

---

## Tests to write first

### Server — add to `server/tests/test_bookings.py`
```python
class TestCreateHotelBooking:

    def test_creates_booking_with_valid_data(self, client, seeded_hotel):
        """TB-15: valid hotel booking request returns 201 with booking record."""

    def test_decrements_rooms_available_on_booking(self, client, seeded_hotel):
        """TB-15: rooms_available on the hotel is decremented after booking."""

    def test_returns_booking_reference(self, client, seeded_hotel):
        """TB-15: response includes a booking_reference in TB-YYYYMMDD-XXXX format."""

    def test_returns_404_for_unknown_hotel(self, client):
        """TB-15: booking with non-existent hotel_id returns 404."""

    def test_returns_422_when_no_rooms_available(self, client, full_hotel):
        """TB-15: booking when rooms_available == 0 returns 422."""

    def test_422_message_includes_room_counts(self, client, full_hotel):
        """TB-15: 422 detail message includes requested and available room counts."""

    def test_status_is_confirmed_on_creation(self, client, seeded_hotel):
        """TB-15: newly created booking has status confirmed."""

    def test_guests_defaults_to_one(self, client, seeded_hotel):
        """TB-15: guests defaults to 1 when not provided."""

    def test_nights_stored_correctly(self, client, seeded_hotel):
        """TB-15: nights value is stored as provided."""


class TestGetHotelBooking:

    def test_returns_booking_by_id(self, client, seeded_hotel_booking):
        """TB-15: GET /bookings/hotels/{id} returns the correct booking."""

    def test_returns_404_for_unknown_booking(self, client):
        """TB-15: unknown booking_id returns 404."""


class TestListHotelBookings:

    def test_returns_all_bookings_without_filter(self, client, seeded_hotel_booking):
        """TB-15: GET /bookings/hotels returns all bookings."""

    def test_filters_by_email(self, client, seeded_hotel_booking):
        """TB-15: email query param filters by contact_email."""

    def test_returns_empty_list_for_unknown_email(self, client):
        """TB-15: unknown email returns empty list not 404."""
```

### Bot — add to `salebot/tests/test_mcp_tools.py`
```python
class TestBookHotel:

    async def test_returns_confirmation_on_success(self, respx_mock):
        """TB-15: successful booking returns formatted confirmation string."""

    async def test_confirmation_contains_booking_reference(self, respx_mock):
        """TB-15: confirmation includes the booking reference."""

    async def test_hotel_id_is_required(self):
        """TB-15: missing hotel_id returns clear error message."""

    async def test_guest_name_is_required(self):
        """TB-15: missing guest_name returns clear error message."""

    async def test_contact_email_is_required(self):
        """TB-15: missing contact_email returns clear error message."""

    async def test_check_in_date_is_required(self):
        """TB-15: missing check_in_date returns clear error message."""

    async def test_check_out_date_is_required(self):
        """TB-15: missing check_out_date returns clear error message."""

    async def test_nights_is_required(self):
        """TB-15: missing nights returns clear error message."""

    async def test_returns_no_rooms_error_on_422(self, respx_mock):
        """TB-15: 422 response returns no-rooms-available message."""

    async def test_returns_not_found_on_404(self, respx_mock):
        """TB-15: 404 response returns hotel-not-found message."""

    async def test_returns_unavailable_on_connection_error(self, respx_mock):
        """TB-15: connection error returns booking unavailable message."""

    async def test_tools_list_contains_six_tools(self):
        """TB-15: TOOLS list contains exactly 6 tools after TB-15."""
```

Add to `conftest.py`:
```python
@pytest.fixture
def mock_hotel_booking_response():
    """TB-15: sample HotelBooking response from server."""
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
```

---

## Acceptance Criteria

### Server
- [ ] `HotelBooking` model exists with all required fields
- [ ] `HotelBookingCreate` schema exists
- [ ] `POST /bookings/hotels` creates booking and returns 201
- [ ] `POST /bookings/hotels` decrements `hotel.rooms_available` by `guests`
- [ ] `POST /bookings/hotels` returns 404 when `hotel_id` not found
- [ ] `POST /bookings/hotels` returns 422 when `rooms_available < guests`
- [ ] 422 detail includes requested and available room counts
- [ ] `booking_reference` matches format `TB-YYYYMMDD-XXXX`
- [ ] `status` defaults to `"confirmed"`
- [ ] `guests` defaults to `1`
- [ ] `GET /bookings/hotels/{id}` returns booking or 404
- [ ] `GET /bookings/hotels?email=...` filters by `contact_email`

### Salebot
- [ ] `book_hotel_tool` dict exists with valid Anthropic format
- [ ] All 6 required fields present in `input_schema`
- [ ] `execute_book_hotel(input: dict) -> str` exists with exact signature
- [ ] Each required field missing returns its specific error message
- [ ] Successful booking returns confirmation string with reference
- [ ] 422 returns no-rooms message, 404 returns not-found message
- [ ] Server unreachable returns unavailable message
- [ ] `book_hotel_tool` appended to `TOOLS` (now 6 tools total)
- [ ] `execute_tool` routes `"book_hotel"` correctly

### System Prompt
- [ ] Section 9 extended with hotel booking flow
- [ ] Agent collects all required fields before calling `book_hotel`

### Tests
- [ ] All server hotel booking tests pass
- [ ] All bot `TestBookHotel` tests pass
- [ ] All previously passing tests still pass (no regression)
- [ ] `uv run ruff check .` passes with no errors

---

## Manual test script

```python
import httpx
base = "http://localhost:8000"

# Test 1: create hotel booking
r = httpx.post(f"{base}/bookings/hotels", json={
    "hotel_id": 1,
    "guest_name": "John Smith",
    "contact_email": "john@example.com",
    "check_in_date": "2026-03-28",
    "check_out_date": "2026-03-30",
    "nights": 2
})
print("Test 1 status:", r.status_code)   # 201
print("Test 1 ref:", r.json()["booking_reference"])

# Test 2: rooms decremented
r2 = httpx.get(f"{base}/hotels/1")
print("Test 2 rooms_available:", r2.json()["rooms_available"])  # original - 1

# Test 3: 422 no rooms
r3 = httpx.post(f"{base}/bookings/hotels", json={
    "hotel_id": 1, "guest_name": "X", "contact_email": "x@x.com",
    "check_in_date": "2026-03-28", "check_out_date": "2026-03-30", "nights": 2,
    "guests": 9999
})
print("Test 3 status:", r3.status_code)  # 422
```

---

## When done
Print: ✅ TB-15 complete
Do not proceed to TB-16 until all acceptance criteria above are checked.
