# TB-12: Fix Package Builder — Spec-Compliant Dataclass Interface

## Context
Read rules/base.md before starting.
Read specs/sprint-1/tb-07-package-builder.md — this story implements the interface that was specified there but never built.
Read salebot/package_builder.py — current dict-based implementation must be replaced.
Read salebot/agent.py — currently does not call package_builder; this story does not change that.
Read salebot/tests/conftest.py — package fixtures are absent and must be added.

## Dependency
TB-11 must be complete (conftest.py fixtures in place, all TB-04 tests passing).
No other stories depend on the current build_package dict interface —
agent.py and bot.py do not import package_builder, so the rewrite is safe.

---

## Goal
Replace the dict-based package_builder.py with the dataclass-based interface specified in TB-07.
Create test_package_builder.py (test-first).
Add package builder fixtures to conftest.py.

---

## Files to create or modify
- salebot/package_builder.py — full rewrite to spec interface
- salebot/tests/test_package_builder.py — create (test-first)
- salebot/tests/conftest.py — append package fixtures

---

## What to build

### 1. Dataclasses

Define the following dataclasses at the top of package_builder.py:

```python
from dataclasses import dataclass

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

### 2. format_stars(stars: int) -> str

- Return "⭐" * n where n = max(1, min(5, stars))
- format_stars(4) → "⭐⭐⭐⭐"
- format_stars(0) → "⭐"   (minimum 1)
- format_stars(6) → "⭐⭐⭐⭐⭐"  (capped at 5)

### 3. format_price(price: float) -> str

- Return f"${price:.2f}"
- format_price(85.0) → "$85.00"
- format_price(1200.5) → "$1200.50"
- format_price(0) → "$0.00"

### 4. calculate_total(package: TourPackage) -> float

- total = flight.price + (hotel.price_per_night × hotel.nights) + sum(a.price for a in activities)
- Add transport.price if transport is not None, else add 0
- Return round(total, 2)

### 5. format_package(package: TourPackage) -> str

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
  1. {name} — {format_price(price)} ({duration_hours_str}hrs)
  2. {name} — {format_price(price)} ({duration_hours_str}hrs)

🚗 *Transport*
  {origin} → {destination} | {type} | {format_price(price)}

💰 *Total Estimate: {format_price(total)}*
  _(Budget remaining: {format_price(budget - total)})_
```

Formatting rules:
- duration_hours_str: show as integer if whole number (3.0 → "3"), decimal if not (1.5 → "1.5")
- 🚗 block is fully omitted (header and all detail lines) when transport is None
- Budget remaining can be negative: e.g. "_(Budget remaining: $-50.00)_"
- Each section separated by a blank line
- Two spaces of indentation on all detail lines under each header

### 6. format_tweak_invitation() -> str

Return exactly this string (no trailing newline):

```
Would you like to adjust anything? I can:
- 🔄 Find a different flight
- 🏨 Upgrade or downgrade the hotel
- 🎯 Add or swap activities
- 🚗 Add transport if not included

Just tell me what you'd like to change!
```

---

## Tests to write first

Create salebot/tests/test_package_builder.py before writing any implementation:

