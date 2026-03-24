import httpx
from typing import Any

BASE_URL = "http://localhost:8000"
TIMEOUT = 10.0

# ---------------------------------------------------------------------------
# Tool definitions in Anthropic format
# ---------------------------------------------------------------------------

TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_flights",
        "description": (
            "Search available flights in the Travelbase inventory. "
            "Returns flights matching the given origin and destination. "
            "Optionally filter by class_type (economy, business, first). "
            "Only returns flights with seats available."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "Departure city, e.g. 'Bangkok'",
                },
                "destination": {
                    "type": "string",
                    "description": "Arrival city, e.g. 'Singapore'",
                },
                "class_type": {
                    "type": "string",
                    "enum": ["economy", "business", "first"],
                    "description": "Optional seat class filter.",
                },
            },
            "required": ["origin", "destination"],
        },
    },
    {
        "name": "search_hotels",
        "description": (
            "Search available hotels in the Travelbase inventory for a given city. "
            "Optionally filter by star rating or maximum price per night. "
            "Only returns hotels with rooms available."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Destination city, e.g. 'Bali'",
                },
                "stars": {
                    "type": "integer",
                    "description": "Exact star rating to filter by (1–5).",
                },
                "max_price": {
                    "type": "number",
                    "description": "Maximum price per night in USD.",
                },
            },
            "required": ["city"],
        },
    },
    {
        "name": "search_activities",
        "description": (
            "Search available activities and experiences in a given city. "
            "Optionally filter by category (adventure, culture, food, nature, "
            "wellness, nightlife, water sports)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City to search activities in, e.g. 'Chiang Mai'",
                },
                "category": {
                    "type": "string",
                    "description": "Optional category filter.",
                },
            },
            "required": ["city"],
        },
    },
    {
        "name": "search_transport",
        "description": (
            "Search available local transport options between two locations. "
            "Types include: car, ferry, bus, train, minivan. "
            "Use this for airport transfers or inter-city connections."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "Departure location, e.g. 'Bali Airport'",
                },
                "destination": {
                    "type": "string",
                    "description": "Arrival location, e.g. 'Ubud'",
                },
                "type": {
                    "type": "string",
                    "enum": ["car", "ferry", "bus", "train", "minivan"],
                    "description": "Optional transport type filter.",
                },
            },
            "required": ["origin", "destination"],
        },
    },
]


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _fmt_time(iso: str) -> str:
    """Return a short human-readable time from an ISO datetime string."""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%a %d %b %H:%M")
    except Exception:
        return iso


async def _get(path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    cleaned = {k: v for k, v in params.items() if v is not None}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(f"{BASE_URL}{path}", params=cleaned)
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Tool executors
# ---------------------------------------------------------------------------

async def search_flights(
    origin: str,
    destination: str,
    class_type: str | None = None,
) -> list[dict[str, Any]]:
    raw = await _get("/flights", {"origin": origin, "destination": destination, "class_type": class_type})
    return [
        {
            "id": f["id"],
            "airline": f["airline"],
            "origin": f["origin"],
            "destination": f["destination"],
            "departure_time": _fmt_time(f["departure_time"]),
            "arrival_time": _fmt_time(f["arrival_time"]),
            "price": f["price"],
            "seats_available": f["seats_available"],
            "class_type": f["class_type"],
        }
        for f in raw
        if f["seats_available"] > 0
    ]


async def search_hotels(
    city: str,
    stars: int | None = None,
    max_price: float | None = None,
) -> list[dict[str, Any]]:
    raw = await _get("/hotels", {"city": city, "stars": stars, "max_price": max_price})
    return [
        {
            "id": h["id"],
            "name": h["name"],
            "city": h["city"],
            "stars": h["stars"],
            "price_per_night": h["price_per_night"],
            "amenities": h["amenities"],
            "rooms_available": h["rooms_available"],
        }
        for h in raw
        if h["rooms_available"] > 0
    ]


async def search_activities(
    city: str,
    category: str | None = None,
) -> list[dict[str, Any]]:
    raw = await _get("/activities", {"city": city, "category": category})
    return [
        {
            "id": a["id"],
            "name": a["name"],
            "city": a["city"],
            "category": a["category"],
            "duration_hours": a["duration_hours"],
            "price": a["price"],
            "availability": a["availability"],
        }
        for a in raw
    ]


async def search_transport(
    origin: str,
    destination: str,
    type: str | None = None,
) -> list[dict[str, Any]]:
    raw = await _get("/transport", {"origin": origin, "destination": destination, "type": type})
    return [
        {
            "id": t["id"],
            "type": t["type"],
            "origin": t["origin"],
            "destination": t["destination"],
            "departure_time": _fmt_time(t["departure_time"]),
            "arrival_time": _fmt_time(t["arrival_time"]),
            "price": t["price"],
            "capacity": t["capacity"],
        }
        for t in raw
    ]


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

async def execute_tool(name: str, inputs: dict[str, Any]) -> Any:
    """Route a tool call by name to the appropriate async function."""
    if name == "search_flights":
        return await search_flights(**inputs)
    if name == "search_hotels":
        return await search_hotels(**inputs)
    if name == "search_activities":
        return await search_activities(**inputs)
    if name == "search_transport":
        return await search_transport(**inputs)
    raise ValueError(f"Unknown tool: {name}")
