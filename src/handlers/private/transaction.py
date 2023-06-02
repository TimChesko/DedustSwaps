from aiogram.types import Message, InlineKeyboardMarkup
from asyncpg import Pool

from src.keyboards.common import create_btn_transaction
from src.models.all_rates.get import GetterAllRates
from src.models.jetton_rate.get import GetterJettonRate
from src.models.jettons_info.get import JettonsInfo


async def transaction_info(pool: Pool, message: Message, hash_tr: str) -> None:
    hash_tr = hash_tr.replace("transaction", "")
    text, buttons = await create_text_and_buttons(pool, hash_tr)
    await message.answer(text=text, parse_mode='HTML', reply_markup=buttons)


async def create_text_and_buttons(pool: Pool, hash_tr: str) -> tuple[str, InlineKeyboardMarkup]:
    info = await GetterJettonRate(pool).get_transaction_by_hash(hash_tr)
    tiker = info['jetton']
    transaction_type = '🟢 #BUY' if info['value'] < 0 else '🔴 #SELL'
    value = info['value'] * -1 if info['value'] < 0 else info['value']
    link_tr = f"https://tonviewer.com/transaction/{hash_tr}"
    time = info['time'].strftime('%Y-%m-%d %H:%M:%S')

    v_today = round((await GetterJettonRate(pool).get_volume_by_time(tiker, 1))['sum'], 2)
    v_weak = round((await GetterJettonRate(pool).get_volume_by_time(tiker, 7))['sum'], 2)
    p_today = round((await GetterJettonRate(pool).get_pool_by_time(tiker, 1))['sum'], 2)
    p_weak = round((await GetterJettonRate(pool).get_pool_by_time(tiker, 7))['sum'], 2)

    last_rate = await GetterAllRates(pool).last_all_rates()
    text = f"<b>{transaction_type} #{tiker}\n" \
           f"{round(value, 1)}</b> " \
           f"({round(value / last_rate[tiker.lower()], 2)} TON / " \
           f"${round((value / last_rate[tiker.lower()]) / last_rate['ton'], 2)})\n" \
           f"💱 <b>{round(last_rate[tiker.lower()], 2)}</b> / " \
           f"${round(1 / last_rate[tiker.lower()] / last_rate['ton'], 3)}\n" \
           f"{time}\n\n" \
           f"Дни: <b>1 | 7</b>\n\n" \
           f"Статистика токена\n" \
           f"Объем продаж: <b>{v_today} | {v_weak}</b>\n" \
           f"Объем пула: <b>{p_today} | {p_weak}</b>\n\n" \
           f"Статистика адреса:\n" \
           f"<code>Egfgjk22134kjj</code>\n" \
           f"Количество транз: <b>2 | 17</b>\n" \
           f"Объем транзакций: <b>1000 | 20000</b>\n" \
           f"Профит 💎: <b>-101 | +2023</b>\n" \
           f"В процентах: <b>-5% | +16%</b>\n\n" \
           f"<b>@dedustSwaps | @tonnull</b>"

    # text = f"<b>{transaction_type} #{tiker}\n" \
    #        f"{round(value, 1)}</b> " \
    #        f"({round(value / last_rate[tiker.lower()], 2)} TON / " \
    #        f"${round((value / last_rate[tiker.lower()]) / last_rate['ton'], 2)})\n" \
    #        f"💱 <b>{round(last_rate[tiker.lower()], 2)}</b> / " \
    #        f"${round(1 / last_rate[tiker.lower()] / last_rate['ton'], 3)}\n" \
    #        f"{time}\n\n" \
    #        f"Объем продаж:\n" \
    #        f"<code>1 день: {v_today}\n</code>" \
    #        f"<code>7 дней: {v_weak}\n\n</code>" \
    #        f"Объем пула:\n" \
    #        f"<code>1 день: {p_today}\n</code>" \
    #        f"<code>7 дней: {p_weak}</code>\n\n" \
    #        f"Статистика адреса по дням:\n" \
    #        f"Количество / объем транзакций (token) |\n" \
    #        f"Профит (ton)/ в процентном соотношении\n" \
    #        f"<code>1 день: 2 / 100 | +2 / +0.01%</code>\n" \
    #        f"<code>7 дней: 17 / 20000 | +2023 / +5.0%</code>\n\n" \
    #        f"<b>@dedustSwaps | @tonnull</b>"

    token_info = await JettonsInfo(pool).get_address_by_token(tiker)
    link_work = f"https://tonviewer.com/{token_info['work_address']}"
    link_pool = f"https://tonviewer.com/{token_info['pool_address']}"
    buttons = await create_btn_transaction(link_tr, link_work, link_pool)

    return text, buttons
