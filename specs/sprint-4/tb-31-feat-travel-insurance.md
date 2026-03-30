---
ticket: TB-31
type: feat
title: Travel Insurance Add-on for Bookings
sprint: sprint-4
status: done
component: salebot, server
depends_on: TB-14, TB-15, TB-16, TB-17
---

# TB-31: Travel Insurance Add-on for Bookings

## Context

Travel insurance provides peace of mind for travelers — covering trip cancellations, medical emergencies, lost luggage, and flight delays. Offering insurance as an add-on at booking time increases revenue and builds trust with customers.

Read `rules/base.md` before starting.

---

## Goal

Allow users to add travel insurance to their package booking. Insurance should be offered as an optional add-on after the full package summary, before final confirmation.

---

## Files to create / modify

| File | Action |
|------|--------|
| `server/models/insurance.py` | create — Insurance plan model |
| `server/routers/insurance.py` | create — Insurance endpoints |
| `server/routers/bookings.py` | modify — add insurance to flight booking |
| `server/seed_insurance.py` | create — seed insurance plans |
| `salebot/mcp_tools.py` | create — `add_insurance` tool |
| `salebot/prompts/system_prompt.md` | modify — add insurance to booking flow |
| `salebot/prompts/system_prompt_my.md` | modify — add insurance (Burmese) |

---

## What to build

### 1. Insurance Model — `server/models/insurance.py`

```python
from sqlmodel import SQLModel, Field

class InsurancePlan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str                          # e.g., "Basic Coverage", "Premium Protection"
    description: str                   # Coverage details
    price_per_person: float           # Price in USD per person
    coverage_types: str               # Comma-separated: "medical,cancellation,luggage,flight_delay"
    max_trip_value: float             # Maximum trip value covered
    medical_coverage: float          # Medical expense coverage amount
    cancellation_coverage: float      # Trip cancellation coverage amount
    is_active: bool = True
```

### 2. Insurance Router — `server/routers/insurance.py`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/insurance` | List all active insurance plans |
| GET | `/insurance/{id}` | Get specific plan details |

### 3. Seed Insurance Plans

Seed 3 insurance plans:

| Plan | Price | Coverage |
|------|-------|----------|
| Basic | $15/person | Trip cancellation, flight delay |
| Standard | $35/person | + Medical expenses up to $10,000 |
| Premium | $65/person | + Lost luggage, adventure activities |

### 4. MCP Tool — `salebot/mcp_tools.py`

Add `add_insurance` tool:

```python
add_insurance_tool = {
    "name": "add_insurance",
    "description": "Add travel insurance to a booking. Pass plan_id, traveler_name, and contact_email.",
    "input_schema": {
        "type": "object",
        "properties": {
            "plan_id": {"type": "integer", "description": "Insurance plan ID (1=Basic, 2=Standard, 3=Premium)"},
            "traveler_name": {"type": "string", "description": "Name of person being insured"},
            "contact_email": {"type": "string", "description": "Email for insurance documents"},
        },
        "required": ["plan_id", "traveler_name", "contact_email"]
    }
}
```

### 5. System Prompt Update

Add to Section 9 (All-or-Nothing Package Booking Flow):

**After Step 3 (Show full booking summary):**

Add insurance offer before final confirmation:

```
📋 Complete Booking Summary:

[existing package summary]

💰 Insurance (Optional):
   • Basic Coverage — $15/person
     Trip cancellation, flight delay protection
   • Standard Protection — $35/person
     + Medical expenses up to $10,000
   • Premium Coverage — $65/person
     + Lost luggage, adventure activities

Would you like to add insurance? (yes/no, or 1/2/3 for specific plan)

Total: $350 (flights + hotel + activities)
Insurance: $35 (Standard Protection × 1 person)
Grand Total: $385
```

**After Step 5 (Handle success):**

If insurance was added, include insurance confirmation with reference number.

---

## Acceptance Criteria

- [ ] Users can see 3 insurance options during booking summary
- [ ] Users can select insurance plan before final confirmation
- [ ] Insurance cost is added to the grand total
- [ ] Insurance booking is confirmed with reference number
- [ ] Insurance data is seeded for all plans
- [ ] Bot offers insurance in both English and Burmese

---

## Definition of Done

- [ ] All acceptance criteria checked off
- [ ] `uv run pytest tests/ -v` passes
- [ ] `uv run ruff check .` passes
- [ ] Manual test: complete booking → add insurance → see confirmation