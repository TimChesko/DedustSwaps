from src.database.process import DataBase
from asyncpg import Pool


class GetterJettonRate:

    def __init__(self, pool: Pool):
        self.pool = pool

    async def last_jetton_transaction(self, jetton: str):
        sql = f"""SELECT * FROM jetton_currency WHERE 
                jetton='{jetton}' ORDER BY ctid DESC LIMIT 1"""
        return await DataBase(self.pool).get_row(sql)
