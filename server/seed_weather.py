from sqlmodel import Session, select
from db import create_db_and_tables, engine
from models.weather import WeatherForecast

from datetime import datetime, timedelta

CITIES = {
    "Bangkok": {"lat": 13.75, "lon": 100.52, "season": "hot_dry"},
    "Singapore": {"lat": 1.35, "lon": 103.82, "season": "tropical"},
    "Kuala Lumpur": {"lat": 3.14, "lon": 101.69, "season": "tropical"},
    "Bali": {"lat": -8.34, "lon": 115.09, "season": "tropical"},
    "Phuket": {"lat": 7.89, "lon": 98.40, "season": "tropical"},
    "Chiang Mai": {"lat": 18.79, "lon": 98.98, "season": "hot_dry"},
    "Hoi An": {"lat": 15.88, "lon": 108.34, "season": "hot_dry"},
    "Hanoi": {"lat": 21.03, "lon": 105.85, "season": "warm_humid"},
    "Ho Chi Minh City": {"lat": 10.82, "lon": 106.63, "season": "hot_dry"},
    "Yangon": {"lat": 16.87, "lon": 96.19, "season": "hot_dry"},
    "Bagan": {"lat": 21.17, "lon": 94.86, "season": "hot_dry"},
    "Mandalay": {"lat": 21.97, "lon": 96.08, "season": "hot_dry"},
    "Inle Lake": {"lat": 20.54, "lon": 96.92, "season": "warm_humid"},
    "Tokyo": {"lat": 35.68, "lon": 139.69, "season": "mild_spring"},
    "Osaka": {"lat": 34.69, "lon": 135.50, "season": "mild_spring"},
    "Seoul": {"lat": 37.57, "lon": 126.98, "season": "mild_spring"},
    "Busan": {"lat": 35.18, "lon": 129.08, "season": "mild_spring"},
    "Beijing": {"lat": 39.90, "lon": 116.41, "season": "warm_spring"},
    "Shanghai": {"lat": 31.23, "lon": 121.47, "season": "warm_spring"},
    "Taipei": {"lat": 25.05, "lon": 121.56, "season": "warm_humid"},
}


def generate_weather(
    city: str, config: dict, start_date: datetime, days: int = 30
) -> list[dict]:
    season = config["season"]
    forecasts = []

    conditions_pool = ["sunny", "partly_cloudy", "cloudy", "rainy"]
    if season in ["hot_dry", "tropical"]:
        conditions_pool += ["sunny", "sunny", "partly_cloudy"]
        base_temp_min = 25
        base_temp_max = 34
    elif season == "warm_spring":
        conditions_pool += ["partly_cloudy", "cloudy"]
        base_temp_min = 15
        base_temp_max = 25
    elif season == "mild_spring":
        conditions_pool += ["partly_cloudy", "cloudy"]
        base_temp_min = 12
        base_temp_max = 22
    else:
        base_temp_min = 22
        base_temp_max = 30

    import random

    random.seed(hash(city) % 2**32)

    for i in range(days):
        date = start_date + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        day_offset = i % 7
        condition = conditions_pool[day_offset % len(conditions_pool)]

        if condition == "rainy":
            temp_min = base_temp_min - 2
            temp_max = base_temp_max - 3
            humidity = random.randint(80, 95)
            precipitation = random.uniform(5, 20)
        elif condition == "cloudy":
            temp_min = base_temp_min - 1
            temp_max = base_temp_max - 2
            humidity = random.randint(60, 75)
            precipitation = random.uniform(0, 2)
        elif condition == "partly_cloudy":
            temp_min = base_temp_min
            temp_max = base_temp_max
            humidity = random.randint(50, 70)
            precipitation = random.uniform(0, 1)
        else:
            temp_min = base_temp_min + 1
            temp_max = base_temp_max + 2
            humidity = random.randint(40, 60)
            precipitation = 0

        uv_index = (
            random.randint(5, 10) if condition == "sunny" else random.randint(2, 7)
        )
        wind_speed = random.randint(5, 25)

        forecasts.append(
            {
                "city": city,
                "date": date_str,
                "temperature_min": round(temp_min, 1),
                "temperature_max": round(temp_max, 1),
                "condition": condition,
                "humidity": humidity,
                "precipitation_mm": round(precipitation, 1),
                "uv_index": uv_index,
                "wind_speed_kmh": wind_speed,
            }
        )

    return forecasts


def seed_weather():
    create_db_and_tables()

    with Session(engine) as session:
        for weather in session.exec(select(WeatherForecast)).all():
            session.delete(weather)
        session.commit()

        start_date = datetime(2026, 4, 1)
        all_forecasts = []

        for city, config in CITIES.items():
            forecasts = generate_weather(city, config, start_date, 30)
            all_forecasts.extend(forecasts)

        weather_objects = [WeatherForecast(**f) for f in all_forecasts]
        session.add_all(weather_objects)
        session.commit()

        count = len(session.exec(select(WeatherForecast)).all())
        print(f"Seeded: {count} weather forecasts for {len(CITIES)} cities")


if __name__ == "__main__":
    seed_weather()
