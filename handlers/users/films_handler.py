import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

import re

from loader import dp, db


@dp.message_handler(Command("watch"))
async def to_watch(message: types.Message, state: FSMContext):
    command = str(message.text)
    film_template = re.findall(r"[^/watch ]\w+", command)
    print(film_template)
    title = " ".join([word for word in film_template])
    if not title:
        await message.answer("Отправьте фильм, который хотите добавить в список для просмотра.\n"
                             f"{db.select_all()}")
        await state.set_state("want_to_watch")
        return
    add_film = db.add_film(name=message.from_user.full_name, title=title)
    if not add_film:
        await message.answer("Этот фильм уже в вашей библиотеке")
    else:
        await message.answer("Фильм добавлен в библиотеку")


@dp.message_handler(state="want_to_watch")
async def adding(message: types.Message, state: FSMContext):
    try:
        title = str(message.text)
        if title == "/exit":
            await message.answer("Вы отменили запрос")
            await state.finish()
            return
        film_template = re.findall(r"\W+", title)
        if film_template and film_template[0] == "/":
            await message.answer("Введите название фильма, а не команду")
            return
        else:
            add_film = db.add_film(name=message.from_user.full_name, title=title)
            if not add_film:
                await message.answer("Этот фильм уже в вашей библиотеке")
            else:
                await message.answer("Фильм добавлен в библиотеку")
    except Exception as err:
        logging.info(str(err) + "\n want_to_watch")
    await state.finish()


@dp.message_handler(Command("watched"))
async def new_film(message: types.Message, state: FSMContext):
    command = str(message.text)
    film_template = re.findall(r"[^/watched ]\w+", command)
    title = " ".join([word for word in film_template])
    if not title:
        await message.answer("Отправьте фильм, который хотите добавить в список просмотренных.\n"
                             f"По желанию можете оставить к нему свою заметку. - ПОКА НЕ РАБОТАЕТ")
        await state.set_state("add_title")
        return
    add_film = db.add_film(name=message.from_user.full_name, title=title, watched=True)
    if not add_film:
        await message.answer("Этот фильм уже в вашей библиотеке")
    else:
        await message.answer("Фильм добавлен в библиотеку")


@dp.message_handler(state="add_title")
async def adding(message: types.Message, state: FSMContext):
    try:
        title = str(message.text)
        if title == "/exit":
            await message.answer("Вы отменили запрос")
            await state.finish()
            return
        film_template = re.findall(r"\W*", title)
        if film_template and film_template[0] == "/":
            await message.answer("Введите название фильма, а не команду")
            return
        else:
            add_film = db.add_film(name=message.from_user.full_name, title=title, watched=True)
            if not add_film:
                await message.answer("Этот фильм уже в вашей библиотеке")
            else:
                await message.answer("Фильм добавлен в библиотеку")
            await message.answer(str(db.select_all()))
    except Exception as err:
        await message.answer(f"{err}, {db.select_all()}")
    await state.finish()


@dp.message_handler(Command("done"))
async def replace(message: types.Message, state: FSMContext):
    command = str(message.text)
    film_template = re.findall(r"[^/done ]\w+", command)
    title = " ".join([word for word in film_template])
    if not title:
        await message.answer("Напишите название просмотренного фильма")
        await state.set_state("getting_done")
        return
    try:
        changed = db.change_column(name=message.from_user.full_name, film=title)
        if changed == "from_to_watch":
            await message.answer("Отлично, вы посмотрели свой фильм")
        elif changed == "from_watched":
            await message.answer("Фильм добавлен в \"Посмотреть позже\"")
        else:
            await message.answer("Такого фильма нет в вашей библиотеке, введите название снова")
            return
    except Exception as err:
        logging.exception(err)


@dp.message_handler(state="getting_done")
async def getting_done(message: types.Message, state: FSMContext):
    try:
        title = str(message.text)
        if title == "/exit":
            await message.answer("Вы отменили запрос")
            await state.finish()
            return
        film_template = re.findall(r"\W*", title)
        if film_template and film_template[0] == "/":
            await message.answer("Введите название фильма, а не команду")
            return
        else:
            changed = db.change_column(name=message.from_user.full_name, film=title)
            if changed == "from_to_watch":
                await message.answer("Отлично, вы посмотрели свой фильм")
            elif changed == "from_watched":
                await message.answer("Фильм добавлен в \"Посмотреть позже\"")
            else:
                await message.answer("Такого фильма нет в вашей библиотеке, введите название снова")
                return
    except Exception as err:
        logging.exception(err)
    await state.finish()


@dp.message_handler(Command("delete"))
async def delete_film(message: types.Message, state: FSMContext):
    command = str(message.text)
    film_template = re.findall(r"[^/delete ]\w+", command)
    title = " ".join([word for word in film_template])
    print(title)
    if not title:
        await message.answer("Введите название фильма, который вы хотите удалить")
        await state.set_state("deleting")
        return
    try:
        delete_film = db.delete_film(name=message.from_user.full_name, title=title)
        if not delete_film:
            await message.answer("Такого фильма нет в библиотеке, повторите попытку")
            return
        else:
            await message.answer(f"Вы удалили фильм {title}")
    except Exception as err:
        await message.answer(str(err))


@dp.message_handler(state="deleting")
async def deleting(message: types.Message, state: FSMContext):
    try:
        title = str(message.text)
        if title == "/exit":
            await message.answer("Вы отменили запрос")
            await state.finish()
            return
        film_template = re.findall(r"\W*", title)
        if film_template and film_template[0] == "/":
            await message.answer("Введите название фильма, а не команду")
            return
        else:
            delete_film = db.delete_film(name=message.from_user.full_name, title=title)
            if not delete_film:
                await message.answer("Такого фильма нет в библиотеке, повторите попытку")
                return
            else:
                await message.answer(f"Вы удалили фильм {title}")
    except Exception as err:
        await message.answer(str(err))
    await state.finish()


