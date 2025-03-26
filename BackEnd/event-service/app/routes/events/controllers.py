from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from enums import StatusEnum
from .models import Event
from .schemas import EventUpdateModel
from ..basic_schema import EventCreateModel
from exceptions import NotFoundError, FailedError

async def get_active_by_id(event_id: int, db: AsyncSession) -> Event:
    event = await db.get(Event, event_id)
    if not event or event.status == StatusEnum.deleted:
        raise NotFoundError("Event not found")
    return event

async def get_all(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Event]:
    active_status_select = (
        select(Event)
        .where(Event.status != StatusEnum.deleted)
        .order_by(desc(Event.date))
        .offset(skip)
        .limit(limit)
        )
    result = await db.execute(active_status_select)
    return result.scalars().unique().all()

async def create(event_data: EventCreateModel, db: AsyncSession) -> Event:
    event_data_dict = event_data.model_dump()
    new_event = Event(**event_data_dict)
    new_event.organizer_id = 1
    new_event.status = StatusEnum.active
    try:
        db.add(new_event)
        await db.commit()
        await db.refresh(new_event)
        return new_event
    except Exception as e:
        await db.rollback()
        raise FailedError(f"Failed to create event: {str(e)}")

async def update(event_id: int, update_data: EventUpdateModel, db: AsyncSession) -> Event:
    event_to_update = await get_active_by_id(event_id=event_id, db=db)    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(event_to_update, key, value)
    try:
        await db.commit()
        await db.refresh(event_to_update)
        return event_to_update
    except Exception as e:
        await db.rollback()
        raise FailedError(f"Failed to update event {event_id}: {str(e)}")

async def soft_delete(event_id: int, db: AsyncSession) -> bool:
    event_to_delete = await get_active_by_id(event_id, db)
    event_to_delete.status = StatusEnum.deleted
    try:
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise FailedError(f"Failed to delete event {event_id}: {str(e)}")
    
async def get_active_registrations(event_id: int, db: AsyncSession, skip: int = 0, limit: int = 10) -> Event:
    event = await get_active_by_id(event_id=event_id, db=db)
    event.participants = [participant for participant in event.participants if not participant.is_deleted]
    event.participants = event.participants[skip:skip+limit]
    return event