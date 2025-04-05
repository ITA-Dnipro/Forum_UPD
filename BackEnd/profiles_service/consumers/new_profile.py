
from services.startups import ProfileStartupService
from services.investors import InvestorsService
from schemas.profiles import Startup, Investor


async def consume_new_user_profiles(consumer):
    try:
        async for msg in consumer:
            print(
                "consumed: ",
                msg.topic,
                msg.partition,
                msg.offset,
                msg.key,
                msg.value,
                msg.timestamp,
            )

            if msg.value["is_startup"]:
                data = {
                "user_id": msg.value["user_id"],
                "is_startup": True,
                "is_fop": msg.value["is_fop"],
                "name": msg.name["name"]
                }
                startup = Startup(**data)
                ProfileStartupService.add_startup(startup)

            elif not msg.value["is_startup"]:
                data = {
                "user_id": msg.value["user_id"],
                "is_legal_entity": msg.value["is_legal_entity"],
                "name": msg.name["name"]
                }
                investor = Investor(**data)
                InvestorsService.add_investor(investor)

    finally:
        await consumer.stop()