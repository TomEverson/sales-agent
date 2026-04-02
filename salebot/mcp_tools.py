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
        "required": [
            "hotel_id",
            "guest_name",
            "contact_email",
            "check_in_date",
            "check_out_date",
            "nights",
        ],
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
        "required": [
            "activity_id",
            "participant_name",
            "contact_email",
            "activity_date",
        ],
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

check_visa_tool = {
    "name": "check_visa",
    "description": (
        "Check visa requirements for traveling to a destination country. "
        "Pass the traveler's passport country as origin_country and destination country."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "origin_country": {
                "type": "string",
                "description": "The traveler's country of citizenship (e.g., Myanmar, Singapore)",
            },
            "destination_country": {
                "type": "string",
                "description": "The destination country to check requirements for (e.g., Japan, Thailand)",
            },
        },
        "required": ["origin_country", "destination_country"],
    },
}

get_weather_tool = {
    "name": "get_weather",
    "description": (
        "Get weather forecast for a destination city. "
        "Pass city name and optionally start_date/end_date (YYYY-MM-DD) to filter the forecast period."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The destination city name (e.g., Bangkok, Tokyo, Singapore)",
            },
            "start_date": {
                "type": "string",
                "description": "Start date of the forecast period in YYYY-MM-DD format (optional)",
            },
            "end_date": {
                "type": "string",
                "description": "End date of the forecast period in YYYY-MM-DD format (optional)",
            },
        },
        "required": ["city"],
    },
}

get_insurance_plans_tool = {
    "name": "get_insurance_plans",
    "description": "Get available travel insurance plans with pricing and coverage details.",
    "input_schema": {
        "type": "object",
        "properties": {},
    },
}

add_insurance_tool = {
    "name": "add_insurance",
    "description": "Add travel insurance to a booking. Pass plan_id (1=Basic, 2=Standard, 3=Premium), traveler_name, and contact_email.",
    "input_schema": {
        "type": "object",
        "properties": {
            "plan_id": {
                "type": "integer",
                "description": "Insurance plan ID (1=Basic $15, 2=Standard $35, 3=Premium $65)",
            },
            "traveler_name": {
                "type": "string",
                "description": "Name of person being insured",
            },
            "contact_email": {
                "type": "string",
                "description": "Email for insurance documents",
            },
        },
        "required": ["plan_id", "traveler_name", "contact_email"],
    },
}

initiate_payment_tool = {
    "name": "initiate_payment",
    "description": (
        "Initiate a payment for a tour package. "
        "Call this AFTER the user has confirmed they want to book the package. "
        "This creates a payment record and returns a booking reference."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "amount": {
                "type": "number",
                "description": "Total amount to pay in USD.",
            },
        },
        "required": ["amount"],
    },
}

confirm_payment_tool = {
    "name": "confirm_payment",
    "description": (
        "Confirm that payment has been received. "
        "Call this AFTER the user sends a payment screenshot/photo. "
        "This marks the payment as paid in the system."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "booking_reference": {
                "type": "string",
                "description": "The booking reference returned from initiate_payment.",
            },
        },
        "required": ["booking_reference"],
    },
}

check_payment_status_tool = {
    "name": "check_payment_status",
    "description": (
        "Check the status of a payment. "
        "Use this to verify if a payment has been confirmed."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "booking_reference": {
                "type": "string",
                "description": "The booking reference returned from initiate_payment.",
            },
        },
        "required": ["booking_reference"],
    },
}

# ---------------------------------------------------------------------------
# Operator Contact Tool
# ---------------------------------------------------------------------------

OPERATOR_CONTACT = """📞 Operator Contact

If you need human assistance, you can reach our support team:

• Phone / WhatsApp: +66 81 234 5678
• Email: support@travelbase.com
• Telegram: @travelbase_support

Our operators are available 24/7 to help with booking issues, payment problems, or any questions the bot cannot resolve.
"""

get_operator_contact_tool = {
    "name": "get_operator_contact",
    "description": "Get contact information for a human operator. Use this when you cannot resolve the user's issue or when the user asks to speak with a human.",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": [],
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
    check_visa_tool,
    get_weather_tool,
    get_insurance_plans_tool,
    add_insurance_tool,
    initiate_payment_tool,
    confirm_payment_tool,
    check_payment_status_tool,
    get_operator_contact_tool,
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
        raw = await _get(
            "/flights",
            {"origin": origin, "destination": destination, "class_type": class_type},
        )
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

    cheapest = min(results, key=lambda x: x["price"])

    def _get_duration(f: dict, raw_f: dict) -> str:
        try:
            from datetime import datetime

            dep_raw = raw[[r["id"] for r in results].index(f["id"])]["departure_time"]
            arr_raw = raw[[r["id"] for r in results].index(f["id"])]["arrival_time"]
            dep = datetime.fromisoformat(dep_raw)
            arr = datetime.fromisoformat(arr_raw)
            delta = arr - dep
            h = delta.seconds // 3600
            m = (delta.seconds % 3600) // 60
            return f"{h}h {m}m"
        except Exception:
            return "N/A"

    parts = [f"**✈️ Flights: {origin or 'Bangkok'} → {destination}**\n"]
    parts.append("| # | Airline | Departure | Arrival | Duration | Price | Seats |")
    parts.append("|---|---------|-----------|---------|----------|-------|-------|")

    raw_map = {r["id"]: r for r in raw}

    for i, flight in enumerate(results, 1):
        seats_indicator = "⚠️" if flight["seats_available"] < 20 else ""
        duration_str = _get_duration(flight, raw_map)
        parts.append(
            f"| {i} | {flight['airline']} | {flight['departure_time']} | "
            f"{flight['arrival_time']} | {duration_str} | ${flight['price']:.0f} | "
            f"{flight['seats_available']} {seats_indicator} |"
        )

    parts.append("")
    parts.append(f"💰 Best value: {cheapest['airline']} (${cheapest['price']:.0f})")

    if len(results) > 1:
        parts.append("Reply with the number (1-4) to select a flight.")

    return "\n".join(parts)


async def execute_search_hotels(input: dict[str, Any]) -> str:
    city = input.get("city")
    if not city:
        return "City is required to search for hotels."
    stars = input.get("stars")
    max_price = input.get("max_price")
    try:
        raw = await _get(
            "/hotels", {"city": city, "stars": stars, "max_price": max_price}
        )
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
        raw = await _get(
            "/transport",
            {"origin": origin, "destination": destination, "type": transport_type},
        )
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


async def execute_check_visa(input: dict) -> str:
    origin = input.get("origin_country")
    destination = input.get("destination_country")

    if not origin:
        return (
            "origin_country (passport country) is required to check visa requirements."
        )
    if not destination:
        return "destination_country is required to check visa requirements."

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(
                f"{BASE_URL}/visa/{origin}/{destination}",
            )
        if resp.status_code == 404:
            return f"Visa information for {origin} citizens traveling to {destination} is not in our database. Please check with the embassy or official immigration website."
        resp.raise_for_status()
        visa = resp.json()

        parts = [f"**Visa Requirements: {origin} → {destination}**"]

        if visa.get("visa_required"):
            parts.append("❌ Visa Required")
        else:
            parts.append("✅ Visa Free")

        if visa.get("visa_on_arrival"):
            parts.append("📝 Visa on Arrival Available")

        if visa.get("visa_eta"):
            parts.append(f"eVisa: {visa['visa_eta']}")

        if visa.get("max_stay_days"):
            parts.append(f"Max Stay: {visa['max_stay_days']} days")

        if visa.get("notes"):
            parts.append(f"Notes: {visa['notes']}")

        return "\n".join(parts)
    except httpx.ConnectError:
        return "Visa lookup is currently unavailable. Please try again."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Visa information for {origin} → {destination} is not available. Please consult the embassy."
        return f"Visa lookup failed: {str(e)}"
    except Exception as e:
        return f"Visa check failed: {str(e)}"


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


async def execute_get_weather(input: dict) -> str:
    city = input.get("city")
    start_date = input.get("start_date")
    end_date = input.get("end_date")

    if not city:
        return "city is required to get weather."

    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(
                f"{BASE_URL}/weather/{city}",
                params=params,
            )
        if resp.status_code == 404:
            return f"Weather data for {city} is not available. Please try another city."
        resp.raise_for_status()
        data = resp.json()

        if not data.get("forecasts"):
            return f"No weather data available for {city} in the specified period."

        condition_icons = {
            "sunny": "☀️",
            "partly_cloudy": "⛅",
            "cloudy": "☁️",
            "rainy": "🌧️",
            "stormy": "⛈️",
            "humid": "💧",
        }

        parts = [f"**Weather Forecast for {city.title()}**\n"]

        for forecast in data["forecasts"][:7]:
            icon = condition_icons.get(forecast["condition"], "🌤️")
            parts.append(
                f"{forecast['date']} | {icon} {forecast['condition'].replace('_', ' ').title()} | "
                f"{forecast['temperature_min']:.0f}°C - {forecast['temperature_max']:.0f}°C | "
                f"💧 {forecast['humidity']}%"
            )

        has_rain = any(f["precipitation_mm"] > 1 for f in data["forecasts"])
        has_high_uv = any(f["uv_index"] > 7 for f in data["forecasts"])

        tips = []
        if has_rain:
            tips.append("🌂 Bring an umbrella or rain jacket")
        if has_high_uv:
            tips.append("☀️ High UV - use sunscreen and a hat")
        tips.append("👕 Light, breathable clothing recommended")

        parts.append("\n**Travel Tips:**")
        for tip in tips:
            parts.append(f"• {tip}")

        return "\n".join(parts)
    except httpx.ConnectError:
        return "Weather service is currently unavailable. Please try again."
    except Exception as e:
        return f"Weather lookup failed: {str(e)}"


async def execute_get_insurance_plans(input: dict) -> str:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{BASE_URL}/insurance")
        resp.raise_for_status()
        plans = resp.json()

        if not plans:
            return "No insurance plans available at this time."

        parts = ["**🛡️ Travel Insurance Options**\n"]

        for plan in plans:
            plan_num = plan["id"]
            name = plan["name"]
            price = plan["price_per_person"]
            desc = plan["description"]

            coverage = plan["coverage_types"].replace(",", ", ")
            medical = plan.get("medical_coverage", 0)
            cancellation = plan.get("cancellation_coverage", 0)

            parts.append(f"**{plan_num}. {name} — ${price}/person**")
            parts.append(f"   {desc}")
            parts.append(f"   Coverage: {coverage}")

            if medical > 0:
                parts.append(f"   Medical: up to ${medical:,.0f}")
            if cancellation > 0:
                parts.append(f"   Cancellation: up to ${cancellation:,.0f}")
            parts.append("")

        parts.append("To add insurance, tell me which plan (1, 2, or 3) and your name.")
        return "\n".join(parts)
    except httpx.ConnectError:
        return "Insurance service is currently unavailable. Please try again."
    except Exception as e:
        return f"Failed to load insurance plans: {str(e)}"


async def execute_add_insurance(input: dict) -> str:
    plan_id = input.get("plan_id")
    traveler_name = input.get("traveler_name")
    contact_email = input.get("contact_email")

    if not plan_id:
        return "plan_id is required to add insurance."
    if not traveler_name:
        return "traveler_name is required to add insurance."
    if not contact_email:
        return "contact_email is required to add insurance."

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(
                f"{BASE_URL}/insurance/book",
                json={
                    "plan_id": plan_id,
                    "traveler_name": traveler_name,
                    "contact_email": contact_email,
                },
            )
        if resp.status_code == 404:
            return "Insurance plan not found. Please check available plans."
        resp.raise_for_status()
        booking = resp.json()

        plan_name = (
            "Basic" if plan_id == 1 else "Standard" if plan_id == 2 else "Premium"
        )

        return (
            f"✅ Travel Insurance added!\n"
            f"Reference: {booking['booking_reference']}\n"
            f"Plan: {plan_name}\n"
            f"Insured: {booking['traveler_name']}\n"
            f"Email: {booking['contact_email']}\n"
            f"Status: {booking['status']}\n\n"
            f"Your insurance documents will be sent to {contact_email}"
        )
    except httpx.ConnectError:
        return "Insurance service is currently unavailable. Please try again."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return "Insurance plan not found."
        return f"Insurance booking failed: {str(e)}"
    except Exception as e:
        return f"Insurance booking failed: {str(e)}"


async def execute_initiate_payment(input: dict) -> str:
    amount = input.get("amount")

    if amount is None:
        return "amount is required to initiate payment."

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(
                f"{BASE_URL}/payments",
                json={"amount": amount},
            )
        resp.raise_for_status()
        payment = resp.json()

        return (
            f"✅ Payment initiated!\n\n"
            f"💳 **Amount: ${amount:.2f}**\n\n"
            f"📱 **Scan to Pay:**\n"
            f"┌─────────────┐\n"
            f"│ QR code would│\n"
            f"│ be displayed │\n"
            f"│    here     │\n"
            f"└─────────────┘\n\n"
            f"🔗 Payment Reference: {payment['booking_reference']}\n\n"
            f"📸 Please send a screenshot of your payment confirmation.\n"
            f"Once I receive the screenshot, I'll confirm your booking."
        )
    except httpx.ConnectError:
        return "Payment service is currently unavailable. Please try again."
    except Exception as e:
        return f"Payment initiation failed: {str(e)}"


async def execute_confirm_payment(input: dict) -> str:
    booking_reference = input.get("booking_reference")

    if not booking_reference:
        return "booking_reference is required to confirm payment."

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.put(
                f"{BASE_URL}/payments/{booking_reference}/confirm",
            )
        if resp.status_code == 404:
            return "Payment not found. Please initiate payment first."
        if resp.status_code == 400:
            return "Payment has already been confirmed."
        resp.raise_for_status()
        payment = resp.json()

        return (
            f"✅ Payment confirmed!\n\n"
            f"Reference: {payment['booking_reference']}\n"
            f"Amount: ${payment['amount']:.2f}\n"
            f"Status: {payment['status']}\n\n"
            f"Now proceeding to create your bookings..."
        )
    except httpx.ConnectError:
        return "Payment service is currently unavailable. Please try again."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return "Payment not found. Please initiate payment first."
        if e.response.status_code == 400:
            return "Payment has already been confirmed."
        return f"Payment confirmation failed: {str(e)}"
    except Exception as e:
        return f"Payment confirmation failed: {str(e)}"


async def execute_check_payment_status(input: dict) -> str:
    booking_reference = input.get("booking_reference")

    if not booking_reference:
        return "booking_reference is required to check payment status."

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{BASE_URL}/payments/{booking_reference}")
        if resp.status_code == 404:
            return "Payment not found."
        resp.raise_for_status()
        payment = resp.json()

        status_emoji = "✅" if payment["status"] == "paid" else "⏳"
        return (
            f"{status_emoji} Payment Status\n\n"
            f"Reference: {payment['booking_reference']}\n"
            f"Amount: ${payment['amount']:.2f}\n"
            f"Status: {payment['status']}"
        )
    except httpx.ConnectError:
        return "Payment service is currently unavailable. Please try again."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return "Payment not found."
        return f"Payment status check failed: {str(e)}"
    except Exception as e:
        return f"Payment status check failed: {str(e)}"


async def execute_get_operator_contact(input: dict) -> str:
    """Return operator contact information for human assistance."""
    return OPERATOR_CONTACT


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
    if tool_name == "check_visa":
        return await execute_check_visa(tool_input)
    if tool_name == "get_weather":
        return await execute_get_weather(tool_input)
    if tool_name == "get_insurance_plans":
        return await execute_get_insurance_plans(tool_input)
    if tool_name == "add_insurance":
        return await execute_add_insurance(tool_input)
    if tool_name == "initiate_payment":
        return await execute_initiate_payment(tool_input)
    if tool_name == "confirm_payment":
        return await execute_confirm_payment(tool_input)
    if tool_name == "check_payment_status":
        return await execute_check_payment_status(tool_input)
    if tool_name == "get_operator_contact":
        return await execute_get_operator_contact(tool_input)
    return f"Unknown tool: {tool_name}"
