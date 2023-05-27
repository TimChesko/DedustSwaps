import asyncio

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis

from src import utils
from src.data import config
from src.database.process import DataBase
from src.database.create import CreateTables
from src.handlers import private
from src.service import APScheduler


async def set_handlers(dp: Dispatcher) -> None:
    dp.include_router(private.router)


async def set_middlewares() -> None:
    pass


async def set_logging(dp: Dispatcher) -> None:
    dp["aiogram_logger_init"] = {"type": "aiogram"}
    dp["aiogram_logger"] = utils.logging.setup_logger().bind(
        **dp["aiogram_logger_init"]
    )


async def setup_aiogram(dp: Dispatcher) -> None:
    await set_logging(dp)
    logger = dp["aiogram_logger"]
    logger.debug("Configuring aiogram")
    await set_handlers(dp)
    await set_middlewares()
    logger.info("Configured aiogram")


async def set_database(dp: Dispatcher) -> None:
    dp['db_pool'] = await DataBase(None).create_db_connection(config)
    await CreateTables(dp['db_pool']).process()


async def on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await set_database(dispatcher)
    await setup_aiogram(dispatcher)
    APScheduler.setup(dispatcher)
    dispatcher["aiogram_logger"].info("Started polling")


async def on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await DataBase(dispatcher['db_pool']).close_db_connection()
    await bot.session.close()
    dispatcher["aiogram_logger"].info("Stopping polling")


async def main() -> None:
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
