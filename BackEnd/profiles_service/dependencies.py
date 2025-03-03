from fastapi import Body, Form
from schemas.profiles import Profile, StatusEnum
from typing import List

def profile_create_dependency(
    name: str = Body(...),
    status: StatusEnum = Body(...),
    is_registered: bool = Body(False),
    is_startup: bool = Body(False),
    is_fop: bool = Body(False),
    profile_categories: List[int] = Body(...),
    profile_regions: List[int] = Body(...) ,
) -> Profile:
    return Profile(
        name=name,
        status=status,
        is_registered=is_registered,
        is_startup=is_startup,
        is_fop=is_fop,
        profile_categories = profile_categories,
        profile_regions = profile_regions
    )