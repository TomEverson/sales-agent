# API Endpoints - Detailed Reference

This document provides detailed documentation for all FastAPI endpoints.

## Base URL
```
http://localhost:8000
```

---

## Health Check

### GET /health

Returns the health status of the API.

**Response:**
```json
{
  "status": "ok"
}
```

---

## Flights API

### GET /flights

List all available flights with optional filtering.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| origin | string | No | Filter by departure city (e.g., "Bangkok") |
| destination | string | No | Filter by arrival city (e.g., "Singapore") |
| class_type | string | No | Filter by class: "economy", "business", "first" |

**Response:** Array of Flight objects
```json
[
  {
    "id": 1,
    "origin": "Bangkok",
    "destination": "Singapore",
    "airline": "Singapore Airlines",
    "departure_time": "2026-04-10T08:00:00",
    "arrival_time": "2026-04-10T11:30:00",
    "price": 250.0,
    "seats_available": 45,
    "class_type": "economy"
  }
]
```

### GET /flights/{flight_id}

Get a specific flight by ID.

**Response:** Single Flight object

### POST /flights

Create a new flight.

**Request Body:**
```json
{
  "origin": "Bangkok",
  "destination": "Singapore",
  "airline": "Singapore Airlines",
  "departure_time": "2026-04-10T08:00:00",
  "arrival_time": "2026-04-10T11:30:00",
  "price": 250.0,
  "seats_available": 50,
  "class_type": "economy"
}
```

### PUT /flights/{flight_id}

Update an existing flight.

### DELETE /flights/{flight_id}

Delete a flight.

---

## Hotels API

### GET /hotels

List all available hotels with optional filtering.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| city | string | No | Filter by city (e.g., "Bali") |
| stars | integer | No | Filter by star rating (1-5) |
| max_price | number | No | Maximum price per night |

**Response:** Array of Hotel objects

### GET /hotels/{hotel_id}

Get a specific hotel by ID.

### POST /hotels

Create a new hotel.

### PUT /hotels/{hotel_id}

Update an existing hotel.

### DELETE /hotels/{hotel_id}

Delete a hotel.

---

## Activities API

### GET /activities

List all activities with optional filtering.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| city | string | No | Filter by city |
| category | string | No | Filter by category: "adventure", "culture", "food", "nature", "wellness", "nightlife", "water_sports" |

**Response:** Array of Activity objects

### GET /activities/{activity_id}

Get a specific activity by ID.

### POST /activities

Create a new activity.

### PUT /activities/{activity_id}

Update an existing activity.

### DELETE /activities/{activity_id}

Delete an activity.

---

## Transport API

### GET /transport

List all transport options with optional filtering.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| origin | string | No | Departure location |
| destination | string | No | Arrival location |
| type | string | No | Transport type: "car", "ferry", "bus", "train", "minivan" |

**Response:** Array of Transport objects

### GET /transport/{transport_id}

Get a specific transport option by ID.

### POST /transport

Create a new transport option.

### PUT /transport/{transport_id}

Update an existing transport option.

### DELETE /transport/{transport_id}

Delete a transport option.

---

## Bookings API

### POST /bookings/flights

Create a flight booking.

**Request Body:**
```json
{
  "flight_id": 1,
  "passenger_name": "John Doe",
  "contact_email": "john@example.com",
  "seats_booked": 2
}
```

**Response:**
```json
{
  "id": 1,
  "flight_id": 1,
  "passenger_name": "John Doe",
  "contact_email": "john@example.com",
  "booking_reference": "TB-20260403-ABCD",
  "status": "confirmed",
  "seats_booked": 2,
  "created_at": "2026-04-03T09:30:00"
}
```

### GET /bookings/flights

List all flight bookings. Optional `email` query parameter to filter by email.

### POST /bookings/hotels

Create a hotel booking.

**Request Body:**
```json
{
  "hotel_id": 1,
  "guest_name": "John Doe",
  "contact_email": "john@example.com",
  "check_in_date": "2026-04-10",
  "check_out_date": "2026-04-12",
  "nights": 2,
  "guests": 2
}
```

### GET /bookings/hotels

List all hotel bookings.

### POST /bookings/activities

Create an activity booking.

**Request Body:**
```json
{
  "activity_id": 1,
  "participant_name": "John Doe",
  "contact_email": "john@example.com",
  "activity_date": "2026-04-11",
  "participants": 2
}
```

### GET /bookings/activities

List all activity bookings.

### POST /bookings/transport

Create a transport booking.

**Request Body:**
```json
{
  "transport_id": 1,
  "passenger_name": "John Doe",
  "contact_email": "john@example.com",
  "passengers": 2
}
```

### GET /bookings/transport

List all transport bookings.

### GET /bookings/packages

Get all bookings grouped by package (booking_reference).

**Response:**
```json
[
  {
    "booking_reference": "TB-20260403-ABCD",
    "items": [
      {
        "kind": "flight",
        "id": 1,
        "passenger_name": "John Doe",
        "contact_email": "john@example.com",
        "status": "confirmed",
        "created_at": "2026-04-03T09:30:00",
        "flight_id": 1,
        "seats_booked": 2
      }
    ],
    "total_items": 1,
    "created_at": "2026-04-03T09:30:00"
  }
]
```

### GET /bookings/stats

Get booking statistics.

**Response:**
```json
{
  "total_bookings": 150,
  "unique_users": 45,
  "by_type": {
    "flights": 40,
    "hotels": 35,
    "activities": 50,
    "transport": 25
  }
}
```

---

## Payments API

### POST /payments

Initiate a payment.

**Request Body:**
```json
{
  "amount": 500.00
}
```

**Response:**
```json
{
  "booking_reference": "PAY-ABC123",
  "amount": 500.00,
  "status": "pending",
  "created_at": "2026-04-03T09:30:00"
}
```

### GET /payments/{booking_reference}

Get payment status.

### PUT /payments/{booking_reference}/confirm

Confirm a payment.

---

## Visa API

### GET /visa/{origin_country}/{destination_country}

Check visa requirements.

**Example:** `GET /visa/Myanmar/Singapore`

**Response:**
```json
{
  "origin_country": "Myanmar",
  "destination_country": "Singapore",
  "visa_required": false,
  "visa_on_arrival": false,
  "max_stay_days": 30
}
```

---

## Weather API

### GET /weather/{city}

Get weather forecast for a city.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| start_date | string | No | Start date (YYYY-MM-DD) |
| end_date | string | No | End date (YYYY-MM-DD) |

**Example:** `GET /weather/Bangkok?start_date=2026-04-10&end_date=2026-04-15`

**Response:**
```json
{
  "city": "Bangkok",
  "forecasts": [
    {
      "date": "2026-04-10",
      "condition": "sunny",
      "temperature_min": 28,
      "temperature_max": 35,
      "humidity": 55,
      "precipitation_mm": 0,
      "uv_index": 8
    }
  ]
}
```

---

## Insurance API

### GET /insurance

Get available insurance plans.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Basic Coverage",
    "price_per_person": 15,
    "description": "Trip cancellation and flight delay protection",
    "coverage_types": "trip_cancellation,flight_delay",
    "medical_coverage": 0,
    "cancellation_coverage": 500
  },
  {
    "id": 2,
    "name": "Standard Protection",
    "price_per_person": 35,
    "description": "Medical coverage up to $10,000",
    "coverage_types": "trip_cancellation,flight_delay,medical",
    "medical_coverage": 10000,
    "cancellation_coverage": 1000
  }
]
```

### POST /insurance/book

Book travel insurance.

**Request Body:**
```json
{
  "plan_id": 1,
  "traveler_name": "John Doe",
  "contact_email": "john@example.com"
}
```

---

## Auth API

### POST /auth/login

Admin login.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

### GET /auth/me

Get current authenticated user (requires Bearer token).

**Headers:**
```
Authorization: Bearer <token>
```

---

## Data Models

### Flight
| Field | Type | Description |
|-------|------|-------------|
| id | int | Primary key |
| origin | str | Departure city |
| destination | str | Arrival city |
| airline | str | Airline name |
| departure_time | datetime | Departure time |
| arrival_time | datetime | Arrival time |
| price | float | Price in USD |
| seats_available | int | Available seats |
| class_type | str | economy, business, first |

### Hotel
| Field | Type | Description |
|-------|------|-------------|
| id | int | Primary key |
| name | str | Hotel name |
| city | str | City location |
| stars | int | Star rating (1-5) |
| price_per_night | float | Price per night |
| amenities | str | Comma-separated amenities |
| rooms_available | int | Available rooms |

### Activity
| Field | Type | Description |
|-------|------|-------------|
| id | int | Primary key |
| name | str | Activity name |
| city | str | City location |
| category | str | Category |
| duration_hours | float | Duration in hours |
| price | float | Price in USD |
| availability | int | Available spots |

### Transport
| Field | Type | Description |
|-------|------|-------------|
| id | int | Primary key |
| type | str | car, ferry, bus, train, minivan |
| origin | str | Departure location |
| destination | str | Arrival location |
| departure_time | datetime | Departure time |
| arrival_time | datetime | Arrival time |
| price | float | Price per person |
| capacity | int | Available capacity |