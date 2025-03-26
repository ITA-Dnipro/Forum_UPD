from .schemas import EventParticipantBaseModel, EventsRegisteredRequestModel
from sqlalchemy.ext.asyncio import AsyncSession
from .models import EventParticipant
from exceptions import FailedError, RegistrationForbidden
from ..events.models import Event
from sqlalchemy import select, update, desc
from typing import List

async def check_slots_amount(event_id: int, db: AsyncSession) -> int:
    query = await db.execute(
        select(Event.available_slots)
        .where(Event.id == event_id)
        .with_for_update()
    )
    event = query.first()
    available_slots, = event
    return available_slots

async def update_availiable_slots(slots_number: int, event_id: int, db: AsyncSession) -> bool:        
    available_slots = await check_slots_amount(event_id=event_id, db=db)
    if slots_number > available_slots:
        raise FailedError(
            f"Not enough available slots: requested {slots_number}, available {available_slots}"
        )
    try:
        await db.execute(
            update(Event)
            .where(Event.id == event_id)
            .values(available_slots=available_slots - slots_number)
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise FailedError(f"Failed to update available slots: {str(e)}")

async def check_existing_registration(user_id: int, event_id: int, db: AsyncSession) -> bool:
    result = await db.execute(
        select(EventParticipant)
        .where(
            EventParticipant.user_id == user_id,
            EventParticipant.event_id == event_id,
            EventParticipant.is_deleted == False
        )
    )
    return result.scalars().first() is not None

async def register(data: EventParticipantBaseModel, event_id: int, db: AsyncSession) -> EventParticipant:
    registration_dict = data.model_dump()
    registration = EventParticipant(**registration_dict)
    registration.user_id = 1
    registration.event_id = event_id
    
    if await check_existing_registration(user_id=registration.user_id, event_id=event_id, db=db):
        raise RegistrationForbidden("User is already registered for this event")
    try:
        await update_availiable_slots(slots_number=registration.human_slots, event_id=event_id, db=db)
        db.add(registration)
        await db.commit()
        await db.refresh(registration)
        return registration
    except Exception as e:
        await db.rollback()
        raise FailedError(f"Failed to register for event: {str(e)}")

async def recover_slots(slots_number: int, event_id: int, db: AsyncSession) -> bool:
    available_slots = await check_slots_amount(event_id=event_id, db=db)
    try:
        await db.execute(
            update(Event)
            .where(Event.id == event_id)
            .values(available_slots=available_slots + slots_number)
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise FailedError(f"Failed to reclaim availiable slots: {str(e)}")
    
async def cancel(event_id: int, db: AsyncSession) -> bool:
    registration = await db.execute(
        select(EventParticipant)
        .where(
            EventParticipant.user_id == 1,
            EventParticipant.event_id == event_id,
            EventParticipant.is_deleted == False
        )
        .limit(1)
    )
    to_cancel = registration.scalars().first()
    if to_cancel is None:
        raise FailedError("Active registration not found")
    
    to_cancel.is_deleted = True
    slots_to_recover = to_cancel.human_slots
    try:
        await recover_slots(slots_number=slots_to_recover, event_id=event_id, db=db)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise FailedError(f"Failed to cancel registration for event {event_id}: {str(e)}")
    
async def get_registered_events(user_id: int, db: AsyncSession, skip: int = 0, limit: int = 10) -> List[EventsRegisteredRequestModel]:
    result = await db.execute(
        select(EventParticipant)
        .join(EventParticipant.event) 
        .where(
            EventParticipant.user_id == user_id,
            EventParticipant.is_deleted != True
        )
        .order_by(desc(Event.date))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().unique().all()