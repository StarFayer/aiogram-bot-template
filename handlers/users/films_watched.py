import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

import re

from loader import dp, db


@dp.message_handler(Command("watch"))
async def to_watch(message: types.Message, state: FSMContext):
    command = str(message.text)
    film_template = re.findall(r"[^(/watch )]\s*\w*", command)
    title = " ".join([word for word in film_template])
    if not title:
        await message.answer("Отправьте фильм, который хотите добавить в список для просмотра.\n")
        await state.set_state("want_to_watch")
        return
    db.add_film(name=message.from_user.full_name, title=title, watched=True)
    await message.answer("Фильм добавлен в библиотеку")


@dp.message_handler(state="want_to_watch")
async def adding(message: types.Message, state: FSMContext):
    try:
        title = str(message.text)
        db.add_film(name=message.from_user.full_name, title=title)
    except Exception as err:
        logging.info(str(err)+"\n want_to_watch")
    await message.answer("Фильм добавлен в библиотеку")
    await state.finish()


@dp.message_handler(Command("watched"))
async def new_film(message: types.Message, state: FSMContext):
    command = str(message.text)
    film_template = re.findall(r"[^(/watched )]\s*\w*", command)
    title = " ".join([word for word in film_template])
    if not title:
        await message.answer("Отправьте фильм, который хотите добавить в список просмотренных.\n"
                             f"По желанию можете оставить к нему свою заметку. - ПОКА НЕ РАБОТАЕТ")
        await state.set_state("add_title")
        return
    db.add_film(name=message.from_user.full_name, title=title, watched=True)
    await message.answer("Фильм добавлен в библиотеку")


@dp.message_handler(state="add_title")
async def adding(message: types.Message, state: FSMContext):
    try:
        title = str(message.text)
        db.add_film(name=message.from_user.full_name, title=title, watched=True)
    except Exception as err:
        await message.answer(str(err))
    await message.answer("Фильм добавлен в библиотеку")
    await state.finish()


@dp.message_handler(Command("done"))
async def replace(message: types.Message):
    command = str(message.text)
    film_template = re.findall(r"[^(/watch )]\s*\w*", command)
    title = " ".join([word for word in film_template])
    if not title:
        await message.answer("Вы не написали название фильма, повторите попытку")
        return
    try:
        db.change_column(name=await message.from_user.full_name, title=title)
        await message.answer("Отлично, вы посмотрели свой фильм")
    except Exception as err:
        logging.exception(err)
