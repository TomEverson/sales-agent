from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models.hotel import Hotel, HotelCreate

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get("", response_model=List[Hotel])
def list_hotels(
    city: Optional[str] = None,
    stars: Optional[int] = None,
    max_price: Optional[float] = None,
    session: Session = Depends(get_session),
) -> List[Hotel]:
    query = select(Hotel)
    if city:
        query = query.where(Hotel.city == city)
    if stars is not None:
        query = query.where(Hotel.stars == stars)
    if max_price is not None:
        query = query.where(Hotel.price_per_night <= max_price)
    return session.exec(query).all()


@router.get("/{hotel_id}", response_model=Hotel)
def get_hotel(hotel_id: int, session: Session = Depends(get_session)) -> Hotel:
    hotel = session.get(Hotel, hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel


@router.post("", response_model=Hotel, status_code=201)
def create_hotel(hotel: HotelCreate, session: Session = Depends(get_session)) -> Hotel:
    db_hotel = Hotel.model_validate(hotel)
    session.add(db_hotel)
    session.commit()
    session.refresh(db_hotel)
    return db_hotel


@router.put("/{hotel_id}", response_model=Hotel)
def update_hotel(
    hotel_id: int, hotel: HotelCreate, session: Session = Depends(get_session)
) -> Hotel:
    db_hotel = session.get(Hotel, hotel_id)
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    hotel_data = hotel.model_dump()
    for key, value in hotel_data.items():
        setattr(db_hotel, key, value)
    session.add(db_hotel)
    session.commit()
    session.refresh(db_hotel)
    return db_hotel


@router.delete("/{hotel_id}", status_code=204)
def delete_hotel(hotel_id: int, session: Session = Depends(get_session)) -> None:
    db_hotel = session.get(Hotel, hotel_id)
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    session.delete(db_hotel)
    session.commit()
