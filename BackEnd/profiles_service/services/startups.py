from utils.uow import UOW
from models.startups import StatusEnum
from schemas.profiles import Startup, StartupOptional, ModerationFeedback, ProfileModerationEnum
from repositories.base import BaseRepository
from repositories.profiles import ProfileRepository
from task import autoapprove_image
from utils.producer import send_approval_email, send_valid_profile_message, get_producer
from utils.time import to_local_time, update_time_to_str
from utils.profile_validation import validate_startup



MODERATION_HOURS = 0.02


class ProfileStartupService:

    def __init__(
            self, 
            uow: UOW,
            repo: ProfileRepository, 
            image_repo: BaseRepository,
            validation_repo: BaseRepository,
            ):
        self.uow = uow
        self.repository = repo
        self.image_repo = image_repo
        self.validation_repo = validation_repo


    async def startups_list(self):
        return await self.repository.get_all()

    async def get_startup_by_id(self, startup_id):
        return await self.repository.get_by_id(startup_id)
    

    async def add_startup(self, data: Startup):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        profile_dict["status"] = StatusEnum.UNDEFINED
        async with self.uow as uow:
            profile = await self.repository.add_one(profile_dict=profile_dict)
            if "edrpou" in profile_dict:
                await self.validation_repo.add_one({"profile_id": profile.id})            
                await uow.session.refresh(profile)
        return profile


    async def partial_startup_update(self, profile_id: int, data: StartupOptional):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        async with self.uow as uow:
            if "banner_id" in profile_dict:
                profile_dict["status"] = StatusEnum.PENDING 
                autoapprove_image.apply_async(args=(profile_id,), countdown=MODERATION_HOURS*3600)
                profile = await self.repository.update(instance_id=profile_id, data=profile_dict)

                profile_view_url = f"http://localhost:8000/api/startup_profiles/{profile.id}/images_moderation"
                await uow.session.refresh(profile)
                await send_approval_email(
                producer = await get_producer(),
                profile_name=profile.name,
                updated_at=profile.updated_at,
                moderation_time=MODERATION_HOURS,
                image_path=profile.banner.image_path,
                profile_view_url=profile_view_url
                )
            else:
                profile = await self.repository.update(instance_id=profile_id, data=profile_dict)
                await uow.session.refresh(profile)

            if "edrpou" in profile_dict:

                if profile.validations:
                    await self.validation_repo.update(profile.validations.id, {"profile_id": profile.id})
                else:
                    await self.validation_repo.add_one({"profile_id": profile.id})


        if validate_startup(profile):
            await send_valid_profile_message(
                producer=await get_producer(),
                user_id=profile.user_id, 
                profile_type="startup",
                status="validated"
                )
            
        return profile


    async def startup_delete(self, profile_id: int):
        async with self.uow as uow:
            await self.repository.soft_delete(profile_id)

    
    async def handle_moderation_feedback(self, profile_id, feedback: ModerationFeedback):     

        feedback_dict = feedback.model_dump()
        async with self.uow as uow:
            if feedback_dict["moderation_status"] == ProfileModerationEnum.APPROVED:  
                profile_update_fields = {"status": StatusEnum.APPROVED}
                profile = await self.repository.update(instance_id=profile_id, data=profile_update_fields)

                banner_id = profile.banner_id
                
                await self.image_repo.update(instance_id=banner_id, data={"is_approved": True})
                
            elif feedback_dict["moderation_status"] == ProfileModerationEnum.REJECTED:
                profile_update_fields = {"status": StatusEnum.BLOCKED}
                await self.repository.soft_delete(profile_id=profile_id)
                profile = await self.repository.update(instance_id=profile_id, data=profile_update_fields)

                banner_id = profile.banner_id
                
                await self.image_repo.update(instance_id=banner_id, data={"is_approved": False})
            await uow.session.refresh(profile)
            
        return profile



