---
ticket: TB-30
type: feat
title: Weather Forecast for Booked Packages
sprint: sprint-4
status: todo
component: salebot, server
depends_on: TB-14, TB-15, TB-16, TB-17
---

# TB-30: Weather Forecast for Booked Packages

## Context

After a user books a travel package, they should receive relevant information to help them prepare for their trip. Weather is one of the most important factors for travel planning. This feature will provide weather forecasts for the destination during the user's travel dates.

Read `rules/base.md` before starting.

---

## Goal

After a successful booking, automatically send the user a weather forecast for their destination covering their travel dates. This helps them pack appropriately and plan activities.

Example usage:
- After booking a Bangkok trip for April 10-15 → show weather forecast for Bangkok during those dates
- After booking a Tokyo trip → show expected weather conditions (cherry blossom season, etc.)

---

## Files to create / modify

| File | Action |
|------|--------|
| `server/routers/weather.py` | create — new FastAPI router with weather data |
| `server/models/weather.py` | create — Weather forecast model |
| `server/seed_weather.py` | create — seed weather data for major cities |
| `salebot/mcp_tools.py` | create — `get_weather` tool |
| `salebot/prompts/system_prompt.md` | modify — add weather notification in booking flow |
| `salebot/prompts/system_prompt_my.md` | modify — add weather notification (Burmese) |

---

## What to build

### 1. Weather Model — `server/models/weather.py`

```python
from sqlmodel import SQLModel, Field

class WeatherForecast(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    city: str                           # e.g., "Bangkok", "Tokyo"
    date: str                           # e.g., "2026-04-10"
    temperature_min: float              # Celsius
    temperature_max: float             # Celsius
    condition: str                     # e.g., "sunny", "rainy", "cloudy", "stormy"
    humidity: int                      # Percentage 0-100
    precipitation_mm: float            # Rainfall in mm
    uv_index: int                      # UV index 1-11+
    wind_speed_kmh: float              # Wind speed
```

---

### 2. Weather Router — `server/routers/weather.py`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/weather/{city}` | Get weather for a city (all available dates) |
| GET | `/weather/{city}?start_date=X&end_date=Y` | Get weather for date range |

**Response example:**
```json
{
  "city": "Tokyo",
  "forecasts": [
    {
      "date": "2026-04-10",
      "temperature_min": 12,
      "temperature_max": 22,
      "condition": "partly_cloudy",
      "humidity": 65,
      "precipitation_mm": 0.5,
      "uv_index": 5,
      "wind_speed_kmh": 15
    }
  ]
}
```

---

### 3. MCP Tool — `salebot/mcp_tools.py`

Add `get_weather` tool:

```python
get_weather_tool = {
    "name": "get_weather",
    "description": "Get weather forecast for a destination city. Pass city name and optionally start_date/end_date (YYYY-MM-DD format) to filter the forecast period.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The destination city name (e.g., Bangkok, Tokyo, Singapore)"
            },
            "start_date": {
                "type": "string",
                "description": "Start date of the forecast period in YYYY-MM-DD format (optional)"
            },
            "end_date": {
                "type": "string",
                "description": "End date of the forecast period in YYYY-MM-DD format (optional)"
            }
        },
        "required": ["city"]
    }
}
```

---

### 4. System Prompt Update

Add to Section 9 (All-or-Nothing Package Booking Flow):

**After Step 5 (Handle success):**

Add new step:

### Step 7: Send Weather Forecast
After displaying booking confirmations, automatically get the weather for the destination:
1. Extract the destination city and travel dates from the package
2. Call `get_weather` tool with city and date range
3. Display a brief weather summary to help the user prepare:
   ```
   🌤️ Weather Forecast for Bangkok (Apr 10-15):
   
   Apr 10 | ☀️ Sunny | 28°C - 35°C | UV: High
   Apr 11 | ⛅ Partly Cloudy | 27°C - 34°C
   Apr 12 | 🌧️ Chance of rain | 26°C - 33°C | 80% chance
   
   Tips: Bring light clothing, sunscreen, and an umbrella!
   ```

4. End with preparation tips based on weather conditions

---

### 5. Seed Weather Data — `server/seed_weather.py`

Seed weather data for all cities in the database:
- Bangkok, Singapore, Kuala Lumpur, Bali, Phuket, Chiang Mai, Hoi An, Yangon, Bagan, Mandalay, Inle Lake, Hanoi, Ho Chi Minh City
- Tokyo, Osaka, Seoul, Busan, Beijing, Shanghai, Taipei

Generate realistic weather based on:
- Season (April = hot/dry in SEA, mild in East Asia)
- Typical patterns (monsoon season, etc.)
- 30 days of forecast data per city

---

## Weather Conditions to Include

| Condition | Icon | Description |
|-----------|------|-------------|
| sunny | ☀️ | Clear skies |
| partly_cloudy | ⛅ | Some clouds |
| cloudy | ☁️ | Overcast |
| rainy | 🌧️ | Rain |
| stormy | ⛈️ | Thunderstorms |
| humid | 💧 | High humidity warning |

---

## Acceptance Criteria

- [ ] `GET /weather/{city}` returns weather forecasts for a city
- [ ] Agent calls `get_weather` after successful booking
- [ ] Weather summary is displayed with travel dates
- [ ] Preparation tips are included based on weather
- [ ] Weather data seeded for all cities in database
- [ ] `uv run ruff check .` passes

---

## Tests to write

- `server/routers/test_weather.py` — test weather endpoints
- `salebot/tests/test_mcp_tools.py` — test get_weather tool

---

## Definition of Done

- [ ] All acceptance criteria checked off
- [ ] `uv run pytest tests/ -v` passes
- [ ] `uv run ruff check .` passes
- [ ] Manual test: book a package → receive weather forecast for destination