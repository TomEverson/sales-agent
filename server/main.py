from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import create_db_and_tables
from routers import (
    flights,
    hotels,
    activities,
    transport,
    bookings,
    visa,
    weather,
    insurance,
    payments,
    auth,
)

app = FastAPI(title="Travel Inventory API", redirect_slashes=False)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
    from routers.auth import ensure_admin_user
    from sqlmodel import Session
    from db import engine

    with Session(engine) as session:
        ensure_admin_user(session)


app.include_router(flights.router)
app.include_router(hotels.router)
app.include_router(activities.router)
app.include_router(transport.router)
app.include_router(bookings.router)
app.include_router(visa.router)
app.include_router(weather.router)
app.include_router(insurance.router)
app.include_router(payments.router)
app.include_router(auth.router)
