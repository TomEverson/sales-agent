# TB-01: MCP Server — Search Flights

## Context
Read rules/base.md before starting.
Read rules/server.md to understand the FastAPI backend you are calling.

This is the first story. There are no dependencies.

---

## Goal
Create the MCP tools module and implement the first tool: search_flights.
The agent will use this tool to find real flight options from the Travelbase inventory.

---

## File to create
salebot/mcp_tools.py

---

## What to build

### 1. HTTP Client Setup
- Use httpx.AsyncClient for all HTTP calls
- Base URL: http://localhost:8000
- Set a timeout of 10 seconds on all requests
- Create a single reusable async function: _get(endpoint, params) → list
  that handles the request and raises a clear error if the server is unreachable

### 2. Tool Definition — search_flights
Define the tool in Anthropic tool format as a Python dict:

```python
{
  "name": "search_flights",
  "description": """Search for available flights in the Travelbase inventory.
  Use this tool when the user mentions a destination, origin, or travel dates.
  Always search for flights before building a tour package.
  Only return flights where seats_available > 0.""",
  "input_schema": {
    "type": "object",
    "properties": {
      "origin": {
        "type": "string",
        "description": "Departure city e.g. Bangkok, Singapore, Kuala Lumpur"
      },
      "destination": {
        "type": "string",
        "description": "Arrival city e.g. Bangkok, Singapore, Bali"
      },
      "class_type": {
        "type": "string",
        "enum": ["economy", "business", "first"],
        "description": "Cabin class. Default to economy if user does not specify."
      }
    },
    "required": ["destination"]
  }
}
```

### 3. Tool Executor — execute_search_flights
Create an async function: execute_search_flights(input: dict) → str

- Extract origin, destination, class_type from input dict (all optional except destination)
- Build query params from non-None values only
- Call GET http://localhost:8000/flights with params
- Filter out any flights where seats_available == 0
- If no results → return "No flights found matching the search criteria."
- If server unreachable → return "Flight search is currently unavailable. Please try again."
- On success → return results as a formatted JSON string

### 4. Tool Registry
Expose two things at the bottom of mcp_tools.py:

```python
# List of all tool definitions (passed to Claude API)
TOOLS = [
    search_flights_tool,
    # more tools added in TB-02, TB-03, TB-04
]

# Dispatcher (called by agent.py in TB-05)
async def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "search_flights":
        return await execute_search_flights(tool_input)
    return f"Unknown tool: {tool_name}"
```

---

## File structure after TB-01
```
salebot/
└── mcp_tools.py   ← only file created in this story
```

---

## Acceptance Criteria

- [ ] mcp_tools.py is created with no import errors
- [ ] search_flights_tool dict is valid Anthropic tool format
  (has name, description, input_schema with type/properties)
- [ ] destination is the only required field
- [ ] origin and class_type are optional
- [ ] execute_search_flights uses httpx.AsyncClient with 10s timeout
- [ ] Query params only include non-None values
  (do not send ?origin=None to the API)
- [ ] Flights with seats_available == 0 are filtered out before returning
- [ ] Returns a clear string message when no results found
- [ ] Returns a clear string message when FastAPI is unreachable (not a Python exception)
- [ ] TOOLS list exists and contains search_flights_tool
- [ ] execute_tool dispatcher exists and routes "search_flights" correctly
- [ ] Running: python -c "import mcp_tools" completes with no errors

---

## Test it manually
After generating, verify with this script:

```python
import asyncio
from mcp_tools import execute_tool

async def test():
    # Test 1: valid search
    result = await execute_tool("search_flights", {"destination": "Singapore"})
    print("Test 1:", result)

    # Test 2: with all filters
    result = await execute_tool("search_flights", {
        "origin": "Bangkok",
        "destination": "Singapore",
        "class_type": "economy"
    })
    print("Test 2:", result)

    # Test 3: destination with no results
    result = await execute_tool("search_flights", {"destination": "Tokyo"})
    print("Test 3:", result)

asyncio.run(test())
```

Expected:
- Test 1: JSON list of flights to Singapore
- Test 2: JSON list filtered by origin + class
- Test 3: "No flights found matching the search criteria."

---

## When done
Print: ✅ TB-01 complete
Do not proceed to TB-02 until all acceptance criteria above are checked.
