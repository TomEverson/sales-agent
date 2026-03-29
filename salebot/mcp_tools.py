import json

import httpx
from typing import Any

BASE_URL = "http://localhost:8000"
TIMEOUT = 10.0

# ---------------------------------------------------------------------------
# Tool definitions in Anthropic format
# ---------------------------------------------------------------------------

search_flights_tool = {
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
        "required": ["destination"],
    },
}

search_hotels_tool = {
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
}

search_activities_tool = {
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
}

search_transport_tool = {
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
}

book_flight_tool = {
    "name": "book_flight",
    "description": """Book a flight for the user.
    Call this tool ONLY after:
    1. The user has explicitly confirmed they want to book (e.g. "book it", "yes book this").
    2. You have collected passenger_name and contact_email from the user.
    Never call this tool speculatively. Always confirm details with the user before booking.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "flight_id": {
                "type": "integer",
                "description": "The id of the flight to book, from the search_flights result.",
            },
            "passenger_name": {
                "type": "string",
                "description": "Full name of the passenger as it should appear on the ticket.",
            },
            "contact_email": {
                "type": "string",
                "description": "Email address for the booking confirmation.",
            },
            "seats_booked": {
                "type": "integer",
                "description": "Number of seats to book. Default 1.",
            },
        },
        "required": ["flight_id", "passenger_name", "contact_email"],
    },
}

book_hotel_tool = {
    "name": "book_hotel",
    "description": """Book a hotel room for the user.
    Call this tool ONLY after:
    1. The user has explicitly confirmed they want to book.
    2. You have collected guest_name, contact_email, check_in_date, check_out_date, and nights.
    Never call this tool speculatively.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "hotel_id": {
                "type": "integer",
                "description": "The id of the hotel to book, from the search_hotels result.",
            },
            "guest_name": {
                "type": "string",
                "description": "Full name of the primary guest.",
            },
            "contact_email": {
                "type": "string",
                "description": "Email address for the booking confirmation.",
            },
            "check_in_date": {
                "type": "string",
                "description": "Check-in date in YYYY-MM-DD format.",
            },
            "check_out_date": {
                "type": "string",
                "description": "Check-out date in YYYY-MM-DD format.",
            },
            "nights": {
                "type": "integer",
                "description": "Number of nights.",
            },
            "guests": {
                "type": "integer",
                "description": "Number of guests. Default 1.",
            },
        },
        "required": ["hotel_id", "guest_name", "contact_email", "check_in_date", "check_out_date", "nights"],
    },
}

book_activity_tool = {
    "name": "book_activity",
    "description": """Book an activity for the user.
    Call this tool ONLY after:
    1. The user has explicitly confirmed they want to book.
    2. You have collected participant_name, contact_email, and activity_date.
    Never call this tool speculatively.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "activity_id": {
                "type": "integer",
                "description": "The id of the activity to book, from the search_activities result.",
            },
            "participant_name": {
                "type": "string",
                "description": "Full name of the primary participant.",
            },
            "contact_email": {
                "type": "string",
                "description": "Email address for the booking confirmation.",
            },
            "activity_date": {
                "type": "string",
                "description": "Planned date for the activity in YYYY-MM-DD format.",
            },
            "participants": {
                "type": "integer",
                "description": "Number of participants. Default 1.",
            },
        },
        "required": ["activity_id", "participant_name", "contact_email", "activity_date"],
    },
}

book_transport_tool = {
    "name": "book_transport",
    "description": """Book a transport option for the user.
    Call this tool ONLY after:
    1. The user has explicitly confirmed they want to book.
    2. You have collected passenger_name and contact_email.
    Transport is optional — only book if user requests it. Never call speculatively.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "transport_id": {
                "type": "integer",
                "description": "The id of the transport to book, from the search_transport result.",
            },
            "passenger_name": {
                "type": "string",
                "description": "Full name of the primary passenger.",
            },
            "contact_email": {
                "type": "string",
                "description": "Email address for the booking confirmation.",
            },
            "passengers": {
                "type": "integer",
                "description": "Number of passengers. Default 1.",
            },
        },
        "required": ["transport_id", "passenger_name", "contact_email"],
    },
}

