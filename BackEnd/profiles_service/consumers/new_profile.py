
from contextlib import asynccontextmanager
from schemas.profiles import Startup, Investor
from dependencies import get_startup_service, get_investor_service
from dependencies import get_async_ouw
from core.database import new_session


@asynccontextmanager
async def get_manual_session():
    session = new_session()
    try:
        yield session
    finally:
        await session.close()



async def consume_new_user_profiles(consumer):
    try:
        async for msg in consumer:
            value = msg.value["company"]
            print(msg.value)
            async with get_manual_session() as session:
                if value["is_startup"]:
                    data = {
                    "user_id": value["user_id"],
                    "is_registered": True,
                    "is_startup": True,
                    "is_fop": not value["is_legal_entity"],
                    "name": value["name"]
                    }
                    startup = Startup(**data)
                    service = get_startup_service(get_async_ouw(session))
                    await service.add_startup(startup)

                elif not value["is_startup"]:
                    data = {
                    "user_id": value["user_id"],
                    "is_legal_entity": value["is_legal_entity"],
                    "name": value["name"]
                    }
                    investor = Investor(**data)
                    service = get_investor_service(get_async_ouw(session))
                    await service.add_investor(investor)

    finally:
        await consumer.stop()