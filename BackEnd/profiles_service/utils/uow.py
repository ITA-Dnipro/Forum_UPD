from sqlalchemy.ext.asyncio import AsyncSession

class UOW:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.session.commit()
        else:
            await self.session.rollback()
        return False

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    def __rep__(self):
        return self.__aenter__
