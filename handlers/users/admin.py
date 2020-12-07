from aiogram import types
from aiogram.dispatcher.filters import Command

from filters.adminfilter import IsPrivate
from loader import dp, db


@dp.message_handler(Command("users"), IsPrivate())
async def get_db(message: types.Message):
    users = db.select_column(everyone=True)
    await message.answer(f"Список всех пользоватлей:\n"
                         f"{users}")
