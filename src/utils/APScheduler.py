from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


async def jetton_rates():
    await get_all_address()


def setup():
    scheduler.add_job(jetton_rates, 'interval', seconds=30)
    scheduler.start()
