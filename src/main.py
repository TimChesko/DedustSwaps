import asyncio

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis

from src.data import config
from src.database.connection import DataBase
from src.handlers import private


async def set_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(private.router)


async def set_middlewares() -> None:
    pass


async def setup_aiogram(dispatcher: Dispatcher) -> None:
    await set_handlers(dispatcher)
    await set_middlewares()


async def on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    dispatcher['config'] = config
    dispatcher['db_pool'] = await DataBase(dispatcher).create_db_connection()
    await setup_aiogram(dispatcher)


async def on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping polling")
    await DataBase(dispatcher).close_db_connection(dispatcher['db_pool'])
    await bot.session.close()


async def main() -> None:
    # APScheduler.setup()
    bot = Bot(config.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(
        storage=RedisStorage(
            redis=Redis(
                host=config.FSM_HOST,
                password=None,
                port=config.FSM_PORT,
                db=0,
            )
        )
    )

    dp.startup.register(on_startup_polling)
    dp.shutdown.register(on_shutdown_polling)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
