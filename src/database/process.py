import asyncpg
from asyncpg import Pool


class DataBase:

    def __init__(self, pool):
        self.pool = pool

    @staticmethod
    async def create_db_connection(config) -> Pool:
        return await asyncpg.create_pool(host=config.PG_HOST,
                                         user=config.PG_USER,
                                         password=config.PG_PASSWORD,
                                         database=config.PG_DATABASE)

    async def close_db_connection(self) -> None:
        db_pool: asyncpg.Pool = self.pool
        await db_pool.close()

    async def get_row(self, sql_request: str):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetchrow(sql_request)

    async def get_all(self, sql_request: str) -> list:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetch(sql_request)

    async def set(self, sql_request: str) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(sql_request)
