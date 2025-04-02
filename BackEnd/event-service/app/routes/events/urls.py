from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from ..basic_schema import EventCreateModel, EventsModel
from .schemas import EventUpdateModel, EventParticipantsModel
from .controllers import get_all, get_active_by_id, create, update, soft_delete, get_active_registrations
from typing import List
from exceptions import NotFoundError, FailedError

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("/", summary="Get all events", response_model=List[EventsModel], status_code=status.HTTP_200_OK)
async def get_events(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_session)):
    events = await get_all(db=db, skip=skip, limit=limit)
    return events

@router.post("/", summary="Create an event", status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreateModel, db: AsyncSession = Depends(get_async_session)):
    try:
        new_event = await create(event_data=event, db=db)
        return {"message": "Event created successfully", "event": new_event}
    except FailedError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{event_id}", summary="Get an event", response_model=EventsModel, status_code=status.HTTP_200_OK)
async def get_event(event_id: int, db: AsyncSession = Depends(get_async_session)):
    try:
        event = await get_active_by_id(event_id=event_id, db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return event

@router.delete("/{event_id}", summary="Delete an event", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: int, db: AsyncSession = Depends(get_async_session)):
    try:
        await soft_delete(event_id=event_id, db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FailedError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{event_id}", summary="Update an event", status_code=status.HTTP_200_OK)
async def update_event(event_id: int, event_data: EventUpdateModel, db: AsyncSession = Depends(get_async_session)):
    try:
        updated_event = await update(event_id=event_id, update_data=event_data, db=db)
        return {"message": "Event updated successfully", "event": updated_event }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FailedError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/{event_id}/participants", summary="Get participants", response_model=EventParticipantsModel, status_code=status.HTTP_200_OK)
async def get_events(event_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_session)):
    participants= await get_active_registrations(event_id=event_id, db=db, skip=skip, limit=limit)
    return participants