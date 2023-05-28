from src.models.all_rates.get import GetterAllRates
from src.models.all_rates.set import SetterAllRates
from src.models.jetton_rate.get import GetterJettonRate
from src.models.jetton_rate.set import SetterJettonCurrency
from src.service.jettons.api import FastApi


class ProcessJettons:

    def __init__(self, pool, jettons_info, start):
        self.pool = pool
        self.jettons_info = jettons_info
        self.start = start

    async def update_rates(self):
        rates_response, trs_response = await self.get_rates_and_transactions()
        await self.__process_rates(rates_response)
        await self.__process_trs(trs_response)

    async def __process_trs(self, trs):
        for token in trs:
            last_tr = await GetterJettonRate(self.pool).last_jetton_transaction(token)
            all_trs = trs[token]['transactions']
            if self.start:
                if last_tr["hash"] != all_trs[0]["hash"]:
                    await SetterJettonCurrency(self.pool).add_value(token, all_trs[0])
            else:
                for i in range(len(all_trs)):
                    if last_tr["hash"] == all_trs[i]["hash"] and i != 0:
                        for x in reversed(all_trs[:i]):
                            await SetterJettonCurrency(self.pool).add_value(token, x)

    async def __process_rates(self, rates):
        if await self.__check_rates(rates):
            sql_columns, sql_values = await self.__get_sql_format(rates)
            await SetterAllRates(self.pool).add_values(sql_columns, sql_values)

    async def __check_rates(self, rates):
        last_rates = await GetterAllRates(self.pool).last_all_rates()
        if last_rates is None:
            return True
        counter = 0
        for rate in rates:
            if rates[rate] is None:
                return False
            if rates[rate] == last_rates[rate.lower()]:
                counter += 1
        if counter != len(last_rates) - 1:
            return True
        return False

    @staticmethod
    async def __get_sql_format(rates):
        sql_columns = ",".join(map(str.lower, rates.keys()))
        sql_values = ",".join([str(val) for val in rates.values()])
        return sql_columns, sql_values

    async def get_rates_and_transactions(self):
        tokens_list_pool, tokens_list_work = await self.__struct_info()
        rates_response = await FastApi(tokens_list_pool).get_tokens_rates()
        trs_response = await FastApi(tokens_list_work).get_last_transactions(10)
        return rates_response, trs_response

    async def __struct_info(self):
        rates, transactions = [], []
        for jetton in self.jettons_info:
            rates.append({'token': jetton['tiker'], 'address': jetton['pool_address']})
            transactions.append({'token': jetton['tiker'], 'address': jetton['work_address']})
        return rates, transactions
