from sqlmodel import Session, select
from db import create_db_and_tables, engine
from models.insurance import InsurancePlan


PLANS = [
    {
        "name": "Basic Coverage",
        "description": "Trip cancellation and flight delay protection",
        "price_per_person": 15.0,
        "coverage_types": "cancellation,flight_delay",
        "max_trip_value": 500.0,
        "medical_coverage": 0.0,
        "cancellation_coverage": 300.0,
        "is_active": True,
    },
    {
        "name": "Standard Protection",
        "description": "Basic + Medical expenses up to $10,000",
        "price_per_person": 35.0,
        "coverage_types": "cancellation,flight_delay,medical",
        "max_trip_value": 1500.0,
        "medical_coverage": 10000.0,
        "cancellation_coverage": 500.0,
        "is_active": True,
    },
    {
        "name": "Premium Coverage",
        "description": "Standard + Lost luggage and adventure activities",
        "price_per_person": 65.0,
        "coverage_types": "cancellation,flight_delay,medical,luggage,adventure",
        "max_trip_value": 3000.0,
        "medical_coverage": 25000.0,
        "cancellation_coverage": 1000.0,
        "is_active": True,
    },
]


def seed_insurance():
    create_db_and_tables()

    with Session(engine) as session:
        for plan in session.exec(select(InsurancePlan)).all():
            session.delete(plan)
        session.commit()

        plans = [InsurancePlan(**p) for p in PLANS]
        session.add_all(plans)
        session.commit()

        count = len(session.exec(select(InsurancePlan)).all())
        print(f"Seeded: {count} insurance plans")


if __name__ == "__main__":
    seed_insurance()
