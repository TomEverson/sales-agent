"""
Format a selected tour package as a Telegram markdown message.

Usage:
    from package_builder import (
        PackageFlight, PackageHotel, PackageActivity,
        PackageTransport, TourPackage,
        format_package, format_tweak_invitation,
    )
    text = format_package(package)
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def format_stars(stars: int) -> str:
    """Return star emoji string clamped to 1–5."""
    # FR-7: minimum 1, maximum 5
    n = max(1, min(5, stars))
    return "⭐" * n


def format_price(price: float) -> str:
    """Return price formatted as USD with 2 decimal places."""
    # FR-7: always starts with "$", always 2dp
    return f"${price:.2f}"


def calculate_total(package: TourPackage) -> float:
    """Return total cost of the package rounded to 2 decimal places."""
    # FR-7: flight + hotel*nights + sum(activities) + optional transport
    hotel_cost = package.hotel.price_per_night * package.hotel.nights
    activity_cost = sum(a.price for a in package.activities)
    transport_cost = package.transport.price if package.transport is not None else 0.0
    return round(package.flight.price + hotel_cost + activity_cost + transport_cost, 2)


def _duration_str(hours: float) -> str:
    """Return hours as integer string if whole, decimal string if not."""
    # FR-7: 3.0 → "3", 1.5 → "1.5"
    if hours == int(hours):
        return str(int(hours))
    return str(hours)


# ---------------------------------------------------------------------------
# Main formatter
# ---------------------------------------------------------------------------


def format_package(package: TourPackage) -> str:
    """Format a TourPackage as a Telegram MarkdownV2-compatible string."""
    lines: list[str] = []

    lines.append("🗺 *Your Tour Package*")
    lines.append("")

    # Flight
    f = package.flight
    lines.append("✈️ *Flight*")
    lines.append(f"  {f.origin} → {f.destination} | {f.airline} | {f.class_type.capitalize()}")
    lines.append(f"  Departure: {f.departure_time} → Arrival: {f.arrival_time}")
    lines.append(f"  Price: {format_price(f.price)}")
    lines.append("")

    # Hotel
    h = package.hotel
    hotel_cost = h.price_per_night * h.nights
    night_word = "nights" if h.nights != 1 else "night"
    lines.append("🏨 *Hotel*")
    lines.append(f"  {h.name} | {format_stars(h.stars)}")
    lines.append(
        f"  Price: {format_price(h.price_per_night)}/night"
        f" × {h.nights} {night_word}"
        f" = {format_price(hotel_cost)}"
    )
    lines.append("")

    # Activities
    lines.append("🎯 *Activities*")
    for i, act in enumerate(package.activities, 1):
        lines.append(
            f"  {i}. {act.name} — {format_price(act.price)} ({_duration_str(act.duration_hours)}hrs)"
        )
    lines.append("")

    # Transport (optional)
    if package.transport is not None:
        t = package.transport
        lines.append("🚗 *Transport*")
        lines.append(
            f"  {t.origin} → {t.destination} | {t.type.capitalize()} | {format_price(t.price)}"
        )
        lines.append("")

    # Totals
    total = calculate_total(package)
    remaining = package.budget - total
    lines.append(f"💰 *Total Estimate: {format_price(total)}*")
    lines.append(f"  _(Budget remaining: {format_price(remaining)})_")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tweak invitation
# ---------------------------------------------------------------------------


def format_tweak_invitation() -> str:
    """Return the standard package tweak invitation string."""
    # FR-7: fixed string, all 4 options
    return (
        "Would you like to adjust anything? I can:\n"
        "- 🔄 Find a different flight\n"
        "- 🏨 Upgrade or downgrade the hotel\n"
        "- 🎯 Add or swap activities\n"
        "- 🚗 Add transport if not included\n"
        "\n"
        "Just tell me what you'd like to change!"
    )
