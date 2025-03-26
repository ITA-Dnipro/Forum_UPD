from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import EventParticipantBaseModel, EventsRegisteredRequestModel
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from .controllers import register, cancel, get_registered_events
from ..events.controllers import get_active_by_id
from exceptions import FailedError, NotFoundError, RegistrationForbidden
from typing import List

router = APIRouter(prefix="/events/participants", tags=["Participants"])


@router.post("/{event_id}/register", summary="Register for an event", response_model=EventsRegisteredRequestModel, status_code=status.HTTP_201_CREATED)
async def register_for_event(registration_data: EventParticipantBaseModel, event_id: int, db: AsyncSession = Depends(get_async_session)):
    try:
        await get_active_by_id(event_id=event_id, db=db)
        registration = await register(data=registration_data, event_id=event_id, db=db)
        return registration
    except RegistrationForbidden as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FailedError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{event_id}/register", summary="Cancel registration", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_registration(event_id: int, db: AsyncSession = Depends(get_async_session)):
    try:
        await get_active_by_id(event_id=event_id, db=db)
        await cancel(event_id=event_id, db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FailedError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    
@router.get("/registrations/all", summary="Get all registrations for user", response_model=List[EventsRegisteredRequestModel], status_code=status.HTTP_200_OK)
async def get_events(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_session)):
    events = await get_registered_events(user_id=1, db=db, skip=skip, limit=limit)
    return events