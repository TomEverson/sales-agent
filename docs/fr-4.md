# FR-4: MCP Server — Search Transport

## Context
Read rules/base.md before starting.
Read rules/server.md to understand the FastAPI backend you are calling.
Read salebot/mcp_tools.py — you will be adding to this existing file.

## Dependency
FR-1, FR-2, and FR-3 must be complete before starting this story.
TOOLS list and execute_tool dispatcher must already exist in mcp_tools.py
with search_flights_tool, search_hotels_tool, and search_activities_tool present.

---

## Goal
Add the search_transport tool to mcp_tools.py so the agent can find
local transport options from the Travelbase inventory when building a tour package.
This is the final MCP tool — after FR-4, all 4 tools are complete.

---

## File to modify
salebot/mcp_tools.py

---

## What to build

### 1. Tool Definition — search_transport_tool
Add the tool definition as a Python dict:
```python
{
  "name": "search_transport",
  "description": """Search for available transport options in the Travelbase inventory.
  Use this tool when the user needs to get between two locations within a destination.
  Common use case: airport to hotel, or city to city connections.
  Transport is optional in a package — only include if it adds value or the user requests it.
  If no transport is found, the package can still be presented without it.""",
  "input_schema": {
    "type": "object",
    "properties": {
      "origin": {
        "type": "string",
        "description": "Departure location e.g. Singapore Airport, Bangkok, Phuket Town"
      },
      "destination": {
        "type": "string",
        "description": "Arrival location e.g. Singapore City, Hotel, Patong Beach"
      },
      "type": {
        "type": "string",
        "enum": ["car", "ferry", "bus", "train", "minivan"],
        "description": "Transport type. Only include if user specifies a preference."
      }
    },
    "required": ["origin", "destination"]
  }
}
```

### 2. Tool Executor — execute_search_transport
Create an async function: execute_search_transport(input: dict) -> str

- Extract origin, destination, and type from input dict
- Both origin and destination are required
- If origin missing → return "Origin is required to search for transport."
- If destination missing → return "Destination is required to search for transport."
- Build query params from non-None values only
- Call GET http://localhost:8000/transport with params
- Do NOT filter by capacity — return all results and let the agent decide
- If no results → return "No transport found from {origin} to {destination}."
- If server unreachable → return "Transport search is currently unavailable. Please try again."
- On success → return results as a formatted JSON string

### 3. Update TOOLS list
Append search_transport_tool to the existing TOOLS list:
```python
TOOLS = [
    search_flights_tool,
    search_hotels_tool,
    search_activities_tool,
    search_transport_tool,   # ← added in FR-4
]
```

### 4. Update execute_tool dispatcher
Add the transport route to the existing dispatcher:
```python
async def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "search_flights":
        return await execute_search_flights(tool_input)
    if tool_name == "search_hotels":
        return await execute_search_hotels(tool_input)
    if tool_name == "search_activities":
        return await execute_search_activities(tool_input)
    if tool_name == "search_transport":
        return await execute_search_transport(tool_input)
    return f"Unknown tool: {tool_name}"
```

---

## File structure after FR-4
```
salebot/
├── mcp_tools.py           ← modified (search_transport added, all 4 tools complete)
└── tests/
    ├── __init__.py
    ├── conftest.py        ← add mock_transport_response fixture
    └── test_mcp_tools.py  ← add transport test class
```

---

## Tests to write first
Add to salebot/tests/test_mcp_tools.py:
```python
class TestExecuteSearchTransport:

    async def test_returns_transport_for_valid_origin_and_destination(self, respx_mock):
        """FR-4: valid origin and destination returns list of transport from FastAPI"""

    async def test_origin_is_required(self):
        """FR-4: missing origin returns clear error message per spec"""

    async def test_destination_is_required(self):
        """FR-4: missing destination returns clear error message per spec"""

    async def test_both_missing_returns_origin_error_first(self):
        """FR-4: when both are missing, origin error is returned first per spec"""

    async def test_optional_type_sent_as_param(self, respx_mock):
        """FR-4: type param is included in query only when provided"""

    async def test_none_params_not_sent(self, respx_mock):
        """FR-4: None values must not be sent as query params per spec"""

    async def test_empty_results_returns_message(self, respx_mock):
        """FR-4: empty list from API returns no transport found message per spec"""

    async def test_error_message_includes_origin_and_destination(self, respx_mock):
        """FR-4: no results message must include both origin and destination per spec"""

    async def test_server_unreachable_returns_message(self, respx_mock):
        """FR-4: connection error returns unavailable message per spec"""

    async def test_capacity_not_used_for_filtering(self, respx_mock):
        """FR-4: results must not be filtered by capacity per spec"""

    async def test_type_filter_ferry(self, respx_mock):
        """FR-4: type ferry is passed correctly as query param"""

    async def test_type_filter_car(self, respx_mock):
        """FR-4: type car is passed correctly as query param"""


class TestToolsRegistry:

    def test_tools_list_contains_all_four_tools(self):
        """FR-4: TOOLS list must contain exactly 4 tools after FR-4 per spec"""

    def test_tools_list_order(self):
        """FR-4: TOOLS list order must be flights, hotels, activities, transport per spec"""

    def test_all_tool_names_are_correct(self):
        """FR-4: each tool in TOOLS must have the exact name defined in its spec"""

    async def test_dispatcher_routes_all_four_tools(self, respx_mock):
        """FR-4: execute_tool must route all 4 tool names without returning unknown tool"""

    async def test_dispatcher_returns_unknown_for_invalid_tool(self):
        """FR-4: execute_tool returns unknown tool message for unrecognized tool name"""
```

Add to conftest.py:
```python
@pytest.fixture
def mock_transport_response():
    """FR-4: shared sample transport data for tests"""
    return [
        {
            "id": 1,
            "type": "car",
            "origin": "Singapore Airport",
            "destination": "Singapore City",
            "departure_time": "2026-03-28T08:00:00",
            "arrival_time": "2026-03-28T08:45:00",
            "price": 30.0,
            "capacity": 4
        },
        {
            "id": 2,
            "type": "bus",
            "origin": "Singapore Airport",
            "destination": "Singapore City",
            "departure_time": "2026-03-28T09:00:00",
            "arrival_time": "2026-03-28T10:00:00",
            "price": 5.0,
            "capacity": 40
        },
        {
            "id": 3,
            "type": "ferry",
            "origin": "Singapore",
            "destination": "Batam",
            "departure_time": "2026-03-28T10:00:00",
            "arrival_time": "2026-03-28T11:00:00",
            "price": 25.0,
            "capacity": 60
        }
    ]
```

---

## Acceptance Criteria

- [ ] search_transport_tool dict exists with correct Anthropic tool format
- [ ] origin and destination are both required fields in input_schema
- [ ] type is optional and uses enum: car, ferry, bus, train, minivan
- [ ] execute_search_transport function exists with exact signature: (input: dict) -> str
- [ ] origin missing returns "Origin is required to search for transport."
- [ ] destination missing returns "Destination is required to search for transport."
- [ ] When both missing, origin error is returned first
- [ ] Query params only include non-None values
- [ ] Results are NOT filtered by capacity — all results returned
- [ ] Empty results return "No transport found from {origin} to {destination}."
  with actual origin and destination interpolated
- [ ] Server unreachable returns "Transport search is currently unavailable. Please try again."
- [ ] search_transport_tool is appended to TOOLS list (now contains exactly 4 tools)
- [ ] execute_tool dispatcher routes "search_transport" to execute_search_transport
- [ ] execute_tool returns "Unknown tool: {tool_name}" for any unrecognized tool name
- [ ] Existing FR-1, FR-2, FR-3 routes in dispatcher are untouched
- [ ] All tests in TestExecuteSearchTransport pass
- [ ] All tests in TestToolsRegistry pass
- [ ] All previously passing FR-1, FR-2, FR-3 tests still pass (no regression)
- [ ] uv run ruff check . passes with no errors

---

## Manual test
After generating, verify with this script:
```python
import asyncio
from mcp_tools import execute_tool, TOOLS

async def test():
    # Test 1: valid origin and destination
    result = await execute_tool("search_transport", {
        "origin": "Singapore Airport",
        "destination": "Singapore City"
    })
    print("Test 1:", result)

    # Test 2: with type filter
    result = await execute_tool("search_transport", {
        "origin": "Singapore Airport",
        "destination": "Singapore City",
        "type": "car"
    })
    print("Test 2:", result)

    # Test 3: no results
    result = await execute_tool("search_transport", {
        "origin": "Tokyo",
        "destination": "Osaka"
    })
    print("Test 3:", result)

    # Test 4: missing origin
    result = await execute_tool("search_transport", {
        "destination": "Singapore City"
    })
    print("Test 4:", result)

    # Test 5: missing destination
    result = await execute_tool("search_transport", {
        "origin": "Singapore Airport"
    })
    print("Test 5:", result)

    # Test 6: unknown tool
    result = await execute_tool("search_packages", {})
    print("Test 6:", result)

    # Test 7: registry check
    print(f"Test 7: TOOLS count = {len(TOOLS)} (expected 4)")
    print("Tool names:", [t['name'] for t in TOOLS])

    # Test 8: regression — previous tools still work
    r1 = await execute_tool("search_flights", {"destination": "Singapore"})
    r2 = await execute_tool("search_hotels", {"city": "Singapore"})
    r3 = await execute_tool("search_activities", {"city": "Singapore"})
    print("Test 8 (regression flights):", r1[:50])
    print("Test 8 (regression hotels):", r2[:50])
    print("Test 8 (regression activities):", r3[:50])

asyncio.run(test())
```

Expected:
- Test 1: JSON list of transport from Singapore Airport to Singapore City
- Test 2: JSON list filtered by car type
- Test 3: "No transport found from Tokyo to Osaka."
- Test 4: "Origin is required to search for transport."
- Test 5: "Destination is required to search for transport."
- Test 6: "Unknown tool: search_packages"
- Test 7: TOOLS count = 4, names = [search_flights, search_hotels, search_activities, search_transport]
- Test 8: JSON previews from all 3 previous tools (no regression)

---

## When done
Print: ✅ FR-4 complete
All 4 MCP tools are now complete.
Do not proceed to FR-5 until all acceptance criteria above are checked.