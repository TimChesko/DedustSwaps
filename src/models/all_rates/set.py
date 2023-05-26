from src.database.process import DataBase


async def add_column_all_rates(pool, token_name):
    sql = f""" ALTER TABLE all_rates ADD COLUMN {token_name.lower()} FLOAT"""
    return await DataBase(pool).set(sql)
