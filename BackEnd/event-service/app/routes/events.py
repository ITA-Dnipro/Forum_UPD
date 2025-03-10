from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Event
from schemas import EventCreate, EventUpdate

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("/", summary="Get all events")
def get_events(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    events = db.query(Event).offset(skip).limit(limit).all()
    return events

@router.post("/", summary="Create an event")
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = Event(**event.dict())
    db_event.organizer_id = 1
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return {"message": "Event created successfully", "event": event}

@router.get("/{event_id}", summary="Get an vent")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.delete("/events/{event_id}", summary="Delete an event")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}

@router.put("/events/{event_id}", summary="Update an event")
def update_event(event_id: int, event_data: EventUpdate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    for key, value in event_data.dict(exclude_unset=True).items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return {"message": "Event updated successfully", "event": event}