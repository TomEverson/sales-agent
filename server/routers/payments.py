import random
import string
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db import get_session
from models.payment import Payment, PaymentCreate, PaymentResponse

router = APIRouter(prefix="/payments", tags=["payments"])


def generate_payment_reference(session: Session) -> str:
    while True:
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        ref = f"PAY-{suffix}"
        if (
            session.exec(
                select(Payment).where(Payment.booking_reference == ref)
            ).first()
            is None
        ):
            return ref


@router.post("", response_model=PaymentResponse, status_code=201)
def create_payment(
    payment: PaymentCreate, session: Session = Depends(get_session)
) -> Payment:
    ref = generate_payment_reference(session)
    db_payment = Payment(
        booking_reference=ref,
        amount=payment.amount,
        status="pending",
        payment_method=payment.payment_method,
    )
    session.add(db_payment)
    session.commit()
    session.refresh(db_payment)
    return db_payment


@router.get("/{booking_reference}", response_model=PaymentResponse)
def get_payment(
    booking_reference: str, session: Session = Depends(get_session)
) -> Payment:
    payment = session.exec(
        select(Payment).where(Payment.booking_reference == booking_reference)
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.put("/{booking_reference}/confirm", response_model=PaymentResponse)
def confirm_payment(
    booking_reference: str, session: Session = Depends(get_session)
) -> Payment:
    payment = session.exec(
        select(Payment).where(Payment.booking_reference == booking_reference)
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status == "paid":
        raise HTTPException(status_code=400, detail="Payment already confirmed")
    payment.status = "paid"
    payment.paid_at = datetime.utcnow()
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment
