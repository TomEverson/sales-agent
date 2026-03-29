# TB-02: MCP Server — Search Hotels

## Context
Read rules/base.md before starting.
Read rules/server.md to understand the FastAPI backend you are calling.
Read salebot/mcp_tools.py from TB-01 — you will be adding to this file.

## Dependency
TB-01 must be complete before starting this story.
TOOLS list and execute_tool dispatcher must already exist in mcp_tools.py.

---

## Goal
Add the search_hotels tool to mcp_tools.py so the agent can find
real hotel options from the Travelbase inventory when building a tour package.

---

## File to modify
salebot/mcp_tools.py

---

## What to build

### 1. Tool Definition — search_hotels_tool
Add the tool definition as a Python dict:
```python
{
  "name": "search_hotels",
  "description": """Search for available hotels in the Travelbase inventory.
  Use this tool when the user mentions a destination city or accommodation preferences.
  Always search for hotels before building a tour package.
  Only return hotels where rooms_available > 0.""",
  "input_schema": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "The city to search hotels in e.g. Singapore, Bangkok, Bali"
      },
      "stars": {
        "type": "integer",
        "description": "Minimum star rating 1 to 5. Only include if user specifies a quality preference."
      },
      "max_price": {
        "type": "number",
        "description": "Maximum price per night in USD. Derive from user budget if possible."
      }
    },
    "required": ["city"]
  }
}
```

### 2. Tool Executor — execute_search_hotels
Create an async function: execute_search_hotels(input: dict) -> str

- Extract city, stars, max_price from input dict
- city is required — if missing return "City is required to search for hotels."
- Build query params from non-None values only
- Call GET http://localhost:8000/hotels with params
- Filter out any hotels where rooms_available == 0
- If no results → return "No hotels found in {city} matching the search criteria."
- If server unreachable → return "Hotel search is currently unavailable. Please try again."
- On success → return results as a formatted JSON string

### 3. Update TOOLS list
Append search_hotels_tool to the existing TOOLS list:
```python
TOOLS = [
    search_flights_tool,
    search_hotels_tool,   # ← added in TB-02
]
```

### 4. Update execute_tool dispatcher
Add the hotels route to the existing dispatcher:
```python
async def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "search_flights":
        return await execute_search_flights(tool_input)
    if tool_name == "search_hotels":
        return await execute_search_hotels(tool_input)
    return f"Unknown tool: {tool_name}"
```

---

## File structure after TB-02
```
salebot/
├── mcp_tools.py           ← modified (search_hotels added)
└── tests/
    ├── __init__.py
    ├── conftest.py        ← add mock_hotel_response fixture
    └── test_mcp_tools.py  ← add hotel test class
```

---

## Tests to write first
Add to salebot/tests/test_mcp_tools.py:
```python
class TestExecuteSearchHotels:

    async def test_returns_hotels_for_valid_city(self, respx_mock):
        """TB-02: valid city returns list of hotels from FastAPI"""

    async def test_filters_out_zero_rooms(self, respx_mock):
        """TB-02: hotels with rooms_available == 0 must be excluded per spec"""

    async def test_city_is_required(self):
        """TB-02: missing city returns clear error message per spec"""

    async def test_optional_stars_sent_as_param(self, respx_mock):
        """TB-02: stars param is included in query only when provided"""

    async def test_optional_max_price_sent_as_param(self, respx_mock):
        """TB-02: max_price param is included in query only when provided"""

    async def test_none_params_not_sent(self, respx_mock):
        """TB-02: None values must not be sent as query params per spec"""

    async def test_empty_results_returns_message(self, respx_mock):
        """TB-02: empty list from API returns no hotels found message per spec"""

    async def test_server_unreachable_returns_message(self, respx_mock):
        """TB-02: connection error returns unavailable message per spec"""

    async def test_error_message_includes_city_name(self, respx_mock):
        """TB-02: no results message must include the searched city name"""
```

Add to conftest.py:
```python
@pytest.fixture
def mock_hotel_response():
    """TB-02: shared sample hotel data for tests"""
    return [
        {
            "id": 1,
            "name": "The Singapore Suites",
            "city": "Singapore",
            "stars": 4,
            "price_per_night": 120.0,
            "amenities": "pool,wifi,gym",
            "rooms_available": 5
        },
        {
            "id": 2,
            "name": "Budget Inn Singapore",
            "city": "Singapore",
            "stars": 2,
            "price_per_night": 40.0,
            "amenities": "wifi",
            "rooms_available": 0   # ← should be filtered out
        }
    ]
```

---

## Acceptance Criteria

- [ ] search_hotels_tool dict exists with correct Anthropic tool format
- [ ] city is the only required field in input_schema
- [ ] stars and max_price are optional
- [ ] execute_search_hotels function exists with exact signature: (input: dict) -> str
- [ ] city missing from input returns "City is required to search for hotels."
- [ ] Query params only include non-None values
- [ ] Hotels with rooms_available == 0 are filtered out before returning
- [ ] Empty results return "No hotels found in {city} matching the search criteria."
  with the actual city name interpolated
- [ ] Server unreachable returns "Hotel search is currently unavailable. Please try again."
- [ ] search_hotels_tool is appended to TOOLS list
- [ ] execute_tool dispatcher routes "search_hotels" to execute_search_hotels
- [ ] All tests in TestExecuteSearchHotels pass
- [ ] uv run ruff check . passes with no errors

---

## Manual test
After generating, verify with this script:
```python
import asyncio
from mcp_tools import execute_tool

async def test():
    # Test 1: valid city
    result = await execute_tool("search_hotels", {"city": "Singapore"})
    print("Test 1:", result)

    # Test 2: with stars and max_price
    result = await execute_tool("search_hotels", {
        "city": "Bangkok",
        "stars": 3,
        "max_price": 100.0
    })
    print("Test 2:", result)

    # Test 3: city with no results
    result = await execute_tool("search_hotels", {"city": "Tokyo"})
    print("Test 3:", result)

    # Test 4: missing city
    result = await execute_tool("search_hotels", {})
    print("Test 4:", result)

asyncio.run(test())
```

Expected:
- Test 1: JSON list of hotels in Singapore (rooms_available > 0 only)
- Test 2: JSON list filtered by stars and price
- Test 3: "No hotels found in Tokyo matching the search criteria."
- Test 4: "City is required to search for hotels."

---

## When done
Print: ✅ TB-02 complete
Do not proceed to TB-03 until all acceptance criteria above are checked.
