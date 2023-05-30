from aiogram import Dispatcher, Bot

from src.data import config


class MsgWork:

    def __init__(self, dp: Dispatcher):
        self.bot: Bot = dp['bot']
        self.config = config

    async def send_msg_array(self, arr_text: list[str]) -> None:
        for msg in arr_text:
            await self.bot.send_message(chat_id=self.config.CHANNEL_ID, text=msg, parse_mode="HTML")
