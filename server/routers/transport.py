from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models.transport import Transport, TransportCreate

router = APIRouter(prefix="/transport", tags=["transport"])


@router.get("", response_model=List[Transport])
def list_transport(
    type: Optional[str] = None,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    session: Session = Depends(get_session),
) -> List[Transport]:
    query = select(Transport)
    if type:
        query = query.where(Transport.type == type)
    if origin:
        query = query.where(Transport.origin == origin)
    if destination:
        query = query.where(Transport.destination == destination)
    return session.exec(query).all()


@router.get("/{transport_id}", response_model=Transport)
def get_transport(transport_id: int, session: Session = Depends(get_session)) -> Transport:
    transport = session.get(Transport, transport_id)
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    return transport


@router.post("", response_model=Transport, status_code=201)
def create_transport(transport: TransportCreate, session: Session = Depends(get_session)) -> Transport:
    db_transport = Transport.model_validate(transport)
    session.add(db_transport)
    session.commit()
    session.refresh(db_transport)
    return db_transport


@router.put("/{transport_id}", response_model=Transport)
def update_transport(
    transport_id: int, transport: TransportCreate, session: Session = Depends(get_session)
) -> Transport:
    db_transport = session.get(Transport, transport_id)
    if not db_transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    transport_data = transport.model_dump()
    for key, value in transport_data.items():
        setattr(db_transport, key, value)
    session.add(db_transport)
    session.commit()
    session.refresh(db_transport)
    return db_transport


@router.delete("/{transport_id}", status_code=204)
def delete_transport(transport_id: int, session: Session = Depends(get_session)) -> None:
    db_transport = session.get(Transport, transport_id)
    if not db_transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    session.delete(db_transport)
    session.commit()
