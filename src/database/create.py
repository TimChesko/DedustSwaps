from src.database.process import DataBase
from src.models.all_rates.get import GetterAllRates
from src.models.all_rates.set import SetterAllRates
from src.models.jettons_info.get import JettonsInfo


class CreateTables:

    def __init__(self, pool):
        self.pool = pool

    async def process(self) -> None:
        await self.create()
        await self.update()

    async def create(self) -> None:
        sql_requests = [
            '''
                CREATE TABLE IF NOT EXISTS jettons_info (
                            tiker TEXT NOT NULL,
                            emoji TEXT NOT NULL,
                            link TEXT NOT NULL,
                            address TEXT NOT NULL,
                            pool_address TEXT NOT NULL,
                            work_address TEXT,
                            decimals INT NOT NULL,
                            timeframe INT NOT NULL)
            ''', '''
                            CREATE TABLE IF NOT EXISTS all_rates (
                                time TIMESTAMP NOT NULL,
                                ton FLOAT)
                        ''', '''
                            CREATE TABLE IF NOT EXISTS jetton_currency (
                                jetton TEXT NOT NULL,
                                hash TEXT NOT NULL,
                                value FLOAT NOT NULL,
                                time TIMESTAMP NOT NULL)
                        ''']
        for sql in sql_requests:
            await DataBase(self.pool).set(sql)

    async def update(self) -> None:
        jettons_info = await JettonsInfo(self.pool).get_all()
        all_rates_columns = await GetterAllRates(self.pool).all_rates_columns()
        if len(jettons_info) > len(all_rates_columns) - 2:
            await self.__check_tokens(jettons_info, all_rates_columns)

    async def __check_tokens(self, jettons_info: list, all_rates_columns: list) -> None:
        for token_info in jettons_info:
            if (token_info['tiker']).lower() not in [tiker['column_name'] for tiker in all_rates_columns]:
                await SetterAllRates(self.pool).add_column_all_rates(token_info['tiker'])
