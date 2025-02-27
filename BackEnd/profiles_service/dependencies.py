from fastapi import Form
from schemas.profiles import Profile

def profile_create_dependency(
    name: str = Form(...),
    is_registered: bool = Form(False),
    is_startup: bool = Form(False),
    is_fop: bool = Form(False),
    categories_ids: list[int] = Form(...),
) -> Profile:
    return Profile(
        name=name,
        is_registered=is_registered,
        is_startup=is_startup,
        is_fop=is_fop,
        categories_ids=categories_ids
    )