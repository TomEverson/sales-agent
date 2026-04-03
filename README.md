# Travelbase Salebot

**P.02 AI Shopping Agent Team** — Tom Everson, Sai Zayar Tun

An AI-powered travel sales agent for Southeast Asia. Users chat with a Telegram bot to build a complete tour package — flights, hotels, activities, transport, and insurance — all within their budget, fully booked and paid through the conversation.

---

## Architecture Overview

```
Telegram User
     │
     ▼
┌─────────────┐     agentic loop      ┌──────────────────┐
│  salebot/   │ ──────────────────▶  │  Anthropic API   │
│  bot.py     │ ◀──────────────────  │  claude-haiku-4-5│
└──────┬──────┘   tool calls/results  └──────────────────┘
       │
       │ HTTP (tool executors)
       ▼
┌─────────────┐
│  server/    │  FastAPI + SQLite
│  main.py    │  REST API on :8000
└─────────────┘
       ▲
       │ HTTP
┌─────────────┐
│  client/    │  React + Tailwind
│  (Admin UI) │  Vite dev server :5173
└─────────────┘
```

**Data flow:**
1. User sends a message to the Telegram bot
2. `bot.py` calls `agent.handle_message(user_id, text)`
3. `agent.py` runs an agentic loop — calls Claude with 16 tools until no more `tool_use` blocks remain
4. Tool executors in `mcp_tools.py` make HTTP calls to the FastAPI backend at `http://localhost:8000`
5. FastAPI queries SQLite (`travel.db`) and returns results
6. Claude's final text response is sent back to Telegram
7. Conversation history (capped at 20 messages) is persisted to JSON on disk

---

## Components

### `salebot/` — Telegram Bot + Claude Agent

| File | Purpose |
|------|---------|
| `bot.py` | Telegram handlers: `/start`, `/clear`, messages, photos, language callbacks |
| `agent.py` | Agentic loop: sends messages to Claude, dispatches tool calls, returns final text |
| `mcp_tools.py` | 16 tool definitions (Anthropic schema) + async HTTP executors |
| `memory.py` | Per-user conversation history + language prefs + pending payments, persisted to JSON |
| `prompts/system_prompt.md` | English agent persona, rules, and decision-making instructions |
| `prompts/system_prompt_my.md` | Burmese language system prompt |
| `package_builder.py` | Formats a complete tour package as Telegram Markdown |
| `data/conversations.json` | Persisted conversation histories (auto-created) |
| `data/preferences.json` | Persisted language preferences and pending payments (auto-created) |

**Agent tools (16 total):**

| Category | Tool | Description |
|----------|------|-------------|
| Search | `search_flights` | Find flights by origin/destination/class |
| Search | `search_hotels` | Find hotels by city/stars/max price |
| Search | `search_activities` | Find activities by city/category |
| Search | `search_transport` | Find transport between two locations |
| Booking | `book_flight` | Create a flight booking |
| Booking | `book_hotel` | Create a hotel booking |
| Booking | `book_activity` | Create an activity booking |
| Booking | `book_transport` | Create a transport booking |
| Info | `check_visa` | Check visa requirements by passport/destination country |
| Info | `get_weather` | Get weather forecast for a city |
| Info | `get_insurance_plans` | List available travel insurance plans |
| Info | `get_operator_contact` | Return human support contact details |
| Insurance | `add_insurance` | Add a travel insurance plan to a booking |
| Payment | `initiate_payment` | Create a payment record, return QR/reference |
| Payment | `confirm_payment` | Mark a payment as paid (triggered by screenshot) |
| Payment | `check_payment_status` | Check if a payment reference has been confirmed |

### `server/` — FastAPI Backend

REST API serving the travel inventory database. All inventory data is stored in `travel.db` (SQLite), managed via SQLModel.

**Routers:**

| Router | Prefix | Description |
|--------|--------|-------------|
| `flights` | `/flights` | CRUD for flight inventory |
| `hotels` | `/hotels` | CRUD for hotel inventory |
| `activities` | `/activities` | CRUD for activity inventory |
| `transport` | `/transport` | CRUD for transport options |
| `bookings` | `/bookings` | Create/list bookings (flights, hotels, activities, transport, packages, stats) |
| `visa` | `/visa` | Visa requirement lookups |
| `weather` | `/weather` | Weather forecast by city |
| `insurance` | `/insurance` | Insurance plans + booking |
| `payments` | `/payments` | Payment initiation and confirmation |
| `auth` | `/auth` | Admin login (JWT), `/auth/me` |

Interactive API docs available at **http://localhost:8000/docs** when running.

### `client/` — React Admin UI

A browser-based admin dashboard for browsing inventory and managing bookings.

**Pages:**

| Page | Route | Description |
|------|-------|-------------|
| Home | `/` | Dashboard / overview |
| Flights | `/flights` | Browse flight inventory |
| Hotels | `/hotels` | Browse hotel inventory |
| Activities | `/activities` | Browse activity inventory |
| Transport | `/transport` | Browse transport options |
| Bookings | `/bookings` | View all bookings grouped as packages |
| Support | `/support` | Emergency contact / operator page |
| Login | `/login` | Admin authentication |

**Stack:** React 19, TypeScript, Tailwind CSS 4, React Router 7, Axios, Vite 8, Playwright (E2E tests)

---

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Node.js 18+ and npm
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))
- An Anthropic API key

### 1. Set up the Server

```bash
cd server
uv sync                                         # Install dependencies
uv run python seed.py                           # Seed flights, hotels, activities, transport
uv run python seed_visa.py                      # Seed visa requirements
uv run python seed_weather.py                   # Seed weather forecasts
uv run python seed_insurance.py                 # Seed insurance plans
uv run uvicorn main:app --reload                # Start on http://localhost:8000
```

### 2. Configure the Bot

Create `salebot/.env`:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ADMIN_CHAT_ID=your_telegram_user_id_here   # optional
```

### 3. Start the Bot

```bash
cd salebot
uv sync                  # Install dependencies
uv run python bot.py     # Start the Telegram bot
```

### 4. Start the Admin Client (optional)

```bash
cd client
npm install
npm run dev              # Start on http://localhost:5173
```

---

## Development Commands

### Server

```bash
cd server
uv run uvicorn main:app --reload    # Start dev server with hot reload
uv run pytest                       # Run tests
ruff check .                        # Lint
```

### Bot

```bash
cd salebot
uv run python bot.py                # Run the bot
uv run pytest                       # Run tests
uv run ruff check .                 # Lint
```

### Client

```bash
cd client
npm run dev             # Start Vite dev server
npm run build           # Production build
npm run lint            # ESLint
npm run test:e2e        # Playwright end-to-end tests
```

---

## Booking Flow

The agent enforces a strict all-or-nothing flow:

```
1. User describes trip (destination, dates, budget)
        │
2. Agent searches flights → hotels → activities → transport
        │
3. Agent presents complete package with total cost
        │
4. User requests tweaks (optional) ──▶ Agent rebuilds package
        │
5. User confirms package ("book it")
        │
6. Agent collects traveler details (name, email, dates)
        │
7. Agent presents full booking summary + insurance options
        │
8. Agent calls initiate_payment → shows QR + PAY-XXXXXX reference
        │
9. User sends payment screenshot
        │
10. Agent calls confirm_payment
        │
11. Agent books all items in order:
        book_flight → book_hotel → book_activity × N → book_transport → add_insurance
        │
    ┌───┴───┐
    │       │
   ALL    ANY FAIL
  succeed    │
    │    STOP — no partial bookings shown
    │    Search alternatives
    │
