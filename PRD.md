# P.02 Travelbase Salebot — Product Requirements Document

**Team:** Tom Everson, Sai Zayar Tun

---

## General Description

An AI-powered travel sales agent for Southeast Asia, delivered through Telegram. Users describe where they want to go and their budget in plain language, and the agent builds a complete, bookable tour package — flights, hotels, activities, transport, and travel insurance — all within their budget. The entire journey from search to confirmed booking and payment happens inside the chat.

The agent is powered by Claude (Anthropic) using an agentic tool-calling loop. It retrieves live inventory from a FastAPI backend, never inventing prices or availability. A React admin dashboard lets operators manage inventory, view bookings, and monitor revenue.

---

## Pivot Note

This project was initially scoped as a general-purpose e-commerce shopping agent using a generic MCP product database. After evaluating the domain, the team pivoted to a travel-specific agent targeting Southeast Asia. The pivot allowed the team to design a richer, more realistic booking workflow and deliver a product with genuine end-to-end value: search → package → payment → confirmed booking.

---

## Features

- Conversational travel package builder via Telegram
- Live inventory search (flights, hotels, activities, transport)
- All-or-nothing package booking (pay first, then all bookings confirmed atomically)
- QR-based payment flow with screenshot confirmation
- Visa requirement checks by passport country
- Weather forecast shown after booking
- Travel insurance add-on (3 tiers)
- Flight comparison table with duration and seat availability
- Burmese language support with auto-detection
- Human operator escalation for unresolvable errors
- Persistent conversation memory across bot restarts
- Admin dashboard: inventory management, booking packages view, statistics
- JWT-protected admin authentication
- Playwright end-to-end test coverage for the client

---

## Product Requirements

### Feature 1: Inventory Search via Backend Tools

#### PR.1.1 — Flight Search
The agent calls `search_flights` with `origin`, `destination`, and optional `class_type` (economy / business / first). The backend returns all flights with `seats_available > 0`. Flights with zero seats are filtered before being shown to the user.

#### PR.1.2 — Hotel Search
The agent calls `search_hotels` with `city` and optional `stars` and `max_price` filters. Hotels with zero rooms available are filtered out.

#### PR.1.3 — Activity Search
The agent calls `search_activities` with `city` and optional `category` (adventure / culture / food / nature / wellness / nightlife / water_sports). All available activities are returned.

#### PR.1.4 — Transport Search
The agent calls `search_transport` with `origin` and `destination` (both required) and an optional `type` filter (car / ferry / bus / train / minivan). Transport is optional in a package and omitted silently if no results are found.

#### PR.1.5 — Inventory Data Schema

| Entity | Key Fields |
|--------|-----------|
| Flight | airline, origin, destination, departure_time, arrival_time, price, seats_available, class_type |
| Hotel | name, city, stars, price_per_night, amenities, rooms_available |
| Activity | name, city, category, duration_hours, price, availability |
| Transport | type, origin, destination, departure_time, arrival_time, price, capacity |

---

### Feature 2: Conversational Agent

#### PR.2.1 — Natural Language Understanding
Users describe their trip in plain language (e.g., "I want to go to Singapore this weekend, my budget is $1,000"). The agent extracts destination, travel dates, budget, number of travelers, and passport country. If any required field is missing, the agent asks — up to 2 clarifying questions per turn.

#### PR.2.2 — Guided Clarification Flow
- **Destination**: if not stated, the agent asks before searching
- **Budget**: always required; agent asks if not provided
- **Dates**: optional; agent proceeds with flexible dates (default 2 nights) if omitted
- **Travelers**: defaults to 1 if not stated
- **Passport country**: collected before visa check, before booking

#### PR.2.3 — Search Strategy
The agent always runs searches in this order before presenting a package:

1. `search_flights` — origin → destination
2. `search_hotels` — destination city
3. `search_activities` — destination city
4. `search_transport` — airport → city center (optional)

The agent never presents a package after fewer than 2 tool calls (flight + hotel minimum). If a search returns no results, the agent silently retries without filters and never tells the user a search "failed".

#### PR.2.4 — Flight Comparison Table (TB-32)
When presenting flight results, the agent renders a comparison table with columns: #, Airline, Departure, Arrival, Duration, Price, Seats. The cheapest option is highlighted. Flights with fewer than 20 seats show a ⚠️ indicator. The user selects by number.

#### PR.2.5 — Package Assembly Rules

**Flights:** prefer economy unless user specifies otherwise; pick best price within budget.

**Hotels:** calculate `price_per_night × nights`; pick highest star rating within remaining budget after flight.

**Activities:** always include at least 1 activity (a package with zero activities is invalid); include up to 3 if budget allows; prioritize category variety.

**Transport:** include only if it adds clear value (e.g., airport pickup); omit silently if budget is tight.

**Budget validation:** total must not exceed user's stated budget. If no valid package exists, the agent tells the user honestly and presents the minimum-cost alternative.

#### PR.2.6 — Package Tweak Handling
After presenting a package, the user may request changes. The agent handles each tweak type without re-searching the whole package:

| Tweak | Action |
|-------|--------|
| "Nicer hotel" / "Upgrade" | Re-search hotels with higher stars filter |
| "Cheaper hotel" | Re-search hotels with lower max_price filter |
| "Different flight" / "Earlier/later" | Re-search flights, present alternatives |
| "More activities" / "Add activity" | Re-search activities, suggest options within remaining budget |
| "Remove activity" | Remove from package, recalculate total |
| "Add transport" | Search transport airport → city center, add if found |

After any tweak, the agent always presents the **complete updated package**, never just the changed component.

---

### Feature 3: Booking System

#### PR.3.1 — All-or-Nothing Booking (TB-27)
Either all items in a package are booked, or none are. The agent collects all traveler details and booking dates before making any booking API calls. If any single booking fails, the agent stops immediately, informs the user that **no bookings have been made**, and offers to search for alternatives.

#### PR.3.2 — Information Collection
Before booking, the agent collects:
- Full traveler name (used on all booking items)
- Contact email (used for all confirmations)
- Number of travelers (default: 1)
- Check-in / check-out dates (for hotel)
- Activity date(s) (one per activity)

#### PR.3.3 — Booking API Calls
After payment is confirmed (see PR.5), bookings are created in this order:

1. `book_flight`
2. `book_hotel`
3. `book_activity` (once per activity)
4. `book_transport` (if applicable)
5. `add_insurance` (if user selected a plan)

Each booking returns a unique reference in the format `TB-YYYYMMDD-XXXX`.

#### PR.3.4 — Booking Confirmation
After all bookings succeed, the agent displays every booking reference number and automatically calls `get_weather` to show a forecast for the travel dates. The conversation history is cleared after successful booking.

#### PR.3.5 — Inventory Decrement
Each successful booking decrements the available count in the inventory (`seats_available`, `rooms_available`, `availability`, `capacity`) via the backend. Out-of-stock items are never shown to users in search results.

---

### Feature 4: Visa Requirements (TB-29)

#### PR.4.1 — Visa Check Before Booking
Before confirming any booking, the agent calls `check_visa` with the user's passport country and travel destination. The agent informs the user of the result:

- **Visa-free**: confirmed, proceed with booking
- **Visa on arrival**: inform user, proceed with confirmation
- **Visa required**: warn user, ask if they have arranged a visa before proceeding

The agent never proceeds with booking if the user needs a visa and has not confirmed they have one.

#### PR.4.2 — Visa Data
The backend stores visa requirements for common Southeast Asia travel corridors (Myanmar, Thailand, Singapore, Malaysia, Cambodia, Vietnam, Japan, South Korea, etc.). Lookups are by `origin_country` / `destination_country`.

---

### Feature 5: Payment Flow (TB-33, TB-34, TB-35)

#### PR.5.1 — Payment Initiation
After the user confirms the package and all booking details are collected, the agent calls `initiate_payment` with the total amount. The backend creates a payment record with status `pending` and returns a reference in the format `PAY-XXXXXXXX`.

The agent displays:
- A mock QR code block
- The payment reference number
- A request for the user to send a payment screenshot

**No bookings are created at this stage.**

#### PR.5.2 — Payment Confirmation via Screenshot
When the user sends a photo (any image), the bot treats it as a payment screenshot. The agent calls `confirm_payment` with the stored `PAY-XXXXXXXX` reference. If confirmed, the backend marks the payment as `paid` and the agent proceeds to create bookings (PR.3.3).

#### PR.5.3 — Payment Rules
- Bookings must **never** be created before `confirm_payment` succeeds
- If confirmation fails, the agent informs the user and offers to retry
- The pending payment reference is stored in per-user memory and survives bot restarts

---

### Feature 6: Travel Insurance (TB-31)

#### PR.6.1 — Insurance Plans
Three tiers are available, presented to the user as part of the booking summary:

| Plan | Price | Coverage |
|------|-------|----------|
| Basic | $15/person | Trip cancellation, flight delay |
| Standard | $35/person | Basic + medical up to $10,000 |
| Premium | $65/person | Standard + lost luggage, adventure sports |

#### PR.6.2 — Insurance Selection
After the user reviews the booking summary, the agent asks: "Would you like to add insurance? (1, 2, 3, or no)". If selected, the insurance cost is added to the payment total and `add_insurance` is called after all other bookings succeed.

---

### Feature 7: Weather Forecast (TB-30)

#### PR.7.1 — Post-Booking Weather
Immediately after displaying booking confirmations, the agent calls `get_weather` for the destination city using the check-in and check-out dates as the forecast range. A 7-day forecast is displayed with condition icons, temperature range, humidity, and travel tips based on expected conditions (rain, high UV, heat).

#### PR.7.2 — Weather Data
Weather data is pre-seeded in the database for major Southeast Asian cities. Conditions include: sunny, partly_cloudy, cloudy, rainy, stormy, humid. Each forecast record includes: date, temperature_min, temperature_max, humidity, precipitation_mm, uv_index.

---

### Feature 8: Language Support (TB-25, TB-26)

#### PR.8.1 — Language Selection
On first contact, the bot presents an inline keyboard with English 🇬🇧 and Burmese 🇲🇲. The user's language preference is stored persistently in `salebot/data/preferences.json` and survives bot restarts.

#### PR.8.2 — Auto-Detection
Incoming messages are scanned for Burmese Unicode characters (U+1000–U+109F). If detected and no language preference is set, the bot prompts language selection immediately.

#### PR.8.3 — Language Priority
Explicitly selected language always takes priority over auto-detection. The language preference is only cleared when the user runs `/clear`.

#### PR.8.4 — Bilingual System Prompts
The agent loads `prompts/system_prompt.md` (English) or `prompts/system_prompt_my.md` (Burmese) based on the stored preference. The agent responds in the user's selected language throughout the conversation.

---

### Feature 9: Human Operator Escalation (TB-40, TB-41)

#### PR.9.1 — Escalation Triggers
The agent escalates to a human operator when:
- A backend service is unreachable (connection error or timeout)
- A booking fails after payment has been confirmed
- The user explicitly asks to speak with a human
- The same issue fails 2–3 times consecutively
- Any payment processing error cannot be resolved

#### PR.9.2 — Escalation Process
1. Acknowledge the issue clearly and sincerely
2. Apologize without using technical jargon
3. Offer to connect with a human operator
4. Call `get_operator_contact` to display contact details

**Operator contact:**
- Phone / WhatsApp: +66 81 234 5678
- Email: support@travelbase.com
- Telegram: @travelbase_support
- Available 24/7

#### PR.9.3 — Support Page (TB-40)
The admin client includes a dedicated `/support` page displaying operator contact information and guidance for users who cannot resolve issues through the bot.

---

### Feature 10: Persistent Conversation Memory (TB-44)

#### PR.10.1 — In-Memory + JSON Persistence
Per-user conversation history is stored in memory and written to disk on every mutation (`salebot/data/conversations.json`, `salebot/data/preferences.json`). Data is reloaded from disk on bot startup — conversations and language preferences survive restarts.

#### PR.10.2 — Memory Limits
- Maximum 20 messages stored per user (oldest pruned automatically)
- Cleared on: `/clear` command, or after a booking is fully confirmed
- Stores: message history (role + content), language preference, pending payment reference

---

### Feature 11: Admin Dashboard (Client)

#### PR.11.1 — Authentication (TB-36, TB-37, TB-38)
The admin UI requires login with a username and password. The backend issues a JWT token on successful login (`POST /auth/login`). All protected routes check for a valid token stored in `localStorage`. Unauthenticated users are redirected to `/login`.

Default credentials (created on first server startup): `admin` / `admin123`.

#### PR.11.2 — Inventory Pages (TB-18–TB-21)
Dedicated pages for viewing and managing each inventory type:
- `/flights` — flight inventory with booking form
- `/hotels` — hotel inventory with booking form
- `/activities` — activity inventory with booking form
- `/transport` — transport options with booking form

#### PR.11.3 — Booking Packages View (TB-42)
`/bookings` displays all bookings grouped by `booking_reference` (package). Each package shows all associated items (flights, hotels, activities, transport, insurance), total item count, guest name, email, and creation timestamp.

#### PR.11.4 — Booking Statistics Dashboard (TB-43)
The home page shows aggregate statistics:
- Total bookings across all types
- Unique users (by email)
- Breakdown by type (flights / hotels / activities / transport)
- Payment totals and revenue

#### PR.11.5 — Playwright E2E Tests (TB-39)
Automated end-to-end tests cover: admin login, navigation between pages, inventory browsing, and protected route enforcement.

---

## Technical Stack

| Layer | Technology |
|-------|-----------|
| AI Model | Claude claude-haiku-4-5 (Anthropic) |
| Bot framework | python-telegram-bot 22.x |
| Agent loop | Custom async agentic loop (10 max iterations) |
| Backend | FastAPI + SQLModel + SQLite |
| Frontend | React 19, TypeScript, Tailwind CSS 4, Vite 8 |
| HTTP client (bot) | httpx (async) |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Testing (server/bot) | pytest + pytest-asyncio + respx |
| Testing (client) | Playwright |
| Linting | ruff (Python), ESLint (TypeScript) |
| Package manager | uv (Python), npm (Node) |

---

## Non-Functional Requirements

**NFR.1 — No invented data:** The agent must never fabricate prices, availability, hotel names, airline names, or any inventory detail. Every item shown to a user must originate from a tool result.

**NFR.2 — Graceful degradation:** If the backend is unreachable, the agent informs the user politely and offers operator contact — it does not crash or return a raw error.

**NFR.3 — All async:** All bot and agent code is async. No blocking I/O on the event loop.

**NFR.4 — Atomic booking:** No partial booking states. Either all items in a confirmed package are booked, or none are.

**NFR.5 — Payment before booking:** The system must never create bookings before `confirm_payment` returns success.

**NFR.6 — Test coverage:** Every story requires tests before implementation (TDD). All HTTP calls in tests are mocked — tests never call the real backend.

---

## Sprint History

| Sprint | Theme | Dates | Tickets | Status |
|--------|-------|-------|---------|--------|
| Sprint 1 | MCP Tools + Agent Core | Mar 16–21 | TB-01 → TB-07 | ✅ Done |
| Sprint 2 | Bot Integration + Fixes | Mar 22–27 | TB-08 → TB-13 | ✅ Done |
| Sprint 3 | Bookings + Language + UI | Mar 28 – Apr 3 | TB-14 → TB-27 | ✅ Done |
| Sprint 4 | Payments, Auth, Insurance, Visa, Weather | Apr 3+ | TB-29 → TB-38 | ✅ Done |
| Sprint 5 | Testing, Operator Support, Dashboard | Apr 3+ | TB-39 → TB-44 | ✅ Done |

### Sprint 1 — MCP Tools + Agent Core
Built and tested all 4 search tools, the Claude agentic loop, per-user memory, and the package builder formatter.

- **TB-01** Search Flights — filter by origin, destination, class; exclude zero-seat flights
- **TB-02** Search Hotels — filter by city, stars, max price; exclude zero-room hotels
- **TB-03** Search Activities — filter by city, category
- **TB-04** Search Transport — filter by origin, destination, type
- **TB-05** Agent Core — agentic tool-calling loop with 10-iteration cap
- **TB-06** Memory — per-user conversation history, capped at 20 messages
- **TB-07** Package Builder — format complete tour package as Telegram Markdown

### Sprint 2 — Bot Integration + Fixes
Wired the Telegram bot, wrote the full system prompt, validated end-to-end flow, and closed test and cleanup gaps from Sprint 1.

