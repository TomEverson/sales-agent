---
ticket: TB-29
type: feat
title: Visa Requirements Information
sprint: sprint-4
status: todo
component: salebot, server
depends_on: none
---

# TB-29: Visa Requirements Information

## Context

When users search for travel packages, they often need to know if they require a visa for their destination. Currently the bot cannot provide this information. Adding visa requirement lookup will help users make informed decisions and build trust.

Read `rules/base.md` before starting.

---

## Goal

Allow the agent to look up and display visa requirements for any destination. Users can ask things like:
- "Do I need a visa for Japan?"
- "Can Myanmar citizens visit Thailand without a visa?"
- "What countries can Singapore passport holders visit without a visa?"

---

## Files to create / modify

| File | Action |
|------|--------|
| `server/routers/visa.py` | create — new FastAPI router with visa info |
| `server/models/visa.py` | create — VisaRequirement model |
| `salebot/mcp_tools.py` | create — `check_visa` tool for Claude |
| `salebot/prompts/system_prompt.md` | modify — add visa lookup instructions |
| `salebot/prompts/system_prompt_my.md` | modify — add visa lookup instructions (Burmese) |

---

## What to build

### 1. Visa Model — `server/models/visa.py`

```python
from sqlmodel import SQLModel, Field

class VisaRequirement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    origin_country: str          # e.g., "Myanmar", "Singapore"
    destination_country: str    # e.g., "Japan", "Thailand"
    visa_required: bool          # True = visa needed, False = visa-free
    visa_on_arrival: bool        # True = can get visa on arrival
    visa_eta: str | None         # e.g., "eVisa available", "URL: https://..."
    max_stay_days: int | None    # e.g., 30, 90, 180
    notes: str | None            # e.g., "Tourist only", "Business requires separate visa"
```

---

### 2. Visa Router — `server/routers/visa.py`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/visa` | List all visa requirements |
| GET | `/visa?origin=Myanmar&destination=Japan` | Get specific requirement |
| POST | `/visa` | Add/update a visa requirement |

**GET `/visa` query params:**
- `origin` — filter by origin country (e.g., "Myanmar")
- `destination` — filter by destination country (e.g., "Japan")

**Response example:**
```json
{
  "origin_country": "Myanmar",
  "destination_country": "Japan",
  "visa_required": true,
  "visa_on_arrival": false,
  "visa_eta": "Apply at: https://www.mofa.go.jp/",
  "max_stay_days": 90,
  "notes": "Tourist visa required. Processing time 5-7 days."
}
```

---

### 3. MCP Tool — `salebot/mcp_tools.py`

Add `check_visa` tool:

```python
check_visa_tool = {
    "name": "check_visa",
    "description": "Check visa requirements for traveling to a destination country. Pass origin_country and destination_country as arguments.",
    "input_schema": {
        "type": "object",
        "properties": {
            "origin_country": {
                "type": "string",
                "description": "The traveler's country of citizenship (e.g., Myanmar, Singapore)"
            },
            "destination_country": {
                "type": "string",
                "description": "The destination country to check visa requirements for (e.g., Japan, Thailand)"
            }
        },
        "required": ["origin_country", "destination_country"]
    }
}

async def execute_check_visa(input: dict) -> str:
    origin = input.get("origin_country")
    destination = input.get("destination_country")
    # Call GET /visa?origin=X&destination=Y
    # Return formatted result
```

---

### 4. System Prompt Update

Add to Section 2 (Information Extraction Rules):

```
5. **Traveler Origin** — the traveler's country of citizenship
   - Used for: visa requirements check, currency, language hints
   - If not mentioned → ask: "What country are you traveling from?"

6. **Passport Country** — the passport the traveler holds
   - If not mentioned → ask: "What is your passport country?"
   - Use for: visa requirement lookup before booking
```

Add new section about visa handling:

```
### Visa Requirements (Section 10)

Before confirming any booking, always check visa requirements for the destination:
1. Ask the user for their passport country if not already known
2. Call check_visa with origin_country and destination_country
3. If visa is required, inform the user before proceeding
4. If visa on arrival is possible, mention the requirements
5. If visa-free, confirm and proceed

Example response:
"[Destination] requires a tourist visa for [Origin] passport holders. You'll need to apply before travel (processing ~5-7 days). Would you like me to proceed with the booking?"

Never book for a destination where the user doesn't have/can't get the required visa.
```

---

### 5. Seed Visa Data — `server/seed.py`

Seed comprehensive visa data covering all countries in the database. Focus on common origin countries:
- Myanmar
- Singapore
- Thailand
- Malaysia
- Indonesia
- Philippines
- Vietnam
- Cambodia
- Laos
- China
- Japan
- South Korea
- USA
- UK
- Australia

Destinations to include:
- All SEA countries
- Japan, Korea, China, Taiwan (newly added)

---

## Acceptance Criteria

- [ ] `GET /visa` returns all visa requirements
- [ ] `GET /visa?origin=X&destination=Y` returns specific requirement
- [ ] Agent can call `check_visa` tool with origin and destination
- [ ] Agent asks for passport country if not provided before booking
- [ ] Agent informs user of visa requirements before booking
- [ ] Visa data is seeded for all countries in the database
- [ ] `uv run ruff check .` passes

---

## Tests to write

- `server/routers/test_visa.py` — test visa endpoints
- `salebot/tests/test_mcp_tools.py` — test check_visa tool

---

## Definition of Done

- [ ] All acceptance criteria checked off
- [ ] `uv run pytest tests/ -v` passes
- [ ] `uv run ruff check .` passes
- [ ] Manual test: ask bot "Do I need a visa for Japan?" → bot responds with requirements