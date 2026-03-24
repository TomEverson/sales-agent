Build a FastAPI backend server for a travel inventory website.

## Stack
- FastAPI
- SQLModel (ORM + schema in one)
- SQLite (file: server/travel.db)
- Python 3.11+
- uv for environment management

## Environment Setup

Use uv for Python environment management.

- Initialize the project with: uv init
- Create virtual environment with: uv venv
- Install dependencies with: uv add fastapi uvicorn sqlmodel python-dotenv
- Use pyproject.toml instead of requirements.txt
- All run instructions should use: uv run uvicorn main:app --reload
- Seed script should run with: uv run python seed.py

## Project structure to generate
server/
├── models/
│   ├── flight.py
│   ├── hotel.py
│   ├── activity.py
│   └── transport.py
├── routers/
│   ├── flights.py
│   ├── hotels.py
│   ├── activities.py
│   └── transport.py
├── db.py
├── seed.py
└── main.py

## Models

Each model file should define two classes:
1. A SQLModel table class (table=True)
2. A Create schema class (no id, for POST requests)

### Flight
- id: int (primary key)
- origin: str
- destination: str
- airline: str
- departure_time: datetime
- arrival_time: datetime
- price: float
- seats_available: int
- class_type: str  # economy, business, first

### Hotel
- id: int (primary key)
- name: str
- location: str
- city: str
- stars: int
- price_per_night: float
- rooms_available: int
- amenities: str  # comma-separated string

### Activity
- id: int (primary key)
- name: str
- city: str
- description: str
- duration_hours: float
- price: float
- category: str  # adventure, culture, food, nature, etc.
- availability: str  # daily, weekends, specific dates

### Transport
- id: int (primary key)
- type: str  # car, ferry, bus, train
- origin: str
- destination: str
- price: float
- capacity: int
- departure_time: datetime
- arrival_time: datetime

## Routers

Each router should implement:
- GET    /         → list all (with optional query param filters)
- GET    /{id}     → get one by id
- POST   /         → create one
- PUT    /{id}     → update one
- DELETE /{id}     → delete one

Filters for list endpoints:
- flights: origin, destination, class_type
- hotels: city, stars, max_price
- activities: city, category
- transport: type, origin, destination

## db.py
- Create SQLite engine pointing to server/travel.db
- Create all tables on startup using SQLModel.metadata.create_all
- Expose a get_session() dependency for routers to use

## main.py
- Create FastAPI app
- Include all 4 routers with prefixes: /flights /hotels /activities /transport
- Call create_db_and_tables() on startup
- Enable CORS for http://localhost:5173 (React Vite dev server)

## seed.py
- Standalone script (if __name__ == "__main__")
- Insert at least 5 realistic records per table
- Use cities in Southeast Asia (Bangkok, Bali, Singapore, Phuket, KL etc.)
- Clear existing data before seeding

## Rules
- Use typing annotations everywhere
- All datetime fields should use datetime type, stored as ISO string in SQLite
- No authentication needed
- Return proper HTTP status codes (404 when not found, etc.)
- Keep it simple — no nested models, no relationships between tables for now