# TB-07: Package Builder — Format Tour Package

## Context
Read rules/base.md before starting.
Read salebot/agent.py from TB-05 — package_builder.py will be called
when Claude has selected items and is ready to present a package.
Read rules/bot.md to understand how the output is sent to Telegram.

## Dependency
TB-05 and TB-06 must be complete before starting this story.
This module is standalone — it has no imports from mcp_tools, agent, or memory.

---

## Goal
Create package_builder.py — the formatting layer that takes raw inventory
items selected by the agent and produces a clean, readable Telegram message.
This module is pure formatting — no API calls, no Claude, no HTTP.

---

## File to create
salebot/package_builder.py

---

## What to build

### 1. Data Classes
Define the following dataclasses for structured input:
```python
from dataclasses import dataclass, field

@dataclass
class PackageFlight:
    origin: str
    destination: str
    airline: str
    class_type: str
    departure_time: str
    arrival_time: str
    price: float

@dataclass
class PackageHotel:
    name: str
    stars: int
    price_per_night: float
    nights: int

@dataclass
class PackageActivity:
    name: str
    price: float
    duration_hours: float

@dataclass
class PackageTransport:
    origin: str
    destination: str
    type: str
    price: float

@dataclass
class TourPackage:
    flight: PackageFlight
    hotel: PackageHotel
    activities: list[PackageActivity]
    budget: float
    transport: PackageTransport | None = None
```

### 2. Star Formatter
Create a function: format_stars(stars: int) -> str

- Return a string of ⭐ repeated stars times
- e.g. format_stars(4) → "⭐⭐⭐⭐"
- If stars < 1 → return "⭐"
- If stars > 5 → return "⭐⭐⭐⭐⭐"
- Always returns at least one star, never more than five

### 3. Price Formatter
Create a function: format_price(price: float) -> str

- Return price formatted as USD string
- Always show 2 decimal places
- e.g. format_price(85.0) → "$85.00"
- e.g. format_price(1200.5) → "$1200.50"

### 4. Total Calculator
Create a function: calculate_total(package: TourPackage) -> float

- Sum all costs in the package:
  - flight.price
  - hotel.price_per_night × hotel.nights
  - sum of all activity.price
  - transport.price if transport is not None, else 0
- Return the total as a float
- Round to 2 decimal places

### 5. Main Formatter
Create the main function: format_package(package: TourPackage) -> str

Build and return this exact Telegram markdown format:
```
🗺 *Your Tour Package*

✈️ *Flight*
  {origin} → {destination} | {airline} | {class_type}
  Departure: {departure_time} → Arrival: {arrival_time}
  Price: {format_price(flight.price)}

🏨 *Hotel*
  {name} | {format_stars(stars)}
  Price: {format_price(price_per_night)}/night × {nights} nights = {format_price(price_per_night * nights)}

🎯 *Activities*
  1. {name} — {format_price(price)} ({duration_hours}hrs)
  2. {name} — {format_price(price)} ({duration_hours}hrs)
  ...

🚗 *Transport*
  {origin} → {destination} | {type} | {format_price(price)}

💰 *Total Estimate: {format_price(total)}*
  _(Budget remaining: {format_price(budget - total)})_
```

#### Formatting rules
- Transport section is included only if package.transport is not None
- If transport is None → omit the entire 🚗 block including the header
- Activities are numbered starting from 1
- duration_hours: show as integer if whole number (3.0 → "3"), decimal if not (1.5 → "1.5")
- Budget remaining can be negative — show it as-is with format_price
  e.g. if over budget: "_(Budget remaining: $-50.00)_"
- Use Telegram markdown: *bold* for headers, _italic_ for budget remaining line
- Each section separated by a blank line
- Two spaces of indentation on detail lines under each header

### 6. Tweak Invitation
Create a function: format_tweak_invitation() -> str

Returns this exact string:
```
Would you like to adjust anything? I can:
- 🔄 Find a different flight
- 🏨 Upgrade or downgrade the hotel
- 🎯 Add or swap activities
- 🚗 Add transport if not included

Just tell me what you'd like to change!
```

This is appended by the agent after presenting a package.
It is a separate function so it can be updated independently.

---

## File structure after TB-07
```
salebot/
├── agent.py                    ← unchanged
├── memory.py                   ← unchanged
├── mcp_tools.py                ← unchanged
├── package_builder.py          ← created in this story
├── prompts/
│   └── system_prompt.md        ← unchanged
└── tests/
    ├── __init__.py
    ├── conftest.py             ← add package fixtures
    └── test_package_builder.py ← created in this story
```

---

