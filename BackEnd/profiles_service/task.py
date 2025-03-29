import asyncio
from celery.app import Celery
from models import *
from models.images import ProfileImage
from models.startups import StatusEnum
from core.settings import settings
from core.database import new_session
import os

from utils.repositories import BaseRepository, ProfileRepository


redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_url = settings.REDIS_URL

app = Celery(__name__, broker=redis_url, backend=redis_url)



@app.task(name='autoapprove_image')
def autoapprove_image(profile_id):
    async def async_autoapprove():
        async with new_session() as session:
            profile_repo = ProfileRepository(model=StartupProfileOrm, session=session)
            image_repo = BaseRepository(ProfileImage, session=session)
            profile_dict = {"status": StatusEnum.AUTOAPPROVED}
            profile = await profile_repo.update(instance_id=profile_id, data=profile_dict)
            banner_id = profile.banner_id
            await image_repo.partial_update(instance_id=banner_id, update_fields={"is_approved": True})

    coroutine = async_autoapprove() 
    return asyncio.run(coroutine)
    