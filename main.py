import asyncio
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from db import init_db, get_player, add_player, update_player, aiosqlite

API_TOKEN = '7215822619:AAH4nCjSaZu1JLeTmc4jKL2DVgUIcSZdPrM'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

WEBAPP_URL = 'https://scarllexx.github.io/PNClickerBot/'


async def on_startup():
    await init_db()


@router.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    player = await get_player(user_id)

    if player is None:
        await add_player(user_id, username)

    webapp_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Play Clicker',
                              web_app=WebAppInfo(url=WEBAPP_URL))]
    ])

    await message.answer("Welcome to the Clicker Game!", reply_markup=webapp_keyboard)


@router.message(Command("stats"))
async def show_stats(message: types.Message):
    user_id = message.from_user.id
    player = await get_player(user_id)

    if player:
        stats_message = f"Points: {player[2]}\nClick Power: {
            player[3]}\nEnergy: {player[4]}"
        await message.answer(stats_message)
    else:
        await message.answer("You are not registered yet. Use /start to begin playing.")


async def autobot_check():
    while True:
        async with aiosqlite.connect('clicker.db') as db:
            async with db.execute('SELECT * FROM players WHERE autobot_active = 1') as cursor:
                players = await cursor.fetchall()
                for player in players:
                    user_id = player[0]
                    autobot_end_time = player[6]
                    if datetime.datetime.now().timestamp() > autobot_end_time:
                        await update_player(user_id, autobot_active=0)
                    else:
                        points = player[2] + player[3]
                        await update_player(user_id, points=points)
        await asyncio.sleep(60)


async def main():
    await on_startup()
    loop = asyncio.get_event_loop()
    loop.create_task(autobot_check())
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