## Tests to write first
Create salebot/tests/test_package_builder.py:
```python
class TestFormatStars:

    def test_four_stars(self):
        """TB-07: 4 stars returns 4 star emoji per spec"""

    def test_five_stars(self):
        """TB-07: 5 stars returns 5 star emoji per spec"""

    def test_one_star(self):
        """TB-07: 1 star returns 1 star emoji per spec"""

    def test_zero_stars_returns_one(self):
        """TB-07: 0 or below returns minimum 1 star per spec"""

    def test_six_stars_capped_at_five(self):
        """TB-07: above 5 is capped at 5 stars per spec"""


class TestFormatPrice:

    def test_whole_number(self):
        """TB-07: whole number shows two decimal places per spec"""

    def test_decimal_number(self):
        """TB-07: decimal price is formatted correctly per spec"""

    def test_starts_with_dollar_sign(self):
        """TB-07: price always starts with dollar sign per spec"""

    def test_large_price(self):
        """TB-07: large price formats correctly per spec"""

    def test_zero_price(self):
        """TB-07: zero formats as $0.00 per spec"""


class TestCalculateTotal:

    def test_sums_flight_hotel_activities(self):
        """TB-07: total includes flight, hotel nights, and all activities per spec"""

    def test_adds_transport_when_present(self):
        """TB-07: transport price is added when not None per spec"""

    def test_excludes_transport_when_none(self):
        """TB-07: transport is not counted when None per spec"""

    def test_hotel_multiplied_by_nights(self):
        """TB-07: hotel cost is price_per_night multiplied by nights per spec"""

    def test_multiple_activities_summed(self):
        """TB-07: all activity prices are summed per spec"""

    def test_rounds_to_two_decimal_places(self):
        """TB-07: total is rounded to 2 decimal places per spec"""

    def test_zero_activities(self):
        """TB-07: package with no activities calculates correctly per spec"""


class TestFormatPackage:

    def test_contains_flight_section(self):
        """TB-07: output contains flight emoji and header per spec"""

    def test_contains_hotel_section(self):
        """TB-07: output contains hotel emoji and header per spec"""

    def test_contains_activities_section(self):
        """TB-07: output contains activities emoji and header per spec"""

    def test_transport_section_included_when_present(self):
        """TB-07: transport section appears when transport is not None per spec"""

    def test_transport_section_omitted_when_none(self):
        """TB-07: entire transport block omitted when transport is None per spec"""

    def test_contains_total_line(self):
        """TB-07: output contains total estimate line per spec"""

    def test_contains_budget_remaining_line(self):
        """TB-07: output contains budget remaining line per spec"""

    def test_budget_remaining_negative_when_over_budget(self):
        """TB-07: budget remaining shown as negative when over budget per spec"""

    def test_activities_are_numbered(self):
        """TB-07: activities start with 1. 2. 3. numbering per spec"""

    def test_duration_whole_number_no_decimal(self):
        """TB-07: whole hour duration shows as integer not float per spec"""

    def test_duration_decimal_shown_as_decimal(self):
        """TB-07: fractional hour duration shows decimal per spec"""

    def test_uses_telegram_bold_for_headers(self):
        """TB-07: section headers wrapped in asterisks for Telegram bold per spec"""

    def test_budget_remaining_uses_italic(self):
        """TB-07: budget remaining line wrapped in underscores for Telegram italic per spec"""


class TestFormatTweakInvitation:

    def test_returns_string(self):
        """TB-07: format_tweak_invitation returns a string per spec"""

    def test_contains_flight_option(self):
        """TB-07: tweak invitation mentions flight option per spec"""

    def test_contains_hotel_option(self):
        """TB-07: tweak invitation mentions hotel option per spec"""

    def test_contains_activities_option(self):
        """TB-07: tweak invitation mentions activities option per spec"""

    def test_contains_transport_option(self):
        """TB-07: tweak invitation mentions transport option per spec"""
```

Add to conftest.py:
```python
@pytest.fixture
def sample_flight():
    """TB-07: sample PackageFlight for formatting tests"""
    from package_builder import PackageFlight
    return PackageFlight(
        origin="Bangkok",
        destination="Singapore",
        airline="AirAsia",
        class_type="economy",
        departure_time="Sat 08:00",
        arrival_time="Sat 09:30",
        price=85.0
    )

@pytest.fixture
def sample_hotel():
    """TB-07: sample PackageHotel for formatting tests"""
    from package_builder import PackageHotel
    return PackageHotel(
        name="The Singapore Suites",
        stars=4,
        price_per_night=120.0,
        nights=2
    )

@pytest.fixture
def sample_activities():
    """TB-07: sample list of PackageActivity for formatting tests"""
    from package_builder import PackageActivity
    return [
        PackageActivity(name="Gardens by the Bay Tour", price=25.0, duration_hours=3.0),
        PackageActivity(name="Singapore Food Walk", price=35.0, duration_hours=2.0)
    ]

@pytest.fixture
def sample_transport():
    """TB-07: sample PackageTransport for formatting tests"""
    from package_builder import PackageTransport
    return PackageTransport(
        origin="Singapore Airport",
        destination="Singapore City",
        type="car",
        price=30.0
    )

@pytest.fixture
def sample_package_with_transport(sample_flight, sample_hotel, sample_activities, sample_transport):
    """TB-07: complete TourPackage with transport for formatting tests"""
    from package_builder import TourPackage
    return TourPackage(
        flight=sample_flight,
        hotel=sample_hotel,
        activities=sample_activities,
        budget=1000.0,
        transport=sample_transport
    )

@pytest.fixture
def sample_package_no_transport(sample_flight, sample_hotel, sample_activities):
    """TB-07: complete TourPackage without transport for formatting tests"""
    from package_builder import TourPackage
    return TourPackage(
        flight=sample_flight,
        hotel=sample_hotel,
        activities=sample_activities,
        budget=1000.0,
        transport=None
    )
```

---

## Acceptance Criteria

- [ ] package_builder.py is created with no import errors
- [ ] PackageFlight dataclass exists with all required fields
- [ ] PackageHotel dataclass exists with all required fields
- [ ] PackageActivity dataclass exists with all required fields
- [ ] PackageTransport dataclass exists with all required fields
- [ ] TourPackage dataclass exists with transport defaulting to None
- [ ] format_stars(stars) exists with exact signature
- [ ] format_stars returns minimum 1 star for values below 1
- [ ] format_stars caps at 5 stars for values above 5
- [ ] format_price(price) exists with exact signature
- [ ] format_price always returns string starting with "$"
- [ ] format_price always shows exactly 2 decimal places
- [ ] calculate_total(package) exists with exact signature
- [ ] calculate_total multiplies hotel price_per_night by nights
- [ ] calculate_total adds transport only when not None
- [ ] calculate_total rounds to 2 decimal places
- [ ] format_package(package) exists with exact signature
- [ ] Transport block fully omitted when transport is None
- [ ] Transport block included when transport is present
- [ ] Activities numbered from 1
- [ ] Whole hour durations shown without decimal
- [ ] Fractional hour durations shown with decimal
- [ ] Section headers use Telegram bold (asterisks)
- [ ] Budget remaining uses Telegram italic (underscores)
- [ ] Budget remaining shown as negative when over budget
- [ ] format_tweak_invitation() exists with exact signature
- [ ] format_tweak_invitation mentions all 4 tweak options
- [ ] All tests in test_package_builder.py pass
- [ ] All previously passing TB-01 through TB-06 tests still pass (no regression)
- [ ] uv run ruff check . passes with no errors

---

## Manual test
After generating, verify with this script:
```python
from package_builder import (
    PackageFlight, PackageHotel, PackageActivity,
    PackageTransport, TourPackage,
    format_package, format_tweak_invitation,
    format_stars, format_price, calculate_total
)

# Test 1: stars formatter
print("Test 1:", format_stars(4))   # ⭐⭐⭐⭐
print("Test 1:", format_stars(0))   # ⭐
print("Test 1:", format_stars(6))   # ⭐⭐⭐⭐⭐

# Test 2: price formatter
print("Test 2:", format_price(85.0))     # $85.00
print("Test 2:", format_price(1200.5))   # $1200.50
print("Test 2:", format_price(0))        # $0.00

# Test 3: full package with transport
package = TourPackage(
    flight=PackageFlight(
        origin="Bangkok", destination="Singapore",
        airline="AirAsia", class_type="economy",
        departure_time="Sat 08:00", arrival_time="Sat 09:30",
        price=85.0
    ),
    hotel=PackageHotel(
        name="The Singapore Suites", stars=4,
        price_per_night=120.0, nights=2
    ),
    activities=[
        PackageActivity(name="Gardens by the Bay Tour", price=25.0, duration_hours=3.0),
        PackageActivity(name="Singapore Food Walk", price=35.0, duration_hours=2.5)
    ],
    transport=PackageTransport(
        origin="Singapore Airport", destination="Singapore City",
        type="car", price=30.0
    ),
    budget=1000.0
)

print("Test 3 total:", calculate_total(package))  # 415.0
print("Test 3 output:")
print(format_package(package))

# Test 4: package without transport
package_no_transport = TourPackage(
    flight=package.flight,
    hotel=package.hotel,
    activities=package.activities,
    budget=1000.0,
    transport=None
)
print("Test 4 (no transport):")
print(format_package(package_no_transport))

# Test 5: over budget
over_budget = TourPackage(
    flight=package.flight,
    hotel=package.hotel,
    activities=package.activities,
    budget=300.0,
    transport=package.transport
)
print("Test 5 (over budget):")
print(format_package(over_budget))

# Test 6: tweak invitation
print("Test 6:")
print(format_tweak_invitation())
```

Expected:
- Test 1: ⭐⭐⭐⭐ / ⭐ / ⭐⭐⭐⭐⭐
- Test 2: $85.00 / $1200.50 / $0.00
- Test 3: full package output with transport, total $415.00, remaining $585.00
- Test 4: same package but 🚗 block completely absent
- Test 5: budget remaining shows negative e.g. $-115.00
- Test 6: tweak invitation with all 4 bullet options

---

## When done
Print: ✅ TB-07 complete
Do not proceed to TB-08 until all acceptance criteria above are checked.
