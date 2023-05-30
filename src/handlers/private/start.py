from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from src.handlers.private.transaction import transaction_info
from asyncpg import Pool

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, db_pool: Pool) -> None:
    args = message.text.split(" ")
    if len(args) > 1:
        if args[1].startswith("transaction"):
            pass
        else:
            await transaction_info(db_pool, message, args[1])
    else:
        await message.answer(message.text)
