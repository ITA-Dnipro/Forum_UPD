from typing import Annotated
from fastapi import APIRouter, Depends, File, Response, UploadFile
from fastapi import HTTPException
from services.images import ImageService
from dependencies import get_image_service


router = APIRouter(
    tags=["Profile images"]
)

@router.post("/", status_code=200)
async def create_file(
    file: Annotated[UploadFile, File(...)],
    service: Annotated[ImageService, Depends(dependency=get_image_service)]
    ):
    image = await service.add_image(file=file)
    return image
    

