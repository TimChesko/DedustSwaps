from datetime import datetime

from src.models.all_rates.get import GetterAllRates
from src.models.all_rates.set import SetterAllRates
from src.models.jetton_rate.get import GetterJettonRate
from src.models.jetton_rate.set import SetterJettonCurrency
from src.service.jettons.api import FastApi
from aiogram import Dispatcher, Bot
from aiogram.utils.markdown import hlink
from asyncpg import Pool

from src.service.newsletter import MsgWork


class ProcessJettons:

    def __init__(self, dp: Dispatcher, jettons_info: list, start: bool):
        self.dp = dp
        self.bot: Bot = dp['bot']
        self.pool: Pool = dp['db_pool']
        self.jettons_info = jettons_info
        self.start = start
        self.trs_to_text = []

    async def update_rates(self) -> None:
        rates_response, trs_response = await self.get_rates_and_transactions()
        await self.__process_rates(rates_response)
        await self.__process_trs(trs_response)
        await self.__process_publish()

    async def __process_publish(self) -> None:
        text = await self.__create_text()
        if len(text) != 0:
            await MsgWork(self.dp).send_msg_array(text)

    async def __create_text(self) -> list[str]:
        result_text = []
        text_all = ""
        bot_name = (await self.bot.get_me()).username
        for index, info in enumerate(self.trs_to_text):
            token = next(iter(info.keys()))
            if len(self.trs_to_text[index][token]) != 0:
                text_token = f"#{token}\n" if len(text_all) == 0 else f"\n#{token}\n"
                for tr in self.trs_to_text[index][token]:
                    text_tr = "🟢 / " if tr['value'] < 0 else "🔴 / "
                    text_tr += str(abs(tr['value'])) + \
                               f" / {datetime.utcfromtimestamp(tr['time']).strftime('%H:%M:%S')}"
                    text_token += hlink(text_tr, f"https://t.me/{bot_name}?start={tr['hash']}") + "\n"

                if len(text_all + text_token) >= 4096:
                    result_text.append(text_all)
                    text_all = text_token
                else:
                    text_all += text_token
        if len(text_all) != 0:
            text_all += "\n@dedustSwaps | @tonnull"
            result_text.append(text_all)
        return result_text

    async def __process_trs(self, trs: dict) -> None:
        for index, token in enumerate(trs):
            last_tr = await GetterJettonRate(self.pool).last_jetton_transaction(token)
            all_trs = trs[token]['transactions']
            if self.start:
                if last_tr["hash"] != all_trs[0]["hash"]:
                    await SetterJettonCurrency(self.pool).add_value(token, all_trs[0])
            else:
                self.trs_to_text.append({token: []})
                for i in range(len(all_trs)):
                    if last_tr["hash"] == all_trs[i]["hash"] and i != 0:
                        for x in reversed(all_trs[:i]):
                            await SetterJettonCurrency(self.pool).add_value(token, x)
                            self.trs_to_text[index][token].append(x)

    async def __process_rates(self, rates: dict) -> None:
        if await self.__check_rates(rates):
            sql_columns, sql_values = await self.__get_sql_format(rates)
            await SetterAllRates(self.pool).add_values(sql_columns, sql_values)

    async def __check_rates(self, rates: dict) -> bool:
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
    async def __get_sql_format(rates: dict) -> tuple[str, str]:
        sql_columns = ",".join(map(str.lower, rates.keys()))
        sql_values = ",".join([str(val) for val in rates.values()])
        return sql_columns, sql_values

    async def get_rates_and_transactions(self) -> tuple[dict[str, int], dict[str, str, str]]:
        tokens_list_pool, tokens_list_work = await self.__struct_info()
        rates_response = await FastApi(tokens_list_pool).get_tokens_rates()
        trs_response = await FastApi(tokens_list_work).get_last_transactions(10)
        return rates_response, trs_response

    async def __struct_info(self) -> tuple[list, list]:
        rates, transactions = [], []
        for jetton in self.jettons_info:
            rates.append({'token': jetton['tiker'],
                          'address': jetton['pool_address'],
                          'decimals': jetton['decimals']})
            transactions.append({'token': jetton['tiker'],
                                 'address': jetton['work_address'],
                                 'decimals': jetton['decimals']})
        return rates, transactions
