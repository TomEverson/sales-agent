from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional

from models.visa import VisaRequirement, VisaRequirementCreate
from db import engine

router = APIRouter(prefix="/visa", tags=["visa"])


def get_session():
    return Session(engine)


@router.get("", response_model=list[VisaRequirement])
def get_visa_requirements(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
):
    with get_session() as session:
        query = select(VisaRequirement)

        if origin:
            query = query.where(VisaRequirement.origin_country.contains(origin))
        if destination:
            query = query.where(
                VisaRequirement.destination_country.contains(destination)
            )

        results = session.exec(query).all()
        return list(results)


@router.post("", response_model=VisaRequirement)
def create_visa_requirement(data: VisaRequirementCreate):
    with get_session() as session:
        existing = session.exec(
            select(VisaRequirement).where(
                VisaRequirement.origin_country == data.origin_country,
                VisaRequirement.destination_country == data.destination_country,
            )
        ).first()

        if existing:
            existing.visa_required = data.visa_required
            existing.visa_on_arrival = data.visa_on_arrival
            existing.visa_eta = data.visa_eta
            existing.max_stay_days = data.max_stay_days
            existing.notes = data.notes
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing

        visa = VisaRequirement(
            origin_country=data.origin_country,
            destination_country=data.destination_country,
            visa_required=data.visa_required,
            visa_on_arrival=data.visa_on_arrival,
            visa_eta=data.visa_eta,
            max_stay_days=data.max_stay_days,
            notes=data.notes,
        )
        session.add(visa)
        session.commit()
        session.refresh(visa)
        return visa


@router.get("/{origin}/{destination}", response_model=VisaRequirement)
def get_specific_visa(origin: str, destination: str):
    with get_session() as session:
        result = session.exec(
            select(VisaRequirement).where(
                VisaRequirement.origin_country.contains(origin),
                VisaRequirement.destination_country.contains(destination),
            )
        ).first()

        if not result:
            raise HTTPException(status_code=404, detail="Visa requirement not found")

        return result
