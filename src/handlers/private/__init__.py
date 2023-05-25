
from aiogram import Router, F

from . import start

router = Router()

router.message.filter(F.chat.type == "private")

router.include_router(start.router)