```python
"""Tests for salebot/package_builder.py — TB-07: Package Builder."""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from package_builder import (
    PackageFlight, PackageHotel, PackageActivity,
    PackageTransport, TourPackage,
    format_stars, format_price, calculate_total,
    format_package, format_tweak_invitation,
)


class TestFormatStars:

    def test_four_stars(self):
        """TB-07: 4 stars returns 4 star emoji per spec."""

    def test_five_stars(self):
        """TB-07: 5 stars returns 5 star emoji per spec."""

    def test_one_star(self):
        """TB-07: 1 star returns 1 star emoji per spec."""

    def test_zero_stars_returns_one(self):
        """TB-07: 0 or below returns minimum 1 star per spec."""

    def test_negative_stars_returns_one(self):
        """TB-07: negative value returns minimum 1 star per spec."""

    def test_six_stars_capped_at_five(self):
        """TB-07: above 5 is capped at 5 stars per spec."""


class TestFormatPrice:

    def test_whole_number(self):
        """TB-07: whole number shows two decimal places per spec."""

    def test_decimal_number(self):
        """TB-07: decimal price is formatted correctly per spec."""

    def test_starts_with_dollar_sign(self):
        """TB-07: price always starts with dollar sign per spec."""

    def test_large_price(self):
        """TB-07: large price formats correctly per spec."""

    def test_zero_price(self):
        """TB-07: zero formats as $0.00 per spec."""


class TestCalculateTotal:

    def test_sums_flight_hotel_activities(self, sample_package_no_transport):
        """TB-07: total includes flight, hotel nights, and all activities per spec."""

    def test_adds_transport_when_present(self, sample_package_with_transport):
        """TB-07: transport price is added when not None per spec."""

    def test_excludes_transport_when_none(self, sample_package_no_transport):
        """TB-07: transport is not counted when None per spec."""

    def test_hotel_multiplied_by_nights(self, sample_package_no_transport):
        """TB-07: hotel cost is price_per_night multiplied by nights per spec."""

    def test_multiple_activities_summed(self, sample_package_no_transport):
        """TB-07: all activity prices are summed per spec."""

    def test_rounds_to_two_decimal_places(self):
        """TB-07: total is rounded to 2 decimal places per spec."""

    def test_zero_activities(self, sample_flight, sample_hotel):
        """TB-07: package with no activities calculates correctly per spec."""


class TestFormatPackage:

    def test_contains_flight_section(self, sample_package_no_transport):
        """TB-07: output contains flight emoji and header per spec."""

    def test_contains_hotel_section(self, sample_package_no_transport):
        """TB-07: output contains hotel emoji and header per spec."""

    def test_contains_activities_section(self, sample_package_no_transport):
        """TB-07: output contains activities emoji and header per spec."""

    def test_transport_section_included_when_present(self, sample_package_with_transport):
        """TB-07: transport section appears when transport is not None per spec."""

    def test_transport_section_omitted_when_none(self, sample_package_no_transport):
        """TB-07: entire transport block omitted when transport is None per spec."""

    def test_contains_total_line(self, sample_package_no_transport):
        """TB-07: output contains total estimate line per spec."""

    def test_contains_budget_remaining_line(self, sample_package_no_transport):
        """TB-07: output contains budget remaining line per spec."""

    def test_budget_remaining_negative_when_over_budget(
        self, sample_flight, sample_hotel, sample_activities
    ):
        """TB-07: budget remaining shown as negative when over budget per spec."""

    def test_activities_are_numbered(self, sample_package_no_transport):
        """TB-07: activities start with 1. 2. numbering per spec."""

    def test_duration_whole_number_no_decimal(self, sample_package_no_transport):
        """TB-07: whole hour duration shows as integer not float per spec."""

    def test_duration_decimal_shown_as_decimal(self, sample_flight, sample_hotel):
        """TB-07: fractional hour duration shows decimal per spec."""

    def test_uses_telegram_bold_for_headers(self, sample_package_no_transport):
        """TB-07: section headers wrapped in asterisks for Telegram bold per spec."""

    def test_budget_remaining_uses_italic(self, sample_package_no_transport):
        """TB-07: budget remaining line wrapped in underscores for Telegram italic per spec."""


class TestFormatTweakInvitation:

    def test_returns_string(self):
        """TB-07: format_tweak_invitation returns a string per spec."""

    def test_contains_flight_option(self):
        """TB-07: tweak invitation mentions flight option per spec."""

    def test_contains_hotel_option(self):
        """TB-07: tweak invitation mentions hotel option per spec."""

    def test_contains_activities_option(self):
        """TB-07: tweak invitation mentions activities option per spec."""

    def test_contains_transport_option(self):
        """TB-07: tweak invitation mentions transport option per spec."""
```

---

## Additions to conftest.py

Append these fixtures to salebot/tests/conftest.py:

```python
@pytest.fixture
def sample_flight():
    """TB-07: sample PackageFlight for formatting tests."""
    from package_builder import PackageFlight
    return PackageFlight(
        origin="Bangkok",
        destination="Singapore",
        airline="AirAsia",
        class_type="economy",
        departure_time="Sat 08:00",
        arrival_time="Sat 09:30",
        price=85.0,
    )


@pytest.fixture
def sample_hotel():
    """TB-07: sample PackageHotel for formatting tests."""
    from package_builder import PackageHotel
    return PackageHotel(
        name="The Singapore Suites",
        stars=4,
        price_per_night=120.0,
        nights=2,
    )


@pytest.fixture
def sample_activities():
    """TB-07: sample list of PackageActivity for formatting tests."""
    from package_builder import PackageActivity
    return [
        PackageActivity(name="Gardens by the Bay Tour", price=25.0, duration_hours=3.0),
        PackageActivity(name="Singapore Food Walk", price=35.0, duration_hours=2.0),
    ]


@pytest.fixture
def sample_transport():
    """TB-07: sample PackageTransport for formatting tests."""
    from package_builder import PackageTransport
    return PackageTransport(
        origin="Singapore Airport",
        destination="Singapore City",
        type="car",
        price=30.0,
    )


@pytest.fixture
def sample_package_with_transport(
    sample_flight, sample_hotel, sample_activities, sample_transport
):
    """TB-07: complete TourPackage with transport for formatting tests."""
    from package_builder import TourPackage
    return TourPackage(
        flight=sample_flight,
        hotel=sample_hotel,
        activities=sample_activities,
        budget=1000.0,
        transport=sample_transport,
    )


@pytest.fixture
def sample_package_no_transport(sample_flight, sample_hotel, sample_activities):
    """TB-07: complete TourPackage without transport for formatting tests."""
    from package_builder import TourPackage
    return TourPackage(
        flight=sample_flight,
        hotel=sample_hotel,
        activities=sample_activities,
        budget=1000.0,
        transport=None,
    )
```