- **TB-08** System Prompt — full agent persona, rules, search strategy, response format
- **TB-09** Telegram Bot — `/start`, `/clear`, message handler, typing indicator
- **TB-10** End-to-End — full package search → presentation → tweak flow tested on Telegram
- **TB-11** Transport test coverage (deferred from TB-04)
- **TB-12** Package builder spec-compliance fix (dataclass interface correction)
- **TB-13** agent.py cleanup — removed dead code, fixed content block serialisation

### Sprint 3 — Bookings + Language + UI
Added complete booking system for all inventory types, Burmese language support, and admin UI booking forms.

- **TB-14** Flight Booking — `book_flight` tool + `POST /bookings/flights`
- **TB-15** Hotel Booking — `book_hotel` tool + `POST /bookings/hotels`
- **TB-16** Activity Booking — `book_activity` tool + `POST /bookings/activities`
- **TB-17** Transport Booking — `book_transport` tool + `POST /bookings/transport`
- **TB-18–21** Admin UI booking forms (flights, hotels, activities, transport)
- **TB-22** My Bookings page in admin UI
- **TB-23** Server + bot booking test coverage
- **TB-24** End-to-end test coverage
- **TB-25** Burmese language support — inline keyboard, bilingual system prompts
- **TB-26** Language selection priority fix — explicit selection overrides auto-detection
- **TB-27** All-or-nothing booking — atomic booking flow enforced in agent and system prompt

### Sprint 4 — Payments, Auth, Insurance, Visa, Weather
Added the full payment flow, admin authentication, and enrichment tools.

- **TB-29** Visa Requirements — `check_visa` tool + `GET /visa/{origin}/{destination}`
- **TB-30** Weather Forecast — `get_weather` tool + weather shown post-booking
- **TB-31** Travel Insurance — 3-tier plans, `add_insurance` tool, booking integration
- **TB-32** Flight Comparison — table format with duration, seat indicators, user selection by number
- **TB-33** Payment Backend — `Payment` model, `POST /payments`, `PUT /payments/{ref}/confirm`
- **TB-34** Payment QR display — agent shows QR block and PAY reference, waits for screenshot
- **TB-35** Payment confirmation + booking creation — `confirm_payment` gates all booking calls
- **TB-36** Admin auth backend — JWT login, hashed passwords, `/auth/login`, `/auth/me`
- **TB-37** Admin login page — login form, token storage, redirect on success
- **TB-38** Protected routes — all admin pages require valid JWT, redirect to `/login`

### Sprint 5 — Testing, Operator Support, Dashboard
Improved reliability, operator hand-off, dashboard insights, and persistent memory.

- **TB-39** Playwright E2E tests — login, navigation, inventory browsing, protected routes
- **TB-40** Emergency Contact page — `/support` with operator contact details
- **TB-41** Bot error fallback — agent calls `get_operator_contact` on unresolvable errors
- **TB-42** Booking Packages View — bookings grouped by reference in admin dashboard
- **TB-43** Booking Statistics Dashboard — total bookings, unique users, revenue breakdown
- **TB-44** Persistent Memory — conversation history and preferences persisted to JSON, survive restarts

---

## Journal

| Date | Entry |
|------|-------|
| 2026-03-16 | Project kickoff. Initial scope: general e-commerce AI shopping agent. |
| 2026-03-20 | Initial feature list and product requirements drafted. |
| 2026-03-21 | Pivoted from generic e-commerce to Southeast Asia travel agent. Domain chosen for richer booking workflow and end-to-end value. Sprint 1 complete: all 4 search tools, agent loop, memory, package builder. |
| 2026-03-27 | Sprint 2 complete. Telegram bot live. Full package flow tested end-to-end on Telegram. Corrective stories for test coverage and agent cleanup closed. |
| 2026-04-03 | Sprint 3 complete. Full booking system live (flights, hotels, activities, transport). Burmese language support added. All-or-nothing atomic booking flow enforced. Admin UI booking forms built. |
| 2026-04-03 | Sprint 4 complete. QR payment flow, admin JWT auth, visa checks, weather forecast, travel insurance, and flight comparison all shipped. |
| 2026-04-03 | Sprint 5 complete. Persistent memory, operator escalation, booking packages view, statistics dashboard, and Playwright E2E tests delivered. All 44 tickets closed. |
