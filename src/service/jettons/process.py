import time

from src.models.jetton_rate.get import get_last_jetton_rate
from src.service.jettons.api import FastApi


class ProcessJettons:

    def __init__(self, pool, jettons_info, start):
        self.pool = pool
        self.jettons_info = jettons_info
        self.start = start

    async def update_rates(self):
        await self.get_rates_and_transactions()

    async def get_rates_and_transactions(self):
        rates_links, transactions_links = await self.__struct_info(self.jettons_info)
        rates = await self.__sort_rates(await FastApi(rates_links, False).run())
        transactions = await self.__sort_transactions(await FastApi(transactions_links, True).run())
        print(transactions)

    async def __sort_rates(self, response):
        result = []
        for token in self.jettons_info:
            if token['tiker'] in response:
                info = response[token['tiker']]
                if 'result' in info and len(info['result']) >= 2 and 'value' in info['result'][1]:
                    value = int(info['result'][1]['value']) / 1e9
                    value = round(1 / value, token['decimals'])
                    result.append([(token['tiker']).lower(), value])
            else:
                return None
        return result

    async def __sort_transactions(self, response):
        verify_transactions = []
        for token in self.jettons_info:
            if token['tiker'] in response:
                last_info = await get_last_jetton_rate(self.pool, token['tiker'])
                for transaction in response[token['tiker']]:
                    try:
                        hash_transaction = transaction['hash']
                        if last_info is not None and hash_transaction == last_info['hash']:
                            break
                        else:
                            transaction_source = None
                            if 'decoded_body' in transaction['out_msgs'][0] and 'Amount' in transaction['out_msgs'][0][
                                'decoded_body']:
                                transaction_source = transaction['out_msgs'][0]

                            elif 'decoded_body' in transaction['in_msg'] and 'Amount' in transaction['in_msg'][
                                'decoded_body']:
                                transaction_source = transaction['in_msg']
                            if transaction_source is not None:
                                verify_transactions.append(
                                    [token, transaction_source, hash_transaction])
                                if self.start:
                                    break
                    except Exception as e:
                        print(e)
        return verify_transactions

    async def __struct_info(self, all_jettons_address):
        rates_links, transactions_links = [], []
        block_info = [["block", "http://mainnet-v4.tonhubapi.com/block/latest"]]
        block = (await FastApi(block_info, False).run())['block']['last']['seqno']
        for token in all_jettons_address:
            urls = await self.__create_link(token, block)
            rates_links.append([token['tiker'], urls[0]])
            transactions_links.append([token['tiker'], urls[1]])
        return rates_links, transactions_links

    @staticmethod
    async def __create_link(token, block):
        body = "te6ccgEBBAEAHQABGAAAAgEAAAAAO5rKAAECCQQAAEAgAwIAAQgAAA"
        url_rate = f"http://mainnet-v4.tonhubapi.com/block/{block}/" \
                   f"{token['pool_address']}/run/estimate_swap_out/{body}"

        url_transactions = f"https://everspace.center/toncoin/getTransactions?address={token['work_address']}" \
                           f"&limit=20"
        return [url_rate, url_transactions]
