---
ticket: TB-32
type: feat
title: Flight Comparison View
sprint: sprint-4
status: done
component: salebot, server
depends_on: TB-01
---

# TB-32: Flight Comparison View

## Context

Currently when a user searches for flights, the agent returns results one at a time. Users often want to compare multiple options side-by-side — different airlines, prices, times, and layovers — before making a decision.

This feature will enhance flight search results to show a comparison table with all available options, making it easier for users to choose.

Read `rules/base.md` before starting.

---

## Goal

When a user asks about flights, show a comparison table with all available flight options. Include airline, departure/arrival times, duration, price, and seat availability. Allow users to easily compare and select.

---

## Files to modify

| File | Action |
|------|--------|
| `salebot/mcp_tools.py` | modify — enhance flight search response format |
| `salebot/prompts/system_prompt.md` | modify — update how flights are presented |
| `salebot/prompts/system_prompt_my.md` | modify — update flight presentation (Burmese) |

---

## What to build

### Enhanced Flight Search Response

When `search_flights` returns results, format them as a comparison table:

```
✈️ Flights from Bangkok to Singapore

| # | Airline | Departure | Arrival | Duration | Price | Seats |
|---|---------|-----------|---------|----------|-------|-------|
| 1 | Singapore Airlines | 08:00 | 09:30 | 1h 30m | $189 | 42 |
| 2 | AirAsia | 14:00 | 17:15 | 2h 15m | $95 | 80 |
| 3 | Thai Airways | 10:30 | 11:45 | 1h 15m | $75 | 20 |
| 4 | Malaysia Airlines | 07:00 | 08:10 | 1h 10m | $130 | 15 |

💰 Best value: AirAsia ($95) — cheapest direct flight
⏱️ Fastest: Thai Airways (1h 15m)
💺 Most seats: AirAsia (80 seats)

Reply with the number (1-4) to select a flight, or ask for more details.
```

### System Prompt Update

Modify Section 5 (Response Format Rules) for flight presentations:

Add a rule for flight comparison:

```
### Flight Results Presentation
When presenting flight search results:
1. Always show a comparison table with all options
2. Include columns: Airline, Departure, Arrival, Duration, Price, Seats
3. Highlight the best value option (lowest price)
4. Highlight the fastest option (shortest duration)
5. Indicate if seats are limited (< 20)
6. Ask user to select by number or ask for more details

When presenting hotel/activity results:
1. Show comparison list with key details
2. Highlight best value within budget
3. Note any limited availability
```

---

## Additional Features

### Filter by Preference

If user specifies preferences, highlight matching options:
- "Cheapest flight" → highlight lowest price
- "Morning flight" → highlight earliest departure
- "Direct only" → show only non-stop flights

### Class Comparison

If user asks to compare classes, show price difference:
```
Economy: $189 | Business: $450 | First: $750
```

---

## Acceptance Criteria

- [ ] Flight results always show as comparison table
- [ ] Table includes all relevant columns (airline, times, price, seats)
- [ ] Best value and fastest options are highlighted
- [ ] User can select flight by number
- [ ] Response works in both English and Burmese

---

## Definition of Done

- [ ] All acceptance criteria checked off
- [ ] `uv run pytest tests/ -v` passes
- [ ] `uv run ruff check .` passes
- [ ] Manual test: search flights → see comparison table → select by number