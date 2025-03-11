from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session, StatusEnum
from models import Event
from schemas import EventCreate, EventUpdate
from crud import get_active_objects, soft_delete

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("/", summary="Get all events")
async def get_events(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_session)):
    events = await get_active_objects(db=db, model=Event, skip=skip, limit=limit)
    return events

@router.post("/", summary="Create an event")
async def create_event(event: EventCreate, db: AsyncSession = Depends(get_async_session)):
    db_event = Event(**event.dict())
    db_event.organizer_id = 1
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return {"message": "Event created successfully", "event": event}

@router.get("/{event_id}", summary="Get an event")
async def get_event(event_id: int, db: AsyncSession = Depends(get_async_session)):
    event = await get_active_objects(db=db, model=Event, obj_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.delete("/events/{event_id}", summary="Delete an event")
async def delete_event(event_id: int, db: AsyncSession = Depends(get_async_session)):
    success = await soft_delete(db=db, model=Event, obj_id=event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}

@router.put("/events/{event_id}", summary="Update an event")
async def update_event(event_id: int, event_data: EventUpdate, db: AsyncSession = Depends(get_async_session)):
    event = await get_active_objects(db=db, model=Event, obj_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    for key, value in event_data.dict(exclude_unset=True).items():
        setattr(event, key, value)

    await db.commit()
    await db.refresh(event)
    return {"message": "Event updated successfully", "event": event}