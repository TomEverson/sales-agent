# Database Schema Reference

This document provides detailed information about the database models and schema.

---

## Database Configuration

- **Database**: SQLite
- **File**: `travel.db` (located in server directory)
- **ORM**: SQLModel (combines SQLAlchemy + Pydantic)

---

## Entity Relationship Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Flight    │     │ FlightBooking│     │   Payment  │
│             │────▶│              │     │             │
│ id (PK)     │     │ flight_id(FK)◀────│ id (PK)     │
│             │     │ booking_ref  │     │ booking_ref │
└─────────────┘     └──────────────┘     └─────────────┘

┌─────────────┐     ┌──────────────┐
│   Hotel     │     │ HotelBooking │
│             │────▶│              │
│ id (PK)     │     │ hotel_id(FK) │
│             │     │ booking_ref  │
└─────────────┘     └──────────────┘

┌─────────────┐     ┌─────────────────┐
│  Activity   │     │ ActivityBooking │
│             │────▶│                 │
│ id (PK)     │     │ activity_id(FK) │
│             │     │ booking_ref     │
└─────────────┘     └─────────────────┘

┌─────────────┐     ┌─────────────────┐
│   Transport │     │TransportBooking │
│             │────▶│                 │
│ id (PK)     │     │ transport_id(FK)│
│             │     │ booking_ref     │
└─────────────┘     └─────────────────┘

┌─────────────┐
│   User      │ (Admin)
│             │
│ id (PK)     │
│ username    │
│ password    │
│ role        │
└─────────────┘
```

---

## Inventory Tables

### Flight

```python
class Flight(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    origin: str                    # Departure city (e.g., "Bangkok")
    destination: str               # Arrival city (e.g., "Singapore")
    airline: str                   # Airline name (e.g., "Singapore Airlines")
    departure_time: datetime      # ISO format datetime
    arrival_time: datetime        # ISO format datetime
    price: float                  # Price in USD per person
    seats_available: int          # Available seats
    class_type: str               # "economy", "business", "first"
```

### Hotel

```python
class Hotel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str                    # Hotel name (e.g., "Marina Bay Hotel")
    city: str                    # City location (e.g., "Singapore")
    stars: int                   # Star rating 1-5
    price_per_night: float       # Price per night in USD
    amenities: str               # Comma-separated (e.g., "wifi,pool,gym")
    rooms_available: int        # Available rooms
```

### Activity

```python
class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str                    # Activity name (e.g., "City Tour")
    city: str                    # City location
    category: str               # "adventure", "culture", "food", "nature", "wellness", "nightlife", "water_sports"
    duration_hours: float       # Duration in hours
    price: float                # Price per person in USD
    availability: int           # Available slots
```

### Transport

```python
class Transport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str                   # "car", "ferry", "bus", "train", "minivan"
    origin: str                 # Departure location (e.g., "Bangkok Airport")
    destination: str            # Arrival location (e.g., "Downtown Bangkok")
    departure_time: datetime   # ISO format datetime
    arrival_time: datetime     # ISO format datetime
    price: float               # Price per person in USD
    capacity: int              # Available seats
```

---

## Booking Tables

### FlightBooking

```python
class FlightBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    flight_id: int = Field(foreign_key="flight.id")
    passenger_name: str         # Full name as on ticket
    contact_email: str          # Email for confirmation
    booking_reference: str     # Unique ref (TB-YYYYMMDD-XXXX)
    status: str = "confirmed"  # Booking status
    seats_booked: int = 1      # Number of seats
    created_at: datetime       # Creation timestamp
```

### HotelBooking

```python
class HotelBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hotel_id: int = Field(foreign_key="hotel.id")
    guest_name: str            # Primary guest name
    contact_email: str         # Email for confirmation
    check_in_date: str         # YYYY-MM-DD format
    check_out_date: str        # YYYY-MM-DD format
    nights: int                # Number of nights
    guests: int = 1            # Number of guests
    booking_reference: str     # Unique reference
    status: str = "confirmed" # Status
    created_at: datetime       # Timestamp
```

### ActivityBooking

```python
class ActivityBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="activity.id")
    participant_name: str      # Primary participant name
    contact_email: str         # Email for confirmation
    activity_date: str         # YYYY-MM-DD format
    participants: int = 1      # Number of participants
    booking_reference: str     # Unique reference
    status: str = "confirmed" # Status
    created_at: datetime       # Timestamp
