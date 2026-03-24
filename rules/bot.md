Build a Telegram bot sales agent for a travel website called Travelbase.

## Stack
- python-telegram-bot (async)
- Anthropic Claude API (claude-sonnet-4-5 model)
- MCP tools that call the FastAPI backend at http://localhost:8000
- uv for environment management

## Project structure
salebot/
├── bot.py                  # Telegram bot entry point
├── agent.py                # Claude agent logic + tool calling loop
├── mcp_tools.py            # MCP tool definitions + HTTP calls to FastAPI
├── memory.py               # Per-user conversation history
├── package_builder.py      # Assembles final tour package from tool results
├── prompts/
│   └── system_prompt.md    # Agent personality and instructions
├── pyproject.toml
└── .env

## Environment Setup
- Use uv for environment management
- Dependencies: uv add anthropic python-telegram-bot python-dotenv httpx
- Run with: uv run python bot.py
- .env variables needed:
  TELEGRAM_BOT_TOKEN=
  ANTHROPIC_API_KEY=

## MCP Tools (mcp_tools.py)

Define the following tools that the Claude agent can call.
Each tool makes an HTTP GET request to the FastAPI backend.

### search_flights
- Params: origin, destination, class_type (optional)
- Calls: GET http://localhost:8000/flights
- Returns: list of flights with id, airline, departure_time, arrival_time, price, seats_available, class_type

### search_hotels
- Params: city, stars (optional), max_price (optional)
- Calls: GET http://localhost:8000/hotels
- Returns: list of hotels with id, name, stars, price_per_night, amenities, rooms_available

### search_activities
- Params: city, category (optional)
- Calls: GET http://localhost:8000/activities
- Returns: list of activities with id, name, category, duration_hours, price, availability

### search_transport
- Params: origin, destination, type (optional)
- Calls: GET http://localhost:8000/transport
- Returns: list of transport options with id, type, departure_time, arrival_time, price, capacity

Each tool should be defined in Anthropic tool format:
{
  "name": "search_flights",
  "description": "...",
  "input_schema": { "type": "object", "properties": { ... } }
}

## Agent Logic (agent.py)

Implement an agentic tool-calling loop:

1. Receive user message + conversation history
2. Call Claude API with system prompt + history + tools
3. If Claude returns tool_use blocks → execute the tools → append results → call Claude again
4. Repeat until Claude returns a final text response with no tool calls
5. Return the final text response

The loop must handle multiple sequential tool calls in one turn
(e.g. Claude calls search_flights, then search_hotels, then search_activities, then search_transport before responding).

## Memory (memory.py)

- Store conversation history per Telegram user_id in a Python dict
- Each entry: { "role": "user" | "assistant", "content": "..." }
- Include tool use and tool result messages in history so Claude has full context
- Cap history at 20 messages per user to avoid token overflow
- Expose: get_history(user_id), append_message(user_id, message), clear_history(user_id)

## Package Builder (package_builder.py)

After Claude selects items from the tools, format the final tour package as a clean Telegram message:

🗺 *Your Tour Package*

✈️ *Flight*
  Bangkok → Singapore | AirAsia | Economy
  Departure: Sat 08:00 → Arrival: Sat 09:30
  Price: $85

🏨 *Hotel*
  The Singapore Suites | ⭐⭐⭐⭐
  Price: $120/night × 2 nights = $240

🎯 *Activities*
  1. Gardens by the Bay Tour — $25 (3hrs)
  2. Singapore Food Walk — $35 (2hrs)

🚗 *Transport*
  Airport → Hotel | Car | $30

💰 *Total Estimate: $415*
  (Budget remaining: $585)

Format using Telegram markdown.
Always show total cost and remaining budget.

## system_prompt.md

Write the full system prompt for the agent with these rules:

- You are Travelbase Assistant, a friendly travel sales agent
- Your job is to build the best possible tour package within the user's budget
- Always extract: destination, travel dates or weekend indicator, budget, number of travelers (default 1 if not mentioned)
- Use tools to search real inventory — never invent prices or availability
- Optimize for: budget fit first, then quality (stars, ratings, variety of activities)
- Always include at least: 1 flight, 1 hotel, 1 activity — transport is optional if not needed
- After presenting a package, invite the user to tweak it:
  e.g. "Would you like a nicer hotel? More activities? A different flight time?"
- When the user requests a change, search again with updated constraints and rebuild the package
- If budget is too tight for a full package, tell the user honestly and suggest what is possible
- Keep responses warm, concise, and helpful — not overly formal
- Never recommend something that is out of stock (seats_available = 0, rooms_available = 0)

## bot.py

- Use python-telegram-bot in async mode
- Handle /start → greeting message + instructions
- Handle /clear → clear user's conversation history
- Handle all text messages → pass to agent.py with user_id and message
- Show "typing..." action while agent is processing
- Send the agent response back to the user

## Rules
- Never hardcode prices or inventory — always use tool results
- Multi-turn: the agent remembers the full conversation and can refine the package across messages
- If Claude asks a clarifying question (e.g. "How many nights?"), that is valid — answer it and continue
- All tool calls must be async (use httpx.AsyncClient)
- Graceful error handling: if FastAPI is unreachable, tell the user to try again later
- uv run python bot.py to start