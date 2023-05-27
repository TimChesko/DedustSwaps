from src.database.process import DataBase


class JettonsInfo:

    def __init__(self, pool):
        self.pool = pool

    async def get_all(self) -> list:
        sql = f"""SELECT * FROM jettons_info"""
        return await DataBase(self.pool).get_all(sql)

    async def get_all_address(self) -> list:
        sql = f"""SELECT tiker, pool_address, work_address FROM jettons_info"""
        return await DataBase(self.pool).get_all(sql)