---

## Acceptance Criteria

- [ ] package_builder.py rewritten with no import errors
- [ ] PackageFlight dataclass exists with fields: origin, destination, airline, class_type, departure_time, arrival_time, price
- [ ] PackageHotel dataclass exists with fields: name, stars, price_per_night, nights
- [ ] PackageActivity dataclass exists with fields: name, price, duration_hours
- [ ] PackageTransport dataclass exists with fields: origin, destination, type, price
- [ ] TourPackage dataclass exists with transport defaulting to None
- [ ] format_stars(stars: int) -> str exists; returns minimum "⭐", maximum "⭐⭐⭐⭐⭐"
- [ ] format_price(price: float) -> str exists; always starts with "$", always 2 decimal places
- [ ] calculate_total(package: TourPackage) -> float exists; multiplies hotel by nights; adds transport only when present; rounds to 2dp
- [ ] format_package(package: TourPackage) -> str exists; transport block fully absent when None
- [ ] Activities in format_package are numbered starting from 1
- [ ] Whole-number duration_hours shows without decimal point (3.0 → "3")
- [ ] Fractional duration_hours shows with decimal point (1.5 → "1.5")
- [ ] Section headers use Telegram bold (*header*)
- [ ] Budget remaining line uses Telegram italic (_text_)
- [ ] Budget remaining can be negative and is shown as-is
- [ ] format_tweak_invitation() -> str exists; mentions all 4 tweak options (flight, hotel, activities, transport)
- [ ] test_package_builder.py exists at salebot/tests/test_package_builder.py
- [ ] All 5 test classes present in test_package_builder.py
- [ ] All 28 tests in test_package_builder.py pass
- [ ] Package fixtures appended to conftest.py
- [ ] All previously passing tests across all test files still pass (no regression)
- [ ] uv run ruff check . passes with no errors

---

## Manual test script

```python
from package_builder import (
    PackageFlight, PackageHotel, PackageActivity,
    PackageTransport, TourPackage,
    format_package, format_tweak_invitation,
    format_stars, format_price, calculate_total,
)

# Test 1: stars formatter
print(format_stars(4))   # ⭐⭐⭐⭐
print(format_stars(0))   # ⭐
print(format_stars(6))   # ⭐⭐⭐⭐⭐

# Test 2: price formatter
print(format_price(85.0))     # $85.00
print(format_price(1200.5))   # $1200.50
print(format_price(0))        # $0.00

# Test 3: full package with transport
pkg = TourPackage(
    flight=PackageFlight(
        origin="Bangkok", destination="Singapore",
        airline="AirAsia", class_type="economy",
        departure_time="Sat 08:00", arrival_time="Sat 09:30",
        price=85.0,
    ),
    hotel=PackageHotel(name="The Singapore Suites", stars=4, price_per_night=120.0, nights=2),
    activities=[
        PackageActivity(name="Gardens by the Bay Tour", price=25.0, duration_hours=3.0),
        PackageActivity(name="Singapore Food Walk", price=35.0, duration_hours=2.5),
    ],
    transport=PackageTransport(
        origin="Singapore Airport", destination="Singapore City",
        type="car", price=30.0,
    ),
    budget=1000.0,
)
print("Total:", calculate_total(pkg))   # 415.0
print(format_package(pkg))

# Test 4: without transport (🚗 block must be absent)
pkg_no_t = TourPackage(pkg.flight, pkg.hotel, pkg.activities, 1000.0, transport=None)
output = format_package(pkg_no_t)
assert "🚗" not in output, "Transport block should be absent"
print(format_package(pkg_no_t))

# Test 5: over budget (negative budget remaining)
pkg_ob = TourPackage(pkg.flight, pkg.hotel, pkg.activities, 300.0, transport=pkg.transport)
print(format_package(pkg_ob))

# Test 6: tweak invitation
print(format_tweak_invitation())
```

Expected:
- Test 1: ⭐⭐⭐⭐ / ⭐ / ⭐⭐⭐⭐⭐
- Test 2: $85.00 / $1200.50 / $0.00
- Test 3: full package with 🚗 block, total $415.00, remaining $585.00
- Test 4: same package but 🚗 block completely absent (assert passes)
- Test 5: _(Budget remaining: $-115.00)_
- Test 6: tweak invitation string with all 4 bullet options

---

## When done
Print: ✅ TB-12 complete
Do not proceed to TB-13 until all acceptance criteria above are checked.
