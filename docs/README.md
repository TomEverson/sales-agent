# Travelbase Salebot - Technical Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Component Overview](#component-overview)
4. [Data Flow](#data-flow)
5. [Tech Stack](#tech-stack)
6. [Getting Started](#getting-started)
7. [API Reference](#api-reference)
8. [Bot Tools Reference](#bot-tools-reference)
9. [Database Schema](#database-schema)
10. [Configuration](#configuration)

---

## Overview

**Travelbase Salebot** is an AI-powered travel sales agent built for a Southeast Asia travel platform. It provides a conversational interface through Telegram where users can search, compare, and book complete tour packages including flights, hotels, activities, and transport.

### Key Features

- **AI-Powered Conversations**: Uses Claude AI to understand user intent and provide personalized recommendations
- **Real-Time Inventory**: Accesses live product data via backend API (no scraping)
- **Multi-Language Support**: English and Burmese (Myanmar) languages
- **Complete Booking Flow**: From search to payment confirmation
- **Travel Services**: Flights, hotels, activities, transport, visa requirements, weather forecasts, travel insurance
- **Admin Dashboard**: React-based admin interface for managing inventory and viewing bookings

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Telegram User  │────▶│   Salebot       │────▶│    FastAPI      │
│                 │◀────│   (Python)      │◀────│    Backend      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │                        │
                              │                        │
                              ▼                        ▼
                       ┌──────────┐            ┌──────────────┐
                       │ Claude    │            │   SQLite     │
                       │ API      │            │   Database   │
                       └──────────┘            └──────────────┘
```

### Components

1. **Salebot** (`/salebot`) - Telegram bot with Claude agent
2. **Server** (`/server`) - FastAPI backend with SQLite
3. **Client** (`/client`) - React admin frontend

---

## Component Overview

### 1. Salebot (Telegram Bot)

| File | Purpose |
|------|---------|
| `bot.py` | Telegram bot entry point, handles incoming messages, commands, and callbacks |
| `agent.py` | Agentic loop - calls Claude API with tools, manages conversation flow |
| `mcp_tools.py` | Tool definitions for Claude + HTTP calls to backend |
| `memory.py` | In-memory conversation history with JSON file persistence |
| `prompts/system_prompt.md` | Agent persona and decision-making instructions |

### 2. Server (FastAPI Backend)

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app setup, CORS, router registration |
| `db.py` | Database connection and table creation |
| `seed.py` | Populates database with sample data |

**Routers** (`server/routers/`):

| Router | Purpose |
|--------|---------|
| `flights.py` | Flight inventory CRUD |
| `hotels.py` | Hotel inventory CRUD |
| `activities.py` | Activity inventory CRUD |
| `transport.py` | Transport options CRUD |
| `bookings.py` | Booking creation and management |
| `payments.py` | Payment initiation and confirmation |
| `visa.py` | Visa requirements lookup |
| `weather.py` | Weather forecast data |
| `insurance.py` | Travel insurance plans |
| `auth.py` | Admin authentication |

**Models** (`server/models/`):

| Model | Purpose |
|-------|---------|
| `flight.py` | Flight inventory schema |
| `hotel.py` | Hotel inventory schema |
| `activity.py` | Activity inventory schema |
| `transport.py` | Transport options schema |
| `booking.py` | Booking records and packages |
| `payment.py` | Payment records |
| `visa.py` | Visa requirement data |
| `weather.py` | Weather forecast data |
| `insurance.py` | Insurance plan data |
| `user.py` | Admin user data |

### 3. Client (React Admin Frontend)

- **Framework**: React 19 with Vite
- **Routing**: React Router DOM
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Testing**: Playwright E2E

**Pages**:

- `Home` - Dashboard with booking statistics
- `Flights` - Flight inventory management
- `Hotels` - Hotel inventory management
- `Activities` - Activity inventory management
- `Transport` - Transport options management
- `Bookings` - View all bookings
- `Support` - Contact information
- `Login` - Admin authentication

---

## Data Flow

1. **User sends message to Telegram bot** → `salebot/bot.py`
2. **Bot calls agent** → `agent.handle_message(user_id, text)`
3. **Agent runs agentic loop**:
   - Calls Claude API with conversation history and available tools
   - Claude decides which tool to call based on user intent
   - Agent executes tool (HTTP call to FastAPI)
   - Tool results fed back to Claude for response generation
4. **Tools make HTTP calls** to FastAPI at `http://localhost:8000`
5. **FastAPI queries SQLite** (`travel.db`) and returns results
6. **Final Claude text response** sent back to Telegram

---

## Tech Stack

### Salebot

- **Language**: Python 3.12
- **AI**: Anthropic Claude API (claude-haiku-4-5)
- **Telegram**: python-telegram-bot
- **HTTP**: httpx
- **Config**: python-dotenv

### Server

- **Framework**: FastAPI
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: SQLite
- **Server**: Uvicorn

### Client

- **Framework**: React 19
- **Build**: Vite 8
- **Routing**: React Router DOM 7
- **Styling**: Tailwind CSS 4
- **Language**: TypeScript

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Anthropic API key
- Telegram Bot Token

### Environment Setup

1. **Create `salebot/.env`**:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
ANTHROPIC_API_KEY=your_api_key
```

2. **Start the server**:
```bash
cd server
uv run uvicorn main:app --reload
```

3. **Seed the database** (first time):
```bash
cd server
uv run python seed.py
```

4. **Start the bot**:
```bash
cd salebot
uv run python bot.py
```

5. **Start the client** (for admin):
```bash
cd client
npm run dev
```

### Ports

- **Server**: http://localhost:8000
- **Client**: http://localhost:5173
- **Bot**: Telegram (external)

---

## API Reference

### Base URL

```
http://localhost:8000
```

### Endpoints

#### Health Check
```
GET /health
```

#### Flights
```
GET    /flights              # List all flights (optional: origin, destination, class_type)
GET    /flights/{flight_id}  # Get specific flight
POST   /flights              # Create flight
PUT    /flights/{flight_id}  # Update flight
DELETE /flights/{flight_id}  # Delete flight
```

#### Hotels
```
GET    /hotels               # List all hotels (optional: city, stars, max_price)
GET    /hotels/{hotel_id}    # Get specific hotel
POST   /hotels               # Create hotel
PUT    /hotels/{hotel_id}    # Update hotel
DELETE /hotels/{hotel_id}    # Delete hotel
```

#### Activities
```
GET    /activities               # List all activities (optional: city, category)
GET    /activities/{activity_id} # Get specific activity
POST   /activities               # Create activity
PUT    /activities/{activity_id}  # Update activity
DELETE /activities/{activity_id} # Delete activity
```

#### Transport
```
GET    /transport               # List all transport (optional: origin, destination, type)
GET    /transport/{transport_id}# Get specific transport
POST   /transport               # Create transport
PUT    /transport/{transport_id}# Update transport
DELETE /transport/{transport_id}# Delete transport
```

#### Bookings
```
POST   /bookings/flights        # Create flight booking
GET    /bookings/flights        # List flight bookings (optional: email)
GET    /bookings/flights/{id}   # Get flight booking

POST   /bookings/hotels         # Create hotel booking
GET    /bookings/hotels         # List hotel bookings
GET    /bookings/hotels/{id}    # Get hotel booking

POST   /bookings/activities     # Create activity booking
GET    /bookings/activities     # List activity bookings
GET    /bookings/activities/{id}# Get activity booking

POST   /bookings/transport      # Create transport booking
GET    /bookings/transport      # List transport bookings
GET    /bookings/transport/{id} # Get transport booking

GET    /bookings/packages       # Get all bookings grouped by package
GET    /bookings/stats          # Get booking statistics
```

#### Payments
```
POST   /payments                     # Initiate payment
GET    /payments/{reference}         # Get payment status
PUT    /payments/{reference}/confirm # Confirm payment
```

#### Visa
```
GET    /visa/{origin}/{destination}  # Check visa requirements
```

#### Weather
```
GET    /weather/{city}               # Get weather (optional: start_date, end_date)
```

#### Insurance
```
GET    /insurance                    # Get insurance plans
POST   /insurance/book               # Book insurance
```

#### Auth
```
POST   /auth/login        # Admin login
GET    /auth/me           # Get current user
```

---

## Bot Tools Reference

The agent has access to the following tools (defined in `salebot/mcp_tools.py`):

### Search Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `search_flights` | Search available flights | `origin`, `destination`, `class_type` |
| `search_hotels` | Search available hotels | `city`, `stars`, `max_price` |
| `search_activities` | Search activities/experiences | `city`, `category` |
| `search_transport` | Search local transport | `origin`, `destination`, `type` |

### Booking Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `book_flight` | Book a flight | `flight_id`, `passenger_name`, `contact_email`, `seats_booked` |
| `book_hotel` | Book a hotel room | `hotel_id`, `guest_name`, `contact_email`, `check_in_date`, `check_out_date`, `nights`, `guests` |
| `book_activity` | Book an activity | `activity_id`, `participant_name`, `contact_email`, `activity_date`, `participants` |
| `book_transport` | Book transport | `transport_id`, `passenger_name`, `contact_email`, `passengers` |
| `add_insurance` | Add travel insurance | `plan_id`, `traveler_name`, `contact_email` |

### Information Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `check_visa` | Check visa requirements | `origin_country`, `destination_country` |
| `get_weather` | Get weather forecast | `city`, `start_date`, `end_date` |
| `get_insurance_plans` | Get available insurance plans | (none) |
| `get_operator_contact` | Get human operator contact | (none) |

### Payment Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `initiate_payment` | Initiate payment for package | `amount` |
| `confirm_payment` | Confirm payment received | `booking_reference` |
| `check_payment_status` | Check payment status | `booking_reference` |

---

## Database Schema

### Flight
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| origin | String | Departure city |
| destination | String | Arrival city |
| airline | String | Airline name |
| departure_time | DateTime | Departure time |
| arrival_time | DateTime | Arrival time |
| price | Float | Price in USD |
| seats_available | Integer | Available seats |
| class_type | String | economy, business, first |

### Hotel
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| name | String | Hotel name |
| city | String | City location |
| stars | Integer | Star rating (1-5) |
| price_per_night | Float | Price per night |
| amenities | String | Comma-separated amenities |
| rooms_available | Integer | Available rooms |

### Activity
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| name | String | Activity name |
| city | String | City location |
| category | String | Category (adventure, culture, etc.) |
| duration_hours | Float | Duration in hours |
| price | Float | Price in USD |
| availability | Integer | Available spots |

### Transport
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| type | String | car, ferry, bus, train, minivan |
| origin | String | Departure location |
| destination | String | Arrival location |
| departure_time | DateTime | Departure time |
| arrival_time | DateTime | Arrival time |
| price | Float | Price per person |
| capacity | Integer | Available capacity |

### Booking Tables

Each booking type (Flight, Hotel, Activity, Transport) has a corresponding booking table with:
- `id` - Primary key
- `related_id` - Foreign key to inventory item
- `passenger_name` / `guest_name` / `participant_name`
- `contact_email`
- `booking_reference` - Unique reference (format: TB-YYYYMMDD-XXXX)
- `status` - Booking status
- `created_at` - Creation timestamp

### Payment
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| booking_reference | String | Reference from initiate_payment |
| amount | Float | Payment amount |
| status | String | pending, paid |
| created_at | DateTime | Creation timestamp |

---

## Configuration

### Server Configuration

The server uses default configuration:
- **Database**: SQLite (`travel.db` in server directory)
- **CORS**: Only allows `http://localhost:5173` (client)
- **Port**: 8000

### Bot Configuration

Environment variables in `salebot/.env`:
- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `ANTHROPIC_API_KEY` - API key from Anthropic

### Memory Configuration

In `salebot/memory.py`:
- `MAX_MESSAGES = 20` - Maximum messages stored per user
- Data persisted to `salebot/data/conversations.json` and `salebot/data/preferences.json`

---

## Development Commands

### Server (FastAPI)
```bash
cd server
uv run uvicorn main:app --reload   # Start on http://localhost:8000
uv run python seed.py              # Seed SQLite database
ruff check .                       # Lint Python
```

### Bot (Telegram + Claude agent)
```bash
cd salebot
uv run python bot.py               # Start Telegram bot
```

### Client (React)
```bash
cd client
npm run dev      # Start Vite dev server on http://localhost:5173
npm run build    # Production build
npm run lint     # Lint TypeScript
npm run test:e2e # Run Playwright tests
```