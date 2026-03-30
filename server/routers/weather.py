from fastapi import APIRouter, Query
from sqlmodel import Session, select
from typing import Optional

from models.weather import WeatherForecast, WeatherForecastCreate
from db import engine

router = APIRouter(prefix="/weather", tags=["weather"])


def get_session():
    return Session(engine)


@router.get("/{city}")
def get_weather(
    city: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    with get_session() as session:
        query = select(WeatherForecast).where(WeatherForecast.city.ilike(f"%{city}%"))

        if start_date:
            query = query.where(WeatherForecast.date >= start_date)
        if end_date:
            query = query.where(WeatherForecast.date <= end_date)

        results = session.exec(query.order_by(WeatherForecast.date)).all()
        return {
            "city": city,
            "forecasts": [
                {
                    "date": w.date,
                    "temperature_min": w.temperature_min,
                    "temperature_max": w.temperature_max,
                    "condition": w.condition,
                    "humidity": w.humidity,
                    "precipitation_mm": w.precipitation_mm,
                    "uv_index": w.uv_index,
                    "wind_speed_kmh": w.wind_speed_kmh,
                }
                for w in results
            ],
        }


@router.post("", response_model=WeatherForecast)
def create_weather(data: WeatherForecastCreate):
    with get_session() as session:
        weather = WeatherForecast(
            city=data.city,
            date=data.date,
            temperature_min=data.temperature_min,
            temperature_max=data.temperature_max,
            condition=data.condition,
            humidity=data.humidity,
            precipitation_mm=data.precipitation_mm,
            uv_index=data.uv_index,
            wind_speed_kmh=data.wind_speed_kmh,
        )
        session.add(weather)
        session.commit()
        session.refresh(weather)
        return weather
