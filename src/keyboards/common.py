from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def create_btn_transaction(tr: str, work: str, pool: str) -> InlineKeyboardMarkup:
    menu = InlineKeyboardBuilder()
    menu.button(text='Транзакция', url=tr)
    menu.button(text="Адрес обработки токенов", url=work)
    menu.button(text="Адрес обработки тонов", url=pool)

    menu.adjust(1, True)
    return menu.as_markup()
