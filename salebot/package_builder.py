"""
Utility to format a selected tour package as a Telegram markdown message.

Usage (called from agent.py or directly):
    text = build_package(flight, hotel, activities, transport, budget, nights)

All arguments are dicts matching the shapes returned by mcp_tools.py.
activities is a list; transport is optional (None or a dict).
"""

from typing import Any


def _stars(n: int) -> str:
    return "⭐" * n


def build_package(
    flight: dict[str, Any],
    hotel: dict[str, Any],
    activities: list[dict[str, Any]],
    budget: float,
    nights: int,
    transport: dict[str, Any] | None = None,
) -> str:
    lines: list[str] = []

    lines.append("🗺 *Your Tour Package*\n")

    # Flight
    lines.append("✈️ *Flight*")
    lines.append(
        f"  {flight['origin']} → {flight['destination']} | "
        f"{flight['airline']} | {flight['class_type'].capitalize()}"
    )
    lines.append(
        f"  Departure: {flight['departure_time']} → Arrival: {flight['arrival_time']}"
    )
    lines.append(f"  Price: ${flight['price']:.0f}\n")

    # Hotel
    hotel_total = hotel["price_per_night"] * nights
    lines.append("🏨 *Hotel*")
    lines.append(f"  {hotel['name']} | {_stars(hotel['stars'])}")
    lines.append(
        f"  ${hotel['price_per_night']:.0f}/night × {nights} night{'s' if nights != 1 else ''}"
        f" = ${hotel_total:.0f}\n"
    )

    # Activities
    activity_total = sum(a["price"] for a in activities)
    lines.append("🎯 *Activities*")
    for i, act in enumerate(activities, 1):
        lines.append(
            f"  {i}. {act['name']} — ${act['price']:.0f} ({act['duration_hours']:.0f}h)"
        )
    lines.append("")

    # Transport (optional)
    transport_total = 0.0
    if transport:
        transport_total = transport["price"]
        lines.append("🚗 *Transport*")
        lines.append(
            f"  {transport['origin']} → {transport['destination']} | "
            f"{transport['type'].capitalize()} | ${transport_total:.0f}"
        )
        lines.append("")

    # Totals
    total = flight["price"] + hotel_total + activity_total + transport_total
    remaining = budget - total

    lines.append(f"💰 *Total Estimate: ${total:.0f}*")
    if remaining >= 0:
        lines.append(f"  _(Budget remaining: ${remaining:.0f})_")
    else:
        lines.append(f"  _⚠️ Over budget by ${abs(remaining):.0f}_")

    return "\n".join(lines)
