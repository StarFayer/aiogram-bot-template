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
        await message.answer("Отправьте фильм, который хотите добавить в список для просмотра.\n"
                             f"{db.select_film()}")
        await state.set_state("want_to_watch")
        return
    db.add_film(id=len(db.select_film()) + 1, name=message.from_user.full_name, title=title)
    await message.answer("Фильм добавлен в библиотеку")


@dp.message_handler(state="want_to_watch")
async def adding(message: types.Message, state: FSMContext):
    try:
        title = str(message.text)
        film_template = re.findall(r"\W+", title)
        if film_template and film_template[0] == "/":
            await message.answer("Введите имя фильма, а не команду")
            return
        else:
            db.add_film(id=len(db.select_film()) + 1, name=message.from_user.full_name, title=title)
    except Exception as err:
        logging.info(str(err) + "\n want_to_watch")
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
    db.add_film(id=len(db.select_film()) + 1, name=message.from_user.full_name, title=title, watched=True)
    await message.answer("Фильм добавлен в библиотеку")


@dp.message_handler(state="add_title")
async def adding(message: types.Message, state: FSMContext):
    try:
        title = str(message.text)
        film_template = re.findall(r"\W+", title)
        if film_template[0] != "/":
            db.add_film(id=len(db.select_film()) + 1, name=message.from_user.full_name, title=title, watched=True)
            await message.answer(str(db.select_film()))
        else:
            await message.answer("Введите имя фильма, а не команду")
            return
    except Exception as err:
        await message.answer(f"{err}, {db.select_film()}")
    await message.answer("Фильм добавлен в библиотеку")
    await state.finish()


@dp.message_handler(Command("done"))
async def replace(message: types.Message):
    command = str(message.text)
    film_template = re.findall(r"[^(/done )]\s*\w*", command)
    title = " ".join([word for word in film_template])
    if not title:
        await message.answer("Вы не написали название фильма, повторите попытку\n")
        # print([str(number) for film in db.select_column(column="ToWatch") for number in film], str(title))
        return
    try:
        changed = db.change_column(name=message.from_user.full_name, film=title)
        if changed == "from_watched":
            await message.answer("Отлично, вы посмотрели свой фильм")
        elif changed == "from_to_watch":
            await message.answer("Фильм добавлен в \"Посмотреть позже\"")
        else:
            await message.answer("Такого фильма нет в вашей библиотеке, введите название снова")
            return
    except Exception as err:
        logging.exception(err)
