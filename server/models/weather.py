from sqlmodel import SQLModel, Field


class WeatherForecast(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    city: str
    date: str
    temperature_min: float
    temperature_max: float
    condition: str
    humidity: int
    precipitation_mm: float
    uv_index: int
    wind_speed_kmh: float


class WeatherForecastCreate(SQLModel):
    city: str
    date: str
    temperature_min: float
    temperature_max: float
    condition: str
    humidity: int
    precipitation_mm: float
    uv_index: int
    wind_speed_kmh: float
