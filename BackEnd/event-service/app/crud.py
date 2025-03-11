from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from typing import List, Optional, Type, TypeVar
from database import StatusEnum

T = TypeVar("T")

async def get_active_objects(db: AsyncSession, model: Type[T], obj_id: int = None, skip: int = 0, limit: int = 10) -> List[T]:
    active_status_select = select(model).where(model.status != StatusEnum.deleted)
    if obj_id is not None:
        active_status_select = active_status_select.where(model.id == obj_id)
    else:
        active_status_select = active_status_select.offset(skip).limit(limit)
    
    result = await db.execute(active_status_select)
    if obj_id is not None:
        return result.scalar_one_or_none()
    else:
        return result.scalars().all()

async def soft_delete(db: AsyncSession, model: Type[T], obj_id: int) -> bool:
    try:
        obj_to_delete = select(model).where(model.id == obj_id, model.status != StatusEnum.deleted)
        result = await db.execute(obj_to_delete)
        obj = result.scalar_one_or_none()
        
        if not obj:
            return False
        
        setattr(obj, "status", StatusEnum.deleted)

        await db.commit()
        return True
    
    except Exception:
        await db.rollback()
        return False



