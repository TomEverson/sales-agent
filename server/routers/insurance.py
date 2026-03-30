from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from models.insurance import (
    InsurancePlan,
    InsuranceBooking,
    InsuranceBookingCreate,
)
from db import engine

router = APIRouter(prefix="/insurance", tags=["insurance"])


def get_session():
    return Session(engine)


@router.get("", response_model=list[InsurancePlan])
def list_insurance_plans():
    with get_session() as session:
        plans = session.exec(select(InsurancePlan).where(InsurancePlan.is_active)).all()
        return list(plans)


@router.get("/{plan_id}", response_model=InsurancePlan)
def get_insurance_plan(plan_id: int):
    with get_session() as session:
        plan = session.get(InsurancePlan, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Insurance plan not found")
        return plan


@router.post("/book", response_model=InsuranceBooking)
def book_insurance(data: InsuranceBookingCreate):
    with get_session() as session:
        plan = session.get(InsurancePlan, data.plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Insurance plan not found")

        import random
        import string

        ref = f"INS-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

        booking = InsuranceBooking(
            plan_id=data.plan_id,
            traveler_name=data.traveler_name,
            contact_email=data.contact_email,
            booking_reference=ref,
            status="confirmed",
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking
