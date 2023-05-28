import asyncio
import json
from pathlib import Path

import aiohttp
import requests
from pytonlib import TonlibClient
from pytonlib.utils.tlb import Slice, deserialize_boc, JettonTransferNotificationMessage, \
    JettonTransferMessage
from tonsdk.contract import Address
from tonsdk.utils import b64str_to_bytes


class FastApi:
    def __init__(self, tokens_list: list[dict[str, str]]):
        self.tokens_list = tokens_list
        self.block = None
        self.result = {}

    async def get_last_transactions(self, limit: int) -> dict[str, str, str]:
        client = await self.__get_client()

        async def get(info: dict[str, str]) -> None:
            trs = await client.get_transactions(account=info["address"], limit=limit)
            self.result[info['token']] = {'transactions': []}
            for tr in trs:
                try:
                    body = tr['out_msgs'][0]['msg_data']['body']
                    cell = deserialize_boc(b64str_to_bytes(body))
                    value = JettonTransferMessage(Slice(cell))
                    self.result[info['token']]['transactions'].append(
                        {
                            "sender": "local",
                            "value": value.amount / 1e9 * -1,
                            "hash": tr['transaction_id']['hash']
                        }
                    )
                except:
                    pass

                try:
                    body = tr['in_msg']['msg_data']['body']
                    cell = deserialize_boc(b64str_to_bytes(body))
                    value = JettonTransferNotificationMessage(Slice(cell))
                    sender_address = Address(
                        str(value.sender.workchain_id) + ':' + str(value.sender.address)).to_string(True, True, True)
                    self.result[info['token']]['transactions'].append(
                        {
                            "sender": sender_address,
                            "value": value.amount / 1e9,
                            "hash": tr['transaction_id']['hash']
                        }
                    )
                except:
                    pass

        tasks = [get(info) for info in self.tokens_list]
        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=5)
        except asyncio.TimeoutError:
            print("Timeout exceeded...")
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

        return self.result

    async def get_tokens_rates(self) -> dict[str, int]:
        connection = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)
        self.result['TON'] = await self.get_ton()
        try:
            async with aiohttp.ClientSession(connector=connection) as session:
                tasks = []
                for info in self.tokens_list:
                    async with asyncio.Semaphore(100):
                        try:
                            block_url = "http://mainnet-v4.tonhubapi.com/block/latest"
                            async with session.get(block_url, ssl=False) as response:
                                obj = json.loads(await response.read())
                                self.block = obj['last']['seqno']
                            url_rate = await self.__create_link(info, self.block)
                            task = asyncio.ensure_future(self.__get_data(session, url_rate, info['token']))
                            tasks.append(task)
                        except:
                            pass

                await asyncio.gather(*tasks)

        finally:
            await connection.close()

        return self.result

    @staticmethod
    async def get_ton() -> float:
        current_rates = requests.get(
            'https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd').json()
        return current_rates.get('the-open-network', {}).get('usd', 0.0)

    async def __get_data(self, session: aiohttp.ClientSession, url_rate: str, token: str) -> None:
        async with session.get(url_rate, ssl=True) as response:
            obj = json.loads(await response.read())
            if 'result' in obj and len(obj['result']) >= 2 and 'value' in obj['result'][1]:
                self.result[token] = int(obj['result'][1]['value']) / 1e9
            else:
                self.result[token] = None
                raise Exception('Не удалось получить данные')

    @staticmethod
    async def __create_link(info: dict[str, str], block: int) -> str:
        body = "te6ccgEBBAEAHQABGAAAAgEAAAAAO5rKAAECCQQAAEAgAwIAAQgAAA"
        url_rate = f"https://mainnet-v4.tonhubapi.com/block/{block}/" \
                   f"{info['address']}/run/estimate_swap_out/{body}"
        return url_rate

    @staticmethod
    async def __get_client() -> TonlibClient:
        url = 'https://ton.org/global-config.json'

        config = requests.get(url).json()

        keystore_dir = '/tmp/ton_keystore'
        Path(keystore_dir).mkdir(parents=True, exist_ok=True)

        client = TonlibClient(ls_index=2, config=config, keystore=keystore_dir, tonlib_timeout=10)
        await client.init()

        return client
