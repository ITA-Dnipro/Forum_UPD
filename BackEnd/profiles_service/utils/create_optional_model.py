from typing import Optional
from pydantic import BaseModel, create_model

def create_optional_model(model: type[BaseModel]) -> type[BaseModel]:
    return create_model(
        f'Optional{model.__name__}',
        **{
            field: (Optional[field_type], None)
            for field, field_type in model.__annotations__.items()
        }
    )