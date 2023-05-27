from src.database.process import DataBase
from asyncpg import Pool


async def get_last_jetton_rate(pool: Pool, jetton: str):
    sql = f"""SELECT * FROM jetton_currency WHERE 
            jetton='{jetton}' ORDER BY ctid DESC LIMIT 1"""
    return await DataBase(pool).get_row(sql)