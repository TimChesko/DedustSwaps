from src.database.process import DataBase


async def get_all_rates_columns(pool):
    sql = f"""SELECT column_name FROM information_schema.columns WHERE table_name='all_rates'"""
    return await DataBase(pool).get_all(sql)
