# TB-03: MCP Server — Search Activities

## Context
Read rules/base.md before starting.
Read rules/server.md to understand the FastAPI backend you are calling.
Read salebot/mcp_tools.py — you will be adding to this existing file.

## Dependency
TB-01 and TB-02 must be complete before starting this story.
TOOLS list and execute_tool dispatcher must already exist in mcp_tools.py
with search_flights_tool and search_hotels_tool already present.

---

## Goal
Add the search_activities tool to mcp_tools.py so the agent can find
real activities and experiences from the Travelbase inventory
when building a tour package.

---

## File to modify
salebot/mcp_tools.py

---

## What to build

### 1. Tool Definition — search_activities_tool
Add the tool definition as a Python dict:
```python
{
  "name": "search_activities",
  "description": """Search for available activities and experiences in the Travelbase inventory.
  Use this tool when the user mentions a destination city or interests like food, adventure, culture.
  Always search for at least one activity — every tour package must include at least one.
  Search broadly first (city only), then narrow by category if the user has preferences.""",
  "input_schema": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "The city to search activities in e.g. Singapore, Bangkok, Bali"
      },
      "category": {
        "type": "string",
        "enum": ["adventure", "culture", "food", "nature", "wellness", "nightlife", "water sports"],
        "description": "Activity category. Only include if user expresses a specific interest."
      }
    },
    "required": ["city"]
  }
}
```

### 2. Tool Executor — execute_search_activities
Create an async function: execute_search_activities(input: dict) -> str

- Extract city and category from input dict
- city is required — if missing return "City is required to search for activities."
- Build query params from non-None values only
- Call GET http://localhost:8000/activities with params
- Do NOT filter by availability — return all results and let the agent decide
- If no results → return "No activities found in {city} matching the search criteria."
- If server unreachable → return "Activity search is currently unavailable. Please try again."
- On success → return results as a formatted JSON string

### 3. Update TOOLS list
Append search_activities_tool to the existing TOOLS list:
```python
TOOLS = [
    search_flights_tool,
    search_hotels_tool,
    search_activities_tool,   # ← added in TB-03
]
```

### 4. Update execute_tool dispatcher
Add the activities route to the existing dispatcher:
```python
async def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "search_flights":
        return await execute_search_flights(tool_input)
    if tool_name == "search_hotels":
        return await execute_search_hotels(tool_input)
    if tool_name == "search_activities":
        return await execute_search_activities(tool_input)
    return f"Unknown tool: {tool_name}"
```

---

## File structure after TB-03
```
salebot/
├── mcp_tools.py           ← modified (search_activities added)
└── tests/
    ├── __init__.py
    ├── conftest.py        ← add mock_activity_response fixture
    └── test_mcp_tools.py  ← add activity test class
```

---

## Tests to write first
Add to salebot/tests/test_mcp_tools.py:
```python
class TestExecuteSearchActivities:

    async def test_returns_activities_for_valid_city(self, respx_mock):
        """TB-03: valid city returns list of activities from FastAPI"""

    async def test_city_is_required(self):
        """TB-03: missing city returns clear error message per spec"""

    async def test_optional_category_sent_as_param(self, respx_mock):
        """TB-03: category param is included in query only when provided"""

    async def test_none_params_not_sent(self, respx_mock):
        """TB-03: None values must not be sent as query params per spec"""

    async def test_empty_results_returns_message(self, respx_mock):
        """TB-03: empty list from API returns no activities found message per spec"""

    async def test_error_message_includes_city_name(self, respx_mock):
        """TB-03: no results message must include the searched city name"""

    async def test_server_unreachable_returns_message(self, respx_mock):
        """TB-03: connection error returns unavailable message per spec"""

    async def test_all_results_returned_regardless_of_availability(self, respx_mock):
        """TB-03: availability field must not be used to filter results per spec"""

    async def test_category_filter_adventure(self, respx_mock):
        """TB-03: category adventure is passed correctly as query param"""

    async def test_category_filter_food(self, respx_mock):
        """TB-03: category food is passed correctly as query param"""
```

Add to conftest.py:
```python
@pytest.fixture
def mock_activity_response():
    """TB-03: shared sample activity data for tests"""
    return [
        {
            "id": 1,
            "name": "Gardens by the Bay Tour",
            "city": "Singapore",
            "category": "nature",
            "duration_hours": 3.0,
            "price": 25.0,
            "availability": "daily"
        },
        {
            "id": 2,
            "name": "Singapore Food Walk",
            "city": "Singapore",
            "category": "food",
            "duration_hours": 2.0,
            "price": 35.0,
            "availability": "weekends"
        },
        {
            "id": 3,
            "name": "Night Safari",
            "city": "Singapore",
            "category": "adventure",
            "duration_hours": 4.0,
            "price": 55.0,
            "availability": "daily"
        }
    ]
```

---

## Acceptance Criteria

- [ ] search_activities_tool dict exists with correct Anthropic tool format
- [ ] city is the only required field in input_schema
- [ ] category is optional and uses enum: adventure, culture, food, nature,
  wellness, nightlife, water sports
- [ ] execute_search_activities function exists with exact signature: (input: dict) -> str
- [ ] city missing from input returns "City is required to search for activities."
- [ ] Query params only include non-None values
- [ ] Results are NOT filtered by availability — all results returned
- [ ] Empty results return "No activities found in {city} matching the search criteria."
  with the actual city name interpolated
- [ ] Server unreachable returns "Activity search is currently unavailable. Please try again."
- [ ] search_activities_tool is appended to TOOLS list (now contains 3 tools)
- [ ] execute_tool dispatcher routes "search_activities" to execute_search_activities
- [ ] Existing TB-01 and TB-02 routes in dispatcher are untouched
- [ ] All tests in TestExecuteSearchActivities pass
- [ ] All previously passing TB-01 and TB-02 tests still pass (no regression)
- [ ] uv run ruff check . passes with no errors

---

## Manual test
After generating, verify with this script:
```python
import asyncio
from mcp_tools import execute_tool

async def test():
    # Test 1: valid city, no category
    result = await execute_tool("search_activities", {"city": "Singapore"})
    print("Test 1:", result)

    # Test 2: valid city with category
    result = await execute_tool("search_activities", {
        "city": "Bangkok",
        "category": "food"
    })
    print("Test 2:", result)

    # Test 3: city with no results
    result = await execute_tool("search_activities", {"city": "Tokyo"})
    print("Test 3:", result)

    # Test 4: missing city
    result = await execute_tool("search_activities", {})
    print("Test 4:", result)

    # Test 5: regression — flights still work
    result = await execute_tool("search_flights", {"destination": "Singapore"})
    print("Test 5 (regression):", result[:50])

asyncio.run(test())
```

Expected:
- Test 1: JSON list of all activities in Singapore
- Test 2: JSON list filtered by food category in Bangkok
- Test 3: "No activities found in Tokyo matching the search criteria."
- Test 4: "City is required to search for activities."
- Test 5: JSON list of flights (confirms no regression from TB-01)

---

## When done
Print: ✅ TB-03 complete
Do not proceed to TB-04 until all acceptance criteria above are checked.
