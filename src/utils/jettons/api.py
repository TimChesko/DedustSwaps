import asyncio
import json

import aiohttp


class FastApi:
    def __init__(self, list_address):
        self.list_address = list_address
        self.result = []
        self.errors = []
        self.parallel_request = 100

    async def gather_with_concurrency(self, conn: aiohttp.TCPConnector, n: int) -> None:
        semaphore = asyncio.Semaphore(n)
        session = aiohttp.ClientSession(connector=conn)

        async def get(address):
            async with semaphore:
                try:
                    url = f"http://tonapi.io/v2/blockchain/accounts/{address}/transactions?before_lt=0&limit=20"
                    async with session.get(url, ssl=False) as response:
                        obj = json.loads(await response.read())
                        self.result.append(obj)
                except Exception as e:
                    self.errors.append({"url": url, "error": str(e)})

        await asyncio.gather(*(get(address) for address in self.list_address))
        await session.close()

    async def run(self) -> list:
        connection = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)

        try:
            await self.gather_with_concurrency(connection, self.parallel_request)
        finally:
            await connection.close()

        if self.errors:
            print(f"Errors: {self.errors}")
        return self.result


urls = [
    "EQAf4BMoiqPf0U2ADoNiEatTemiw3UXkt5H90aQpeSKC2l7f",
    "EQCklyfK3XqZgcceV2jfwuSitrsn3Lv0UQhB3PNnMrXpjWHe",
    "EQCfm8SZAEHn10u263xNEpYmtwimFJmGx0BDnX2GNKOD2qkc"
]

loop = asyncio.get_event_loop()
loop.run_until_complete(FastApi(urls).run())
