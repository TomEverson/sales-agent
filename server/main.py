from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import create_db_and_tables
from routers import flights, hotels, activities, transport, bookings

app = FastAPI(title="Travel Inventory API", redirect_slashes=False)

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


app.include_router(flights.router)
app.include_router(hotels.router)
app.include_router(activities.router)
app.include_router(transport.router)
app.include_router(bookings.router)
