from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


async def jetton_rates():
    print('I`m Working!')


def setup():
    scheduler.add_job(jetton_rates, 'interval', seconds=15)
    scheduler.start()