12. Agent shows all booking references
13. Agent shows weather forecast for travel dates
```

**Hard rules enforced by the system prompt:**
- Never create bookings before payment is confirmed
- If any booking fails, stop immediately — no partial confirmations
- Never invent prices or availability — only return data from tool results
- Always check visa requirements before confirming a booking
- Filter out flights with `seats_available == 0` and hotels with `rooms_available == 0`

---

## Language Support

The bot supports **English** and **Burmese (Myanmar)**:

- On first message, the bot displays an inline keyboard to select language
- Language preference is persisted across sessions in `salebot/data/preferences.json`
- The agent loads the matching system prompt (`system_prompt.md` / `system_prompt_my.md`)
- Burmese script is auto-detected from Unicode range U+1000–U+109F
- Users can reset with `/clear` and re-select language

---

## Conversation Memory

- **Storage:** In-memory dict + JSON file persistence
- **Files:** `salebot/data/conversations.json`, `salebot/data/preferences.json`
- **Cap:** 20 messages per user (oldest messages pruned automatically)
- **Cleared on:** `/clear` command, or after a booking is confirmed
- **Persists:** Full conversation history, language preference, pending payment reference

---

## Database Schema (SQLite)

**Inventory tables:** `flight`, `hotel`, `activity`, `transport`

**Booking tables:** `flightbooking`, `hotelbooking`, `activitybooking`, `transportbooking`

**Other tables:** `payment`, `insurance`, `insurancebooking`, `visarequirement`, `weatherforecast`, `user`

Booking references use format `TB-YYYYMMDD-XXXX`. Payment references use `PAY-XXXXXXXX`.

See [`docs/database-schema.md`](docs/database-schema.md) for full schema details.

---

## API Reference

Full endpoint reference at [`docs/api-endpoints.md`](docs/api-endpoints.md), or interactively at http://localhost:8000/docs.

**Key endpoints summary:**

```
GET  /health                              Health check
GET  /flights?origin=&destination=        Search flights
GET  /hotels?city=&stars=&max_price=      Search hotels
GET  /activities?city=&category=          Search activities
GET  /transport?origin=&destination=      Search transport
POST /bookings/flights                    Create flight booking
POST /bookings/hotels                     Create hotel booking
POST /bookings/activities                 Create activity booking
POST /bookings/transport                  Create transport booking
GET  /bookings/packages                   All bookings grouped by reference
GET  /bookings/stats                      Booking statistics
POST /payments                            Initiate payment
PUT  /payments/{ref}/confirm              Confirm payment
GET  /visa/{origin}/{destination}         Visa requirements
GET  /weather/{city}                      Weather forecast
GET  /insurance                           Insurance plans
POST /insurance/book                      Book insurance
POST /auth/login                          Admin login (returns JWT)
GET  /auth/me                             Current admin user
```

---

## Admin Access

The admin UI at http://localhost:5173 is protected by JWT authentication.

Default admin credentials (auto-created on server startup):
- **Username:** `admin`
- **Password:** `admin123`

Change these in `server/routers/auth.py` → `ensure_admin_user()` before deploying.

---

## Project Structure

```
sales_agent/
├── salebot/                    # Telegram bot + Claude agent
│   ├── bot.py                  # Telegram event handlers
│   ├── agent.py                # Claude agentic loop
│   ├── mcp_tools.py            # Tool definitions + HTTP executors
│   ├── memory.py               # Conversation memory (in-memory + JSON)
│   ├── package_builder.py      # Tour package formatter
│   ├── prompts/
│   │   ├── system_prompt.md    # English agent instructions
│   │   └── system_prompt_my.md # Burmese agent instructions
│   ├── data/                   # Auto-created at runtime
│   │   ├── conversations.json
│   │   └── preferences.json
│   └── tests/                  # Pytest test suite
├── server/                     # FastAPI backend
│   ├── main.py                 # App setup, CORS, router registration
│   ├── db.py                   # SQLite engine + table creation
│   ├── models/                 # SQLModel ORM + Pydantic schemas
│   ├── routers/                # One router per resource
│   ├── seed.py                 # Main inventory seed script
│   ├── seed_visa.py            # Visa data seed
│   ├── seed_weather.py         # Weather data seed
│   ├── seed_insurance.py       # Insurance plans seed
│   ├── travel.db               # SQLite database (auto-created)
│   └── tests/                  # Pytest test suite
├── client/                     # React admin UI
│   ├── src/
│   │   ├── pages/              # Route-level components
│   │   ├── components/         # Shared UI components
│   │   ├── services/           # Axios API client
│   │   ├── context/            # React context (auth)
│   │   └── types/              # TypeScript interfaces
│   └── tests/                  # Playwright E2E tests
├── docs/
│   ├── api-endpoints.md        # Full API reference
│   ├── database-schema.md      # Full schema reference
│   └── agent-workflow.md       # Agent decision-making guide
├── rules/                      # Development guidelines
│   ├── base.md
│   ├── bot.md
│   ├── server.md
│   └── client.md
└── specs/                      # Sprint feature specs (TB-01 → TB-44)
```

---

## Environment Variables

**`salebot/.env`**
```env
TELEGRAM_BOT_TOKEN=      # From @BotFather
ANTHROPIC_API_KEY=       # From console.anthropic.com
ADMIN_CHAT_ID=           # Optional: your Telegram user ID for admin notifications
```

**`server/.env`** — currently empty, reserved for future config (database URL, JWT secret override, etc.)

---

## Human Operator Escalation

When the agent cannot resolve an issue, it calls `get_operator_contact` and provides:

- **Phone / WhatsApp:** +66 81 234 5678
- **Email:** support@travelbase.com
- **Telegram:** @travelbase_support

Escalation is triggered when:
- A backend service is unreachable
- A booking fails after payment is confirmed
- The user explicitly asks to speak with a human
- The same issue fails 2–3 times consecutively
