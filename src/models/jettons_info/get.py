from src.database.process import DataBase


async def get_all_jettons_info(pool):
    sql = f"""SELECT * FROM jettons_info"""
    return await DataBase(pool).get_all(sql)
