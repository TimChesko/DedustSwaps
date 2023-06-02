from datetime import datetime

from src.database.process import DataBase
from asyncpg import Pool


class SetterJettonCurrency:

    def __init__(self, pool: Pool):
        self.pool = pool

    async def add_value(self, token, tr):
        sql = f"""INSERT INTO jetton_rate (jetton, hash, value, time) 
        VALUES('{token}','{tr['hash']}', {tr['value']}, '{datetime.now()}')"""
        return await DataBase(self.pool).set(sql)
