from src.database.process import DataBase
from asyncpg import Pool


class GetterAllRates:

    def __init__(self, pool: Pool):
        self.pool = pool

    async def all_rates_columns(self):
        sql = f"""SELECT column_name FROM information_schema.columns WHERE table_name='all_rates'"""
        return await DataBase(self.pool).get_all(sql)

    async def last_all_rates(self):
        sql = "SELECT * FROM all_rates ORDER BY ctid DESC LIMIT 1"
        return await DataBase(self.pool).get_row(sql)
