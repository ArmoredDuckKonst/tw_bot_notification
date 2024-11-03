import logging
from aiogram import Bot, Dispatcher, types, html
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
import sys
import asyncio
import datetime
from db_config import session, User, Shift, D_shift, sessionmaker, engine





logging.basicConfig(level=logging.INFO)

API_TOKEN = '7137709814:AAHiUPlk3co_P2UBjDfePVQ7Xg-zfxtjHKQ'
GROUP_ID = -4594917612
USER_ID = 123456789

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()


def get_d_operator():
    today = datetime.date.today()
    operator = session.query(D_shift).filter(D_shift.date == today, D_shift.shift == "t").first()  # Сменщик сейчас
    if operator is None:
        tg_id = None
    else:
        user_id = operator.user_id
        tg = session.query(User).filter(User.id == user_id).first()
        tg_id = tg.tg_id
    return tg_id


def get_n_operator():
    today = datetime.date.today()
    operator = session.query(Shift).filter(Shift.date == today, Shift.shift == "t").first()  # Сменщик сейчас
    if operator is None:
        tg_id = None
    else:
        user_id = operator.user_id
        tg = session.query(User).filter(User.id == user_id).first()
        tg_id = tg.tg_id
        return tg_id

async def send_n_notification():
    tg_id = get_n_operator()
    if tg_id is None:
        await bot.send_message(GROUP_ID, "Ночной дежурный не установлен на сегодня.", parse_mode='HTML')
    else:
        operator = session.query(User).filter(User.tg_id == tg_id).first()
        mention = f"<a href='tg://user?id={tg_id}'>{operator.name}</a>"
        message = f"Привет, @{mention}! Сегодня ты закрываешь опер. день!."
        await bot.send_message(GROUP_ID, message, parse_mode='HTML')


async def send_d_notification():
    tg_id = get_d_operator()
    if tg_id is None:
        await bot.send_message(GROUP_ID, "Дневной дежурный не установлен на сегодня.", parse_mode='HTML')
    else:
        operator = session.query(User).filter(User.tg_id == tg_id).first()
        mention = f"<a href='tg://user?id={tg_id}'>{operator.name}</a>"
        message = f"Привет, {mention}! Проверь утренний клиринг!."
        await bot.send_message(GROUP_ID, message, parse_mode='HTML')


async def send_msg():
    await bot.send_message(GROUP_ID, "Бот запущен.", parse_mode='HTML')


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    tg_id = message.from_user.id
    user_name = message.from_user.username
    if user_name is None:
        user_name = message.from_user.full_name
        mention = f"<a href='tg://user?id={tg_id}'>{user_name}</a>"
    else:
        mention = f"<a href='tg://user?id={tg_id}'>{user_name}</a>"
    msg_text = f"Привет, {mention}! Я буду отправлять тебе оповещения."
    await message.answer(msg_text)
    await send_msg()



async def set_new_n_shift():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    operator = session.query(Shift).filter(Shift.date == today, Shift.shift == "t").first() #Сменщик сейчас

    if operator is None:
        #Найти последнего активного сменщика
        last_operator = session.query(Shift).filter(Shift.shift == "t").order_by(Shift.id.desc()).first()
        last_operator.shift = "f"
        session.commit()
        delta = (today - last_operator.date).days
        if delta > 4:
            id = last_operator.user_id + (delta % 4)
        else:
            id = last_operator.user_id + delta
        if id > 4:
            id = 1
        new_operator = Shift(user_id=id+1, date=tomorrow, shift='t')
        session.add(new_operator)
        session.commit()
    else:
        operator = session.query(Shift).filter(Shift.date == today).first()
        operator.shift = "f"
        session.commit()
        new_operator_id = operator.user_id + 1
        if new_operator_id > 4:
            new_operator_id = 1
        new_operator = Shift(user_id=new_operator_id, date=tomorrow, shift='t')
        session.add(new_operator)
        session.commit()
    await bot.send_message(GROUP_ID, f"Ночной дежурный на завтра - {tomorrow} установлен.", parse_mode='HTML')


async def set_new_d_shift():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    operator = session.query(D_shift).filter(D_shift.date == today, D_shift.shift == "t").first() #Сменщик сейчас


    if operator is None:
        #Найти последнего активного сменщика
        last_operator = session.query(D_shift).filter(D_shift.shift == "t").order_by(D_shift.id.desc()).first()
        last_operator.shift = "f"
        session.commit()
        delta = (today - last_operator.date).days
        if delta > 4:
            id = last_operator.user_id + (delta % 4)
        else:
            id = last_operator.user_id + delta
        if id > 4:
            id = 1
        new_operator = D_shift(user_id=id+1, date=tomorrow, shift='t')
        session.add(new_operator)
        session.commit()
    else:
        operator = session.query(D_shift).filter(D_shift.date == today).first()
        operator.shift = "f"
        session.commit()
        new_operator_id = operator.user_id + 1
        if new_operator_id > 4:
            new_operator_id = 1
        new_operator = D_shift(user_id=new_operator_id, date=tomorrow, shift='t')
        session.add(new_operator)
        session.commit()
    await bot.send_message(GROUP_ID, f"Дневной дежурный на завтра - {tomorrow} установлен.", parse_mode='HTML')



async def set_shifts_for_tomorrow():
    await set_new_d_shift()
    await set_new_n_shift()

async def n_notification():
    await send_n_notification()


async def d_notification():
    await send_d_notification()


scheduler.add_job(set_shifts_for_tomorrow, 'cron', hour=23, minute=45)
scheduler.add_job(d_notification, 'cron', hour=7, minute=45)
scheduler.add_job(d_notification, 'cron', hour=8, minute=0)
scheduler.add_job(n_notification, 'cron', hour=23, minute=15)
scheduler.add_job(n_notification, 'cron', hour=23, minute=30)



async def on_startup():
    await send_msg()
    #await
    #await send_d_notification()
    scheduler.start()
dp.startup.register(on_startup)


async def main() -> None:
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
