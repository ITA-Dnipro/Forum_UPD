from fastapi import Form
from schemas.profiles import Profile, StatusEnum
from typing import List

def profile_create_dependency(
    name: str = Form(...),
    status: StatusEnum = Form(...),
    is_registered: bool = Form(False),
    is_startup: bool = Form(False),
    is_fop: bool = Form(False),
    profile_categories: List[str] = Form(..., default=""),
) -> Profile:
    return Profile(
        name=name,
        status=status,
        is_registered=is_registered,
        is_startup=is_startup,
        is_fop=is_fop,
        profile_categories = [int(x.strip()) for x in profile_categories[0].split(",")]
    )