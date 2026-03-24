from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models.flight import Flight, FlightCreate

router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("", response_model=List[Flight])
def list_flights(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    class_type: Optional[str] = None,
    session: Session = Depends(get_session),
) -> List[Flight]:
    query = select(Flight)
    if origin:
        query = query.where(Flight.origin == origin)
    if destination:
        query = query.where(Flight.destination == destination)
    if class_type:
        query = query.where(Flight.class_type == class_type)
    return session.exec(query).all()


@router.get("/{flight_id}", response_model=Flight)
def get_flight(flight_id: int, session: Session = Depends(get_session)) -> Flight:
    flight = session.get(Flight, flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight


@router.post("", response_model=Flight, status_code=201)
def create_flight(flight: FlightCreate, session: Session = Depends(get_session)) -> Flight:
    db_flight = Flight.model_validate(flight)
    session.add(db_flight)
    session.commit()
    session.refresh(db_flight)
    return db_flight


@router.put("/{flight_id}", response_model=Flight)
def update_flight(
    flight_id: int, flight: FlightCreate, session: Session = Depends(get_session)
) -> Flight:
    db_flight = session.get(Flight, flight_id)
    if not db_flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    flight_data = flight.model_dump()
    for key, value in flight_data.items():
        setattr(db_flight, key, value)
    session.add(db_flight)
    session.commit()
    session.refresh(db_flight)
    return db_flight


@router.delete("/{flight_id}", status_code=204)
def delete_flight(flight_id: int, session: Session = Depends(get_session)) -> None:
    db_flight = session.get(Flight, flight_id)
    if not db_flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    session.delete(db_flight)
    session.commit()
