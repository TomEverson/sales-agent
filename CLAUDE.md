# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered travel sales agent ("Travelbase Salebot") with three components:
- **salebot/**: Telegram bot + Claude agentic loop
- **server/**: FastAPI backend with SQLite inventory database
- **client/**: React frontend (admin/browse UI)

## Development Commands

### Server (FastAPI)
```bash
cd server
uv run uvicorn main:app --reload   # Start on http://localhost:8000
uv run python seed.py              # Seed SQLite database with sample data
ruff check .                       # Lint Python
```

### Bot (Telegram + Claude agent)
```bash
cd salebot
uv run python bot.py               # Start Telegram bot (requires .env)
```

### Client (React)
```bash
cd client
npm run dev      # Start Vite dev server on http://localhost:5173
npm run build
npm run lint
```

## Architecture

**Data flow:**
1. User messages Telegram bot → `salebot/bot.py`
2. `bot.py` calls `agent.handle_message(user_id, text)`
3. `agent.py` runs agentic loop: calls Claude with tools until no more tool_use blocks
4. Tools in `mcp_tools.py` make HTTP calls to FastAPI at `http://localhost:8000`
5. FastAPI queries SQLite (`travel.db`) and returns results
6. Final Claude text response is sent back to Telegram

**Conversation memory** (`salebot/memory.py`): in-memory dict keyed by Telegram user_id, capped at 20 messages per user.

**Tool definitions** (`salebot/mcp_tools.py`): four tools — `search_flights`, `search_hotels`, `search_activities`, `search_transport`. Each maps to a GET endpoint with optional query params; out-of-stock items are filtered before returning results.

**Backend models** (`server/models/`): SQLModel classes that serve as both ORM models and Pydantic schemas. Each router (`server/routers/`) provides CRUD endpoints.

## Development Rules

From `rules/base.md`:
- Spec-driven: read the relevant `rules/*.md` file before writing code for that component
- Implement one feature at a time
- Python linting: `ruff check .`

From `rules/bot.md`:
- All bot/agent code must be async
- Never invent prices or inventory — only return data from the backend
- If the backend is unreachable, inform the user gracefully

From `rules/server.md`:
- Use `uv` for Python environment management
- Use SQLModel for ORM + schema validation

## Environment Variables

**salebot/.env:**
```
TELEGRAM_BOT_TOKEN=...
ANTHROPIC_API_KEY=...
```

**server/.env:** (currently empty, reserved for future config)

## Key Files

| File | Purpose |
|------|---------|
| `salebot/agent.py` | Agentic loop: Claude API calls, tool dispatch, history management |
| `salebot/mcp_tools.py` | Tool schemas for Claude + HTTP calls to backend |
| `salebot/prompts/system_prompt.md` | Agent persona and decision-making instructions |
| `salebot/package_builder.py` | Formats complete tour packages as Telegram markdown |
| `server/main.py` | FastAPI app setup, CORS, router registration |
| `server/seed.py` | Populates `travel.db` with sample flights/hotels/activities/transport |
| `docs/fr-1.md` | Feature requests and specs |
