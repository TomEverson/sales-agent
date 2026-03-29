---
ticket: TB-16
type: feat
title: Activity Booking — Book an Activity
sprint: sprint-3
status: todo
component: server, salebot
depends_on: TB-14
---

# TB-16: Activity Booking — Book an Activity

## Context
Read `rules/base.md` before starting.
Read `rules/server.md` — adding a new model and endpoints to FastAPI.
Read `server/models/booking.py` from TB-14 — follow the same pattern.
Read `server/routers/bookings.py` — reuse `generate_booking_reference()`.
Read `salebot/mcp_tools.py` — adding `book_activity` to the tool registry.
Read `salebot/prompts/system_prompt.md` — extending Section 9.

## Dependency
TB-14 must be complete.
`generate_booking_reference()` must already exist in `server/routers/bookings.py`.

---

## Goal
Allow the user to book an activity directly through the Telegram bot.

**Important difference from flights and hotels:** The `Activity` model has no capacity
or availability count field — activities are assumed to be always bookable as long as
they exist in inventory. `ActivityBooking` simply records the booking; no inventory
field is decremented.

---

## Files to create / modify

| File | Action |
|------|--------|
| `server/models/booking.py` | modify — add ActivityBooking, ActivityBookingCreate |
| `server/routers/bookings.py` | modify — add activity booking endpoints |
| `salebot/mcp_tools.py` | modify — add book_activity tool + executor |
| `salebot/prompts/system_prompt.md` | modify — extend Section 9 with activity rules |
| `salebot/tests/test_mcp_tools.py` | modify — add TestBookActivity class |
| `server/tests/test_bookings.py` | modify — add activity booking test classes |

---

## What to build

### 1. Server — ActivityBooking Model
Add to `server/models/booking.py`:

```python
class ActivityBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="activity.id")
    participant_name: str
    contact_email: str
    activity_date: str       # ISO date string: YYYY-MM-DD — when they plan to do it
    participants: int = 1
    booking_reference: str   # format: TB-YYYYMMDD-XXXX
    status: str = "confirmed"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ActivityBookingCreate(SQLModel):
    activity_id: int
    participant_name: str
    contact_email: str
    activity_date: str
    participants: int = 1
```

### 2. Server — Activity Booking Endpoints
Add to `server/routers/bookings.py` with prefix `/bookings/activities`:

#### POST `/bookings/activities` — Create booking
- Look up activity by `activity_id` → 404 if not found
- No inventory decrement — activities have no capacity field
- Generate `booking_reference` using `generate_booking_reference()`
- Persist and return the `ActivityBooking` with status 201

#### GET `/bookings/activities/{booking_id}` — Get booking
- Return booking by id — 404 if not found

#### GET `/bookings/activities` — List bookings
- Optional query param: `email`
- Filter by `contact_email` when provided

### 3. MCP Tool — book_activity tool definition
Add to `salebot/mcp_tools.py`:

```python
book_activity_tool = {
    "name": "book_activity",
    "description": """Book an activity for the user.
    Call this tool ONLY after:
    1. The user has explicitly confirmed they want to book.
    2. You have collected participant_name, contact_email, and activity_date.
    Never call this tool speculatively.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "activity_id": {
                "type": "integer",
                "description": "The id of the activity to book, from the search_activities result."
            },
            "participant_name": {
                "type": "string",
                "description": "Full name of the primary participant."
            },
            "contact_email": {
                "type": "string",
                "description": "Email address for the booking confirmation."
            },
            "activity_date": {
                "type": "string",
                "description": "Planned date for the activity in YYYY-MM-DD format."
            },
            "participants": {
                "type": "integer",
                "description": "Number of participants. Default 1."
            }
        },
        "required": ["activity_id", "participant_name", "contact_email", "activity_date"]
    }
}
```

### 4. MCP Tool — execute_book_activity executor
Add to `salebot/mcp_tools.py`:

```python
async def execute_book_activity(input: dict) -> str:
```

- Required: `activity_id`, `participant_name`, `contact_email`, `activity_date`
- Missing `activity_id` → `"activity_id is required to book an activity."`
- Missing `participant_name` → `"Participant name is required to book an activity."`
- Missing `contact_email` → `"Contact email is required to book an activity."`
- Missing `activity_date` → `"Activity date is required to book an activity."`
- Call `POST http://localhost:8000/bookings/activities`
- On 201 → return formatted confirmation:
  ```
  ✅ Activity booking confirmed!
  Reference: TB-20260328-C5T1
  Activity: {activity name}
  Participant: {participant_name}
  Date: {activity_date}
  Participants: {participants}
  Email: {contact_email}
  Status: confirmed
  ```
- On 404 → `"Activity not found. Please search for activities again."`
- On server unreachable → `"Activity booking is currently unavailable. Please try again."`

Note: No 422 case — activities have no capacity to exhaust.

### 5. MCP Tool — update TOOLS and dispatcher
Append `book_activity_tool` to `TOOLS` (now 7 tools):
```python
TOOLS = [
    search_flights_tool,
    search_hotels_tool,
    search_activities_tool,
    search_transport_tool,
    book_flight_tool,
    book_hotel_tool,
    book_activity_tool,     # ← added in TB-16
]
```

Add route in `execute_tool`:
```python
if tool_name == "book_activity":
    return await execute_book_activity(tool_input)
```

### 6. System Prompt — extend Section 9
Append to Section 9 in `salebot/prompts/system_prompt.md`:

```
### Activity booking flow
- After presenting activities, ask: "Would you like me to book any of these activities?"
- If yes, collect in order:
  1. Participant name
  2. Contact email (reuse from flight/hotel booking if already collected this session)
  3. Activity date (confirm from travel dates in conversation)
  4. Number of participants (default 1 if not mentioned)
- Confirm: "Booking [activity name] for [participant_name] on [date]. Shall I go ahead?"
- Only after confirmation → call book_activity.
- Activities have no capacity limit — they can always be booked if they exist.
- You can book multiple activities in sequence — call book_activity once per activity.
```

---

## File structure after TB-16
```
server/
├── models/
│   └── booking.py       ← modified (ActivityBooking added)
├── routers/
│   └── bookings.py      ← modified (activity endpoints added)
└── tests/
    └── test_bookings.py ← modified (activity test classes added)

salebot/
├── mcp_tools.py          ← modified (book_activity added, TOOLS = 7)
├── prompts/
│   └── system_prompt.md  ← modified (Section 9 activity rules added)
└── tests/
    └── test_mcp_tools.py ← modified (TestBookActivity added)
```

---

## Tests to write first

### Server — add to `server/tests/test_bookings.py`
```python
class TestCreateActivityBooking:

    def test_creates_booking_with_valid_data(self, client, seeded_activity):
        """TB-16: valid activity booking request returns 201 with booking record."""

    def test_returns_booking_reference(self, client, seeded_activity):
        """TB-16: response includes a booking_reference in TB-YYYYMMDD-XXXX format."""

    def test_returns_404_for_unknown_activity(self, client):
        """TB-16: booking with non-existent activity_id returns 404."""

    def test_status_is_confirmed_on_creation(self, client, seeded_activity):
        """TB-16: newly created booking has status confirmed."""

    def test_participants_defaults_to_one(self, client, seeded_activity):
        """TB-16: participants defaults to 1 when not provided."""

    def test_no_inventory_decrement_occurs(self, client, seeded_activity):
        """TB-16: activity record is unchanged after booking — no capacity field to decrement."""

    def test_multiple_bookings_for_same_activity_allowed(self, client, seeded_activity):
        """TB-16: same activity can be booked multiple times without error."""


class TestGetActivityBooking:

    def test_returns_booking_by_id(self, client, seeded_activity_booking):
        """TB-16: GET /bookings/activities/{id} returns the correct booking."""

    def test_returns_404_for_unknown_booking(self, client):
        """TB-16: unknown booking_id returns 404."""


class TestListActivityBookings:

    def test_returns_all_bookings_without_filter(self, client, seeded_activity_booking):
        """TB-16: GET /bookings/activities returns all bookings."""

    def test_filters_by_email(self, client, seeded_activity_booking):
        """TB-16: email query param filters by contact_email."""
```

