from datetime import datetime

from src.database.process import DataBase
from asyncpg import Pool


class SetterAllRates:

    def __init__(self, pool: Pool):
        self.pool = pool

    async def add_column_all_rates(self, token_name):
        sql = f"""ALTER TABLE all_rates ADD COLUMN {token_name.lower()} FLOAT"""
        return await DataBase(self.pool).set(sql)

    async def add_values(self, columns, values):
        sql = f"""INSERT INTO all_rates (time, {columns}) 
                    VALUES('{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', {values})"""
        return await DataBase(self.pool).set(sql)