TOOLS: list[dict[str, Any]] = [
    search_flights_tool,
    search_hotels_tool,
    search_activities_tool,
    search_transport_tool,
    book_flight_tool,
    book_hotel_tool,
    book_activity_tool,
    book_transport_tool,
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
# Tool executors — each takes a raw input dict and returns a str
# ---------------------------------------------------------------------------

async def execute_search_flights(input: dict[str, Any]) -> str:
    destination = input.get("destination")
    origin = input.get("origin")
    class_type = input.get("class_type")
    try:
        raw = await _get("/flights", {"origin": origin, "destination": destination, "class_type": class_type})
    except (httpx.ConnectError, httpx.TimeoutException):
        return "Flight search is currently unavailable. Please try again."

    results = [
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
    if not results:
        return "No flights found matching the search criteria."
    return json.dumps(results, ensure_ascii=False)


async def execute_search_hotels(input: dict[str, Any]) -> str:
    city = input.get("city")
    if not city:
        return "City is required to search for hotels."
    stars = input.get("stars")
    max_price = input.get("max_price")
    try:
        raw = await _get("/hotels", {"city": city, "stars": stars, "max_price": max_price})
    except (httpx.ConnectError, httpx.TimeoutException):
        return "Hotel search is currently unavailable. Please try again."

    results = [
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
    if not results:
        return f"No hotels found in {city} matching the search criteria."
    return json.dumps(results, ensure_ascii=False)


async def execute_search_activities(input: dict[str, Any]) -> str:
    city = input.get("city")
    if not city:
        return "City is required to search for activities."
    category = input.get("category")
    try:
        raw = await _get("/activities", {"city": city, "category": category})
    except (httpx.ConnectError, httpx.TimeoutException):
        return "Activity search is currently unavailable. Please try again."

    results = [
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
    if not results:
        return f"No activities found in {city} matching the search criteria."
    return json.dumps(results, ensure_ascii=False)


async def execute_search_transport(input: dict[str, Any]) -> str:
    origin = input.get("origin")
    destination = input.get("destination")
    transport_type = input.get("type")
    # FR-4: origin and destination are both required
    if not origin:
        return "Origin is required to search for transport."
    if not destination:
        return "Destination is required to search for transport."
    try:
        raw = await _get("/transport", {"origin": origin, "destination": destination, "type": transport_type})
    except (httpx.ConnectError, httpx.TimeoutException):
        return "Transport search is currently unavailable. Please try again."

    results = [
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
    if not results:
        return f"No transport found from {origin} to {destination}."
    return json.dumps(results, ensure_ascii=False)


async def execute_book_flight(input: dict) -> str:
    flight_id = input.get("flight_id")
    passenger_name = input.get("passenger_name")
    contact_email = input.get("contact_email")
    seats_booked = input.get("seats_booked", 1)

    if not flight_id:
        return "flight_id is required to book a flight."
    if not passenger_name:
        return "Passenger name is required to book a flight."
    if not contact_email:
        return "Contact email is required to book a flight."

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{BASE_URL}/bookings/flights",
                json={
                    "flight_id": flight_id,
                    "passenger_name": passenger_name,
                    "contact_email": contact_email,
                    "seats_booked": seats_booked,
                },
            )
        if response.status_code == 422:
            return "Sorry, this flight no longer has enough seats available. Please search for another flight."
        if response.status_code == 404:
            return "Flight not found. Please search for flights again."
        response.raise_for_status()
        booking = response.json()
        return (
            f"✅ Booking confirmed!\n"
            f"Reference: {booking['booking_reference']}\n"
            f"Passenger: {booking['passenger_name']}\n"
            f"Email: {booking['contact_email']}\n"
            f"Seats: {booking['seats_booked']}\n"
            f"Status: {booking['status']}"
        )
    except httpx.ConnectError:
        return "Booking is currently unavailable. Please try again."
    except Exception as e:
        return f"Booking failed: {str(e)}"


async def execute_book_hotel(input: dict) -> str:
    hotel_id = input.get("hotel_id")
    guest_name = input.get("guest_name")
    contact_email = input.get("contact_email")
    check_in_date = input.get("check_in_date")
    check_out_date = input.get("check_out_date")
    nights = input.get("nights")
    guests = input.get("guests", 1)

    if not hotel_id:
        return "hotel_id is required to book a hotel."
    if not guest_name:
        return "Guest name is required to book a hotel."
    if not contact_email:
        return "Contact email is required to book a hotel."
    if not check_in_date:
        return "Check-in date is required to book a hotel."
    if not check_out_date:
        return "Check-out date is required to book a hotel."
    if not nights:
        return "Number of nights is required to book a hotel."

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{BASE_URL}/bookings/hotels",
                json={
                    "hotel_id": hotel_id,
                    "guest_name": guest_name,
                    "contact_email": contact_email,
                    "check_in_date": check_in_date,
                    "check_out_date": check_out_date,
                    "nights": nights,
                    "guests": guests,
                },
            )
        if response.status_code == 422:
            return "Sorry, this hotel no longer has enough rooms available. Please search for another hotel."
        if response.status_code == 404:
            return "Hotel not found. Please search for hotels again."
        response.raise_for_status()
        booking = response.json()
        return (
            f"✅ Hotel booking confirmed!\n"
            f"Reference: {booking['booking_reference']}\n"
            f"Guest: {booking['guest_name']}\n"
            f"Check-in: {booking['check_in_date']} → Check-out: {booking['check_out_date']} ({booking['nights']} nights)\n"
            f"Email: {booking['contact_email']}\n"
            f"Status: {booking['status']}"
        )
    except httpx.ConnectError:
        return "Hotel booking is currently unavailable. Please try again."
    except Exception as e:
        return f"Hotel booking failed: {str(e)}"


async def execute_book_activity(input: dict) -> str:
    activity_id = input.get("activity_id")
    participant_name = input.get("participant_name")
    contact_email = input.get("contact_email")
    activity_date = input.get("activity_date")
    participants = input.get("participants", 1)

    if not activity_id:
        return "activity_id is required to book an activity."
    if not participant_name:
        return "Participant name is required to book an activity."
    if not contact_email:
        return "Contact email is required to book an activity."
    if not activity_date:
        return "Activity date is required to book an activity."

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{BASE_URL}/bookings/activities",
                json={
                    "activity_id": activity_id,
                    "participant_name": participant_name,
                    "contact_email": contact_email,
                    "activity_date": activity_date,
                    "participants": participants,
                },
            )
        if response.status_code == 404:
            return "Activity not found. Please search for activities again."
        response.raise_for_status()
        booking = response.json()
        return (
            f"✅ Activity booking confirmed!\n"
            f"Reference: {booking['booking_reference']}\n"
            f"Participant: {booking['participant_name']}\n"
            f"Date: {booking['activity_date']}\n"
            f"Participants: {booking['participants']}\n"
            f"Email: {booking['contact_email']}\n"
            f"Status: {booking['status']}"
        )
    except httpx.ConnectError:
        return "Activity booking is currently unavailable. Please try again."
    except Exception as e:
        return f"Activity booking failed: {str(e)}"


async def execute_book_transport(input: dict) -> str:
    transport_id = input.get("transport_id")
    passenger_name = input.get("passenger_name")
    contact_email = input.get("contact_email")
    passengers = input.get("passengers", 1)

    if not transport_id:
        return "transport_id is required to book transport."
    if not passenger_name:
        return "Passenger name is required to book transport."
    if not contact_email:
        return "Contact email is required to book transport."

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{BASE_URL}/bookings/transport",
                json={
                    "transport_id": transport_id,
                    "passenger_name": passenger_name,
                    "contact_email": contact_email,
                    "passengers": passengers,
                },
            )
        if response.status_code == 422:
            return "Sorry, this transport option no longer has enough capacity. Please search for another option."
        if response.status_code == 404:
            return "Transport not found. Please search for transport again."
        response.raise_for_status()
        booking = response.json()
        return (
            f"✅ Transport booking confirmed!\n"
            f"Reference: {booking['booking_reference']}\n"
            f"Passenger: {booking['passenger_name']}\n"
            f"Passengers: {booking['passengers']}\n"
            f"Email: {booking['contact_email']}\n"
            f"Status: {booking['status']}"
        )
    except httpx.ConnectError:
        return "Transport booking is currently unavailable. Please try again."
    except Exception as e:
        return f"Transport booking failed: {str(e)}"


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

async def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Route a tool call by name to the appropriate async function."""
    if tool_name == "search_flights":
        return await execute_search_flights(tool_input)
    if tool_name == "search_hotels":
        return await execute_search_hotels(tool_input)
    if tool_name == "search_activities":
        return await execute_search_activities(tool_input)
    if tool_name == "search_transport":
        return await execute_search_transport(tool_input)
    if tool_name == "book_flight":
        return await execute_book_flight(tool_input)
    if tool_name == "book_hotel":
        return await execute_book_hotel(tool_input)
    if tool_name == "book_activity":
        return await execute_book_activity(tool_input)
    if tool_name == "book_transport":
        return await execute_book_transport(tool_input)
    return f"Unknown tool: {tool_name}"