### Bot — add to `salebot/tests/test_mcp_tools.py`
```python
class TestBookActivity:

    async def test_returns_confirmation_on_success(self, respx_mock):
        """TB-16: successful booking returns formatted confirmation string."""

    async def test_confirmation_contains_booking_reference(self, respx_mock):
        """TB-16: confirmation includes the booking reference."""

    async def test_activity_id_is_required(self):
        """TB-16: missing activity_id returns clear error message."""

    async def test_participant_name_is_required(self):
        """TB-16: missing participant_name returns clear error message."""

    async def test_contact_email_is_required(self):
        """TB-16: missing contact_email returns clear error message."""

    async def test_activity_date_is_required(self):
        """TB-16: missing activity_date returns clear error message."""

    async def test_returns_not_found_on_404(self, respx_mock):
        """TB-16: 404 response returns activity-not-found message."""

    async def test_returns_unavailable_on_connection_error(self, respx_mock):
        """TB-16: connection error returns booking unavailable message."""

    async def test_no_422_case_exists(self, respx_mock):
        """TB-16: activity booking never returns 422 — no capacity to exhaust."""

    async def test_tools_list_contains_seven_tools(self):
        """TB-16: TOOLS list contains exactly 7 tools after TB-16."""
```

Add to `conftest.py`:
```python
@pytest.fixture
def mock_activity_booking_response():
    """TB-16: sample ActivityBooking response from server."""
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
```

---

## Acceptance Criteria

### Server
- [ ] `ActivityBooking` model exists with all required fields
- [ ] `ActivityBookingCreate` schema exists
- [ ] `POST /bookings/activities` creates booking and returns 201
- [ ] `POST /bookings/activities` does NOT decrement any inventory field
- [ ] `POST /bookings/activities` allows multiple bookings for the same activity
- [ ] `POST /bookings/activities` returns 404 when `activity_id` not found
- [ ] `booking_reference` matches format `TB-YYYYMMDD-XXXX`
- [ ] `status` defaults to `"confirmed"`
- [ ] `participants` defaults to `1`
- [ ] `GET /bookings/activities/{id}` returns booking or 404
- [ ] `GET /bookings/activities?email=...` filters by `contact_email`

### Salebot
- [ ] `book_activity_tool` dict exists with valid Anthropic format
- [ ] `activity_id`, `participant_name`, `contact_email`, `activity_date` are required
- [ ] `execute_book_activity(input: dict) -> str` exists with exact signature
- [ ] Each required field missing returns its specific error message
- [ ] Successful booking returns confirmation string with reference
- [ ] 404 returns not-found message
- [ ] Server unreachable returns unavailable message
- [ ] No 422 handling needed
- [ ] `book_activity_tool` appended to `TOOLS` (now 7 tools total)
- [ ] `execute_tool` routes `"book_activity"` correctly

### System Prompt
- [ ] Section 9 extended with activity booking flow
- [ ] Prompt notes that activities have no capacity limit
- [ ] Prompt instructs agent it can book multiple activities in sequence

### Tests
- [ ] All server activity booking tests pass
- [ ] All bot `TestBookActivity` tests pass
- [ ] All previously passing tests still pass (no regression)
- [ ] `uv run ruff check .` passes with no errors

---

## Manual test script

```python
import httpx
base = "http://localhost:8000"

# Test 1: create activity booking
r = httpx.post(f"{base}/bookings/activities", json={
    "activity_id": 1,
    "participant_name": "John Smith",
    "contact_email": "john@example.com",
    "activity_date": "2026-03-29"
})
print("Test 1 status:", r.status_code)   # 201
print("Test 1 ref:", r.json()["booking_reference"])

# Test 2: book again — should succeed (no capacity limit)
r2 = httpx.post(f"{base}/bookings/activities", json={
    "activity_id": 1,
    "participant_name": "Jane Doe",
    "contact_email": "jane@example.com",
    "activity_date": "2026-03-29"
})
print("Test 2 status:", r2.status_code)  # 201 — no 422

# Test 3: 404 unknown activity
r3 = httpx.post(f"{base}/bookings/activities", json={
    "activity_id": 9999,
    "participant_name": "X",
    "contact_email": "x@x.com",
    "activity_date": "2026-03-29"
})
print("Test 3 status:", r3.status_code)  # 404
```

---

## When done
Print: ✅ TB-16 complete
Do not proceed to TB-17 until all acceptance criteria above are checked.
