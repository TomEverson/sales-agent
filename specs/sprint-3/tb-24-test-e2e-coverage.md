---
ticket: TB-24
type: test
title: Test Coverage — Full Application E2E Tests
sprint: sprint-3
status: todo
component: server, salebot, client
depends_on: TB-23
---

# TB-24: Test Coverage — Full Application E2E Tests

## Context
This ticket builds on TB-23 to add end-to-end tests covering the full application flow.

## Dependency
TB-23 (unit booking tests) should be complete first.

---

## Goal
Add E2E tests that verify the complete flow across all three components:
1. Server API endpoints (non-booking)
2. Full user journey: search → select → book → confirm

---

## Current Test Coverage

### Existing (220 tests in salebot/)
- test_agent.py - Agent loop, tool execution
- test_bot.py - Telegram bot handlers
- test_mcp_tools.py - Search tools (NOT booking tools yet)
- test_memory.py - Conversation memory
- test_package_builder.py - Tour package formatting
- test_system_prompt.py - System prompt loading

### Missing
- Server booking tests (covered in TB-23)
- Bot booking tool tests (covered in TB-23)
- Server non-booking API tests
- Full E2E flows

---

## Files to create

| File | Action |
|------|--------|
| `server/tests/test_flights.py` | create — flight API tests |
| `server/tests/test_hotels.py` | create — hotel API tests |
| `server/tests/test_activities.py` | create — activity API tests |
| `server/tests/test_transport.py` | create — transport API tests |
| `salebot/tests/test_booking_integration.py` | create — E2E booking flow |

---

## What to build

### 1. Server — Flight API Tests (`server/tests/test_flights.py`)

```python
class TestSearchFlights:
    - test_returns_flights_list
    - test_filters_by_origin
    - test_filters_by_destination
    - test_filters_by_class_type
    - test_excludes_flights_with_zero_seats
    - test_returns_empty_for_no_matches

class TestGetFlight:
    - test_returns_flight_by_id
    - test_returns_404_for_unknown_flight
```

### 2. Server — Hotel API Tests (`server/tests/test_hotels.py`)

```python
class TestSearchHotels:
    - test_returns_hotels_list
    - test_filters_by_city
    - test_filters_by_stars
    - test_filters_by_max_price
    - test_excludes_hotels_with_zero_rooms

class TestGetHotel:
    - test_returns_hotel_by_id
    - test_returns_404_for_unknown_hotel
```

### 3. Server — Activity API Tests (`server/tests/test_activities.py`)

```python
class TestSearchActivities:
    - test_returns_activities_list
    - test_filters_by_city
    - test_filters_by_category

class TestGetActivity:
    - test_returns_activity_by_id
```

### 4. Server — Transport API Tests (`server/tests/test_transport.py`)

```python
class TestSearchTransport:
    - test_returns_transport_list
    - test_filters_by_origin
    - test_filters_by_destination
    - test_filters_by_type

class TestGetTransport:
    - test_returns_transport_by_id
```

### 5. Bot — E2E Booking Flow (`salebot/tests/test_booking_integration.py`)

```python
class TestFullBookingFlow:
    @pytest.mark.asyncio
    async def test_search_then_book_flight_flow(self, respx_mock):
        """TB-24: full flow from search to booking confirmation"""
        
    @pytest.mark.asyncio
    async def test_search_then_book_hotel_flow(self, respx_mock):
        """TB-24: full hotel search → book → confirm"""
        
    @pytest.mark.asyncio
    async def test_handles_booking_failure_gracefully(self, respx_mock):
        """TB-24: handles 422 seat unavailable gracefully"""
```

---

## Acceptance Criteria

### Server API Tests
- [ ] All flight endpoints tested (search, get, filters)
- [ ] All hotel endpoints tested
- [ ] All activity endpoints tested
- [ ] All transport endpoints tested
- [ ] 404 cases handled

### Bot E2E Tests
- [ ] Full search → book → confirm flow works
- [ ] Error handling in full flow
- [ ] No race conditions

### General
- [ ] Total test count: ~100 new tests
- [ ] All tests pass

---

## When done
Print: ✅ TB-24 complete
