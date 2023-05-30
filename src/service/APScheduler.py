from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Dispatcher

from src.models.jettons_info.get import JettonsInfo
from src.service.jettons.process import ProcessJettons

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


async def jetton_rates(start: bool, dp: Dispatcher):
    jettons_info = await JettonsInfo(dp['db_pool']).get_all()
    await ProcessJettons(dp, jettons_info, start).update_rates()


def setup(dp: Dispatcher):
    scheduler.add_job(jetton_rates, args=[True, dp])
    scheduler.add_job(jetton_rates, 'interval', args=[False, dp], seconds=30)
    scheduler.start()
