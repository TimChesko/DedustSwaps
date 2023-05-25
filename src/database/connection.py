import asyncpg
from asyncpg import Pool


class DataBase:

    def __init__(self, dispatcher):
        config = dispatcher['config']
        self.host = config.PG_HOST
        self.user = config.PG_USER
        self.password = config.PG_PASSWORD
        self.database = config.PG_DATABASE

    async def create_db_connection(self) -> Pool:
        return await asyncpg.create_pool(user=self.user,
                                         password=self.password,
                                         database=self.database,
                                         host=self.host)

    @staticmethod
    async def close_db_connection(pool) -> None:
        db_pool: asyncpg.Pool = pool
        await db_pool.close()

    @staticmethod
    async def get_row(pool, sql_request: str):
        async with pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetchrow(sql_request)

    @staticmethod
    async def get_all(pool, sql_request: str) -> list:
        async with pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetch(sql_request)

    @staticmethod
    async def set(pool, sql_request: str) -> None:
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(sql_request)
