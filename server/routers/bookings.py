import random
import string
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db import get_session
from models.activity import Activity
from models.booking import (
    ActivityBooking,
    ActivityBookingCreate,
    FlightBooking,
    FlightBookingCreate,
    HotelBooking,
    HotelBookingCreate,
    TransportBooking,
    TransportBookingCreate,
)
from models.flight import Flight
from models.hotel import Hotel
from models.transport import Transport

router = APIRouter(prefix="/bookings", tags=["bookings"])


def generate_booking_reference(session: Session) -> str:
    today = date.today().strftime("%Y%m%d")
    while True:
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        ref = f"TB-{today}-{suffix}"
        # Check uniqueness across all 4 booking tables
        if (
            session.exec(select(FlightBooking).where(FlightBooking.booking_reference == ref)).first()
            is None
            and session.exec(
                select(HotelBooking).where(HotelBooking.booking_reference == ref)
            ).first()
            is None
            and session.exec(
                select(ActivityBooking).where(ActivityBooking.booking_reference == ref)
            ).first()
            is None
            and session.exec(
                select(TransportBooking).where(TransportBooking.booking_reference == ref)
            ).first()
            is None
        ):
            return ref


# ---------------------------------------------------------------------------
# Flight bookings
# ---------------------------------------------------------------------------


@router.post("/flights", response_model=FlightBooking, status_code=201)
def create_flight_booking(
    booking: FlightBookingCreate, session: Session = Depends(get_session)
) -> FlightBooking:
    flight = session.get(Flight, booking.flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    if flight.seats_available < booking.seats_booked:
        raise HTTPException(
            status_code=422,
            detail=f"Not enough seats available. Requested: {booking.seats_booked}, Available: {flight.seats_available}",
        )
    flight.seats_available -= booking.seats_booked
    session.add(flight)
    ref = generate_booking_reference(session)
    db_booking = FlightBooking.model_validate(booking, update={"booking_reference": ref})
    session.add(db_booking)
    session.commit()
    session.refresh(db_booking)
    return db_booking


@router.get("/flights", response_model=List[FlightBooking])
def list_flight_bookings(
    email: Optional[str] = None, session: Session = Depends(get_session)
) -> List[FlightBooking]:
    query = select(FlightBooking)
    if email:
        query = query.where(FlightBooking.contact_email == email)
    return session.exec(query).all()


@router.get("/flights/{booking_id}", response_model=FlightBooking)
def get_flight_booking(
    booking_id: int, session: Session = Depends(get_session)
) -> FlightBooking:
    booking = session.get(FlightBooking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Flight booking not found")
    return booking


# ---------------------------------------------------------------------------
# Hotel bookings
# ---------------------------------------------------------------------------


@router.post("/hotels", response_model=HotelBooking, status_code=201)
def create_hotel_booking(
    booking: HotelBookingCreate, session: Session = Depends(get_session)
) -> HotelBooking:
    hotel = session.get(Hotel, booking.hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    if hotel.rooms_available < booking.guests:
        raise HTTPException(
            status_code=422,
            detail=f"Not enough rooms available. Requested: {booking.guests}, Available: {hotel.rooms_available}",
        )
    hotel.rooms_available -= booking.guests
    session.add(hotel)
    ref = generate_booking_reference(session)
    db_booking = HotelBooking.model_validate(booking, update={"booking_reference": ref})
    session.add(db_booking)
    session.commit()
    session.refresh(db_booking)
    return db_booking


@router.get("/hotels", response_model=List[HotelBooking])
def list_hotel_bookings(
    email: Optional[str] = None, session: Session = Depends(get_session)
) -> List[HotelBooking]:
    query = select(HotelBooking)
    if email:
        query = query.where(HotelBooking.contact_email == email)
    return session.exec(query).all()


@router.get("/hotels/{booking_id}", response_model=HotelBooking)
def get_hotel_booking(
    booking_id: int, session: Session = Depends(get_session)
) -> HotelBooking:
    booking = session.get(HotelBooking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Hotel booking not found")
    return booking


# ---------------------------------------------------------------------------
# Activity bookings
# ---------------------------------------------------------------------------


@router.post("/activities", response_model=ActivityBooking, status_code=201)
def create_activity_booking(
    booking: ActivityBookingCreate, session: Session = Depends(get_session)
) -> ActivityBooking:
    activity = session.get(Activity, booking.activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    ref = generate_booking_reference(session)
    db_booking = ActivityBooking.model_validate(booking, update={"booking_reference": ref})
    session.add(db_booking)
    session.commit()
    session.refresh(db_booking)
    return db_booking


@router.get("/activities", response_model=List[ActivityBooking])
def list_activity_bookings(
    email: Optional[str] = None, session: Session = Depends(get_session)
) -> List[ActivityBooking]:
    query = select(ActivityBooking)
    if email:
        query = query.where(ActivityBooking.contact_email == email)
    return session.exec(query).all()


@router.get("/activities/{booking_id}", response_model=ActivityBooking)
def get_activity_booking(
    booking_id: int, session: Session = Depends(get_session)
) -> ActivityBooking:
    booking = session.get(ActivityBooking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Activity booking not found")
    return booking


# ---------------------------------------------------------------------------
# Transport bookings
# ---------------------------------------------------------------------------


@router.post("/transport", response_model=TransportBooking, status_code=201)
def create_transport_booking(
    booking: TransportBookingCreate, session: Session = Depends(get_session)
) -> TransportBooking:
    transport = session.get(Transport, booking.transport_id)
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    if transport.capacity < booking.passengers:
        raise HTTPException(
            status_code=422,
            detail=f"Not enough capacity available. Requested: {booking.passengers}, Available: {transport.capacity}",
        )
    transport.capacity -= booking.passengers
    session.add(transport)
    ref = generate_booking_reference(session)
    db_booking = TransportBooking.model_validate(booking, update={"booking_reference": ref})
    session.add(db_booking)
    session.commit()
    session.refresh(db_booking)
    return db_booking


@router.get("/transport", response_model=List[TransportBooking])
def list_transport_bookings(
    email: Optional[str] = None, session: Session = Depends(get_session)
) -> List[TransportBooking]:
    query = select(TransportBooking)
    if email:
        query = query.where(TransportBooking.contact_email == email)
    return session.exec(query).all()


@router.get("/transport/{booking_id}", response_model=TransportBooking)
def get_transport_booking(
    booking_id: int, session: Session = Depends(get_session)
) -> TransportBooking:
    booking = session.get(TransportBooking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Transport booking not found")
    return booking
