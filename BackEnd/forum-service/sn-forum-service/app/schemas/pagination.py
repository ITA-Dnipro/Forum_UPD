from pydantic import BaseModel
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    next_paging_state: Optional[str] = None