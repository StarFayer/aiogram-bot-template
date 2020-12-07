from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, db


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    db.add_user(name=message.from_user.full_name)
    await message.answer('\n'.join([f'Добро пожаловать, {message.from_user.get_mention()}!',
                                    f"Этот бот поможет вам в том, чтобы хранить фильмы и напоминать о том, что вы хотели их посмотреть",
                                    f"Напишите /watched, чтобы добавить первые фильмы в вашу библиотеку \"Просмотрено\"",
                                    f"Напишите /help, чтобы ознакомиться со всеми командами"]))

