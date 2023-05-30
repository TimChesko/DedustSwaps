from asyncpg import Pool

from src.database.process import DataBase


class GetterJettonRate:

    def __init__(self, pool: Pool):
        self.pool = pool

    async def last_jetton_transaction(self, jetton: str):
        sql = f"""SELECT * FROM jetton_currency WHERE 
                jetton='{jetton}' ORDER BY ctid DESC LIMIT 1"""
        return await DataBase(self.pool).get_row(sql)

    async def get_transaction_by_hash(self, hash_tr: str):
        sql = f"""SELECT * FROM jetton_currency WHERE 
                        hash='{hash_tr}' ORDER BY ctid DESC LIMIT 1"""
        return await DataBase(self.pool).get_row(sql)

    async def get_pool_by_time(self, token: str, days: int):
        sql = f"""SELECT SUM(value) 
                FROM jetton_currency 
                WHERE jetton = '{token}' 
                AND time 
                BETWEEN NOW()::DATE - INTERVAL '{days} days' AND NOW()"""
        return await DataBase(self.pool).get_row(sql)

    async def get_volume_by_time(self, token: str, days: int):
        sql = f"""SELECT SUM(ABS(value)) 
                    FROM jetton_currency 
                    WHERE jetton = '{token}' 
                    AND time BETWEEN NOW()::DATE - INTERVAL '{days} days' AND NOW();
                """
        return await DataBase(self.pool).get_row(sql)
