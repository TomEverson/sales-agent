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
    BookingPackage,
    BookingPackageItem,
    BookingStats,
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
            session.exec(
                select(FlightBooking).where(FlightBooking.booking_reference == ref)
            ).first()
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
                select(TransportBooking).where(
                    TransportBooking.booking_reference == ref
                )
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
    db_booking = FlightBooking.model_validate(
        booking, update={"booking_reference": ref}
    )
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
    db_booking = ActivityBooking.model_validate(
        booking, update={"booking_reference": ref}
    )
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
    db_booking = TransportBooking.model_validate(
        booking, update={"booking_reference": ref}
    )
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


# ---------------------------------------------------------------------------
# Package grouping & statistics
# ---------------------------------------------------------------------------


@router.get("/packages", response_model=list[BookingPackage])
def list_booking_packages(
    session: Session = Depends(get_session),
) -> list[BookingPackage]:
    """Return all bookings grouped by booking_reference as packages."""
    all_refs: set[str] = set()

    # Collect all unique booking references
    for cls, kind in [
        (FlightBooking, "flight"),
        (HotelBooking, "hotel"),
        (ActivityBooking, "activity"),
        (TransportBooking, "transport"),
    ]:
        refs = session.exec(select(cls.booking_reference)).all()
        all_refs.update(refs)

    packages: list[BookingPackage] = []
    for ref in sorted(all_refs):
        items: list[BookingPackageItem] = []
        earliest: str = ""

        # Flight bookings
        flight_rows = session.exec(
            select(FlightBooking).where(FlightBooking.booking_reference == ref)
        ).all()
        for row in flight_rows:
            created = row.created_at.isoformat() if row.created_at else ""
            if not earliest or created < earliest:
                earliest = created
                items.append(
                    BookingPackageItem(
                        kind="flight",
                        id=row.id or 0,
                        passenger_name=row.passenger_name,
                        contact_email=row.contact_email,
                        status=row.status,
                        created_at=row.created_at,
                        flight_id=row.flight_id,
                        seats_booked=row.seats_booked,
                    )
                )

        # Hotel bookings
        hotel_rows = session.exec(
            select(HotelBooking).where(HotelBooking.booking_reference == ref)
        ).all()
        for row in hotel_rows:
            created = row.created_at.isoformat() if row.created_at else ""
            if not earliest or created < earliest:
                earliest = created
                items.append(
                    BookingPackageItem(
                        kind="hotel",
                        id=row.id or 0,
                        passenger_name=row.guest_name,
                        contact_email=row.contact_email,
                        status=row.status,
                        created_at=row.created_at,
                        hotel_id=row.hotel_id,
                        guests=row.guests,
                        check_in_date=row.check_in_date,
                        check_out_date=row.check_out_date,
                    )
                )

        # Activity bookings
        activity_rows = session.exec(
            select(ActivityBooking).where(ActivityBooking.booking_reference == ref)
        ).all()
        for row in activity_rows:
            created = row.created_at.isoformat() if row.created_at else ""
            if not earliest or created < earliest:
                earliest = created
                items.append(
                    BookingPackageItem(
                        kind="activity",
                        id=row.id or 0,
                        passenger_name=row.participant_name,
                        contact_email=row.contact_email,
                        status=row.status,
                        created_at=row.created_at,
                        activity_id=row.activity_id,
                        participants=row.participants,
                        activity_date=row.activity_date,
                    )
                )

        # Transport bookings
        transport_rows = session.exec(
            select(TransportBooking).where(TransportBooking.booking_reference == ref)
        ).all()
        for row in transport_rows:
            created = row.created_at.isoformat() if row.created_at else ""
            if not earliest or created < earliest:
                earliest = created
            items.append(
                BookingPackageItem(
                    kind="transport",
                    id=row.id or 0,
                    passenger_name=row.passenger_name,
                    contact_email=row.contact_email,
                    status=row.status,
                    created_at=row.created_at,
                    transport_id=row.transport_id,
                    passengers=row.passengers,
                )
            )

        packages.append(
            BookingPackage(
                booking_reference=ref,
                items=items,
                total_items=len(items),
                created_at=earliest,
            )
        )

    # Sort by most recent first
    packages.sort(key=lambda p: p.created_at, reverse=True)
    return packages


@router.get("/stats", response_model=BookingStats)
def get_booking_stats(session: Session = Depends(get_session)) -> BookingStats:
    """Return aggregated booking statistics."""
    flight_count = len(session.exec(select(FlightBooking)).all())
    hotel_count = len(session.exec(select(HotelBooking)).all())
    activity_count = len(session.exec(select(ActivityBooking)).all())
    transport_count = len(session.exec(select(TransportBooking)).all())

    total = flight_count + hotel_count + activity_count + transport_count

    # Unique users
    emails: set[str] = set()
    for cls in [FlightBooking, HotelBooking, ActivityBooking, TransportBooking]:
        rows = session.exec(select(cls.contact_email)).all()
        emails.update(rows)

    return BookingStats(
        total_bookings=total,
        unique_users=len(emails),
        by_type={
            "flights": flight_count,
            "hotels": hotel_count,
            "activities": activity_count,
            "transport": transport_count,
        },
    )