```

### TransportBooking

```python
class TransportBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transport_id: int = Field(foreign_key="transport.id")
    passenger_name: str        # Primary passenger name
    contact_email: str         # Email for confirmation
    passengers: int = 1        # Number of passengers
    booking_reference: str     # Unique reference
    status: str = "confirmed" # Status
    created_at: datetime       # Timestamp
```

---

## Payment Table

### Payment

```python
class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    booking_reference: str     # Reference from initiate_payment (PAY-XXXXXX)
    amount: float              # Payment amount in USD
    status: str = "pending"   # "pending" or "paid"
    created_at: datetime       # Creation timestamp
```

---

## Insurance Table

### Insurance

```python
class Insurance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str                  # Plan name (e.g., "Basic Coverage")
    price_per_person: float    # Price per person in USD
    description: str           # Plan description
    coverage_types: str        # Comma-separated types
    medical_coverage: int      # Medical coverage amount
    cancellation_coverage: int # Cancellation coverage amount

class InsuranceBooking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="insurance.id")
    traveler_name: str         # Name of insured person
    contact_email: str         # Email for documents
    booking_reference: str     # Unique reference
    status: str = "confirmed" # Status
    created_at: datetime       # Timestamp
```

---

## Visa Table

### VisaRequirement

```python
class VisaRequirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    origin_country: str        # Traveler's country (e.g., "Myanmar")
    destination_country: str   # Destination (e.g., "Singapore")
    visa_required: bool        # Is visa required?
    visa_on_arrival: bool      # Is visa on arrival available?
    visa_eta: str | None       # eVisa information
    max_stay_days: int | None  # Maximum stay duration
    notes: str | None          # Additional notes
```

---

## Weather Table

### WeatherForecast

```python
class WeatherForecast(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    city: str                  # City name (e.g., "Bangkok")
    date: str                  # Date (YYYY-MM-DD)
    condition: str             # "sunny", "partly_cloudy", "cloudy", "rainy", "stormy", "humid"
    temperature_min: float     # Min temperature in Celsius
    temperature_max: float     # Max temperature in Celsius
    humidity: int              # Humidity percentage
    precipitation_mm: float    # Precipitation in mm
    uv_index: int              # UV index
```

---

## User Table

### User

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str              # Admin username
    hashed_password: str       # Hashed password
    role: str = "admin"        # User role (currently "admin" only)
```

---

## Response Models

### BookingPackageItem

A single booking item within a package grouping:

```python
class BookingPackageItem(SQLModel):
    kind: str                  # "flight", "hotel", "activity", "transport"
    id: Optional[int] = None  # Booking ID
    passenger_name: str        # Name
    contact_email: str         # Email
    status: str               # Status
    created_at: datetime      # Creation time
    # Type-specific fields
    flight_id: Optional[int] = None
    hotel_id: Optional[int] = None
    activity_id: Optional[int] = None
    transport_id: Optional[int] = None
    seats_booked: Optional[int] = None
    guests: Optional[int] = None
    participants: Optional[int] = None
    passengers: Optional[int] = None
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None
    activity_date: Optional[str] = None
```

### BookingPackage

A complete travel package (all items with same booking_reference):

```python
class BookingPackage(SQLModel):
    booking_reference: str             # Unique package reference
    items: list[BookingPackageItem]   # All items in package
    total_items: int                  # Count of items
    created_at: str                   # ISO datetime of earliest item
```

### BookingStats

Aggregated booking statistics:

```python
class BookingStats(SQLModel):
    total_bookings: int              # Total number of bookings
    unique_users: int                # Unique email count
    by_type: dict[str, int]          # Breakdown by type
```

---

## Seeding Scripts

The database can be seeded with sample data using:

- `server/seed.py` - Main seed script for flights, hotels, activities, transport
- `server/seed_visa.py` - Visa requirements data
- `server/seed_weather.py` - Weather forecast data
- `server/seed_insurance.py` - Insurance plans data

---

## Indexes

The following indexes are created automatically by SQLModel:

- Primary keys on all tables
- Foreign key constraints for relationships

Additional indexes can be added for performance optimization on frequently queried columns:
- `Flight.destination`
- `Hotel.city`
- `Activity.city`, `Activity.category`
- `Transport.origin`, `Transport.destination`
- Booking tables: `booking_reference` (already unique)