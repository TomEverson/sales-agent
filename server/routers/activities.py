from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models.activity import Activity, ActivityCreate

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=List[Activity])
def list_activities(
    city: Optional[str] = None,
    category: Optional[str] = None,
    session: Session = Depends(get_session),
) -> List[Activity]:
    query = select(Activity)
    if city:
        query = query.where(Activity.city == city)
    if category:
        query = query.where(Activity.category == category)
    return session.exec(query).all()


@router.get("/{activity_id}", response_model=Activity)
def get_activity(activity_id: int, session: Session = Depends(get_session)) -> Activity:
    activity = session.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.post("", response_model=Activity, status_code=201)
def create_activity(activity: ActivityCreate, session: Session = Depends(get_session)) -> Activity:
    db_activity = Activity.model_validate(activity)
    session.add(db_activity)
    session.commit()
    session.refresh(db_activity)
    return db_activity


@router.put("/{activity_id}", response_model=Activity)
def update_activity(
    activity_id: int, activity: ActivityCreate, session: Session = Depends(get_session)
) -> Activity:
    db_activity = session.get(Activity, activity_id)
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    activity_data = activity.model_dump()
    for key, value in activity_data.items():
        setattr(db_activity, key, value)
    session.add(db_activity)
    session.commit()
    session.refresh(db_activity)
    return db_activity


@router.delete("/{activity_id}", status_code=204)
def delete_activity(activity_id: int, session: Session = Depends(get_session)) -> None:
    db_activity = session.get(Activity, activity_id)
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    session.delete(db_activity)
    session.commit()
