from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("watch", "Добавить фильм в \"Посмотреть позже\""),
        types.BotCommand("watched", "Добавить фильм в \"Просмотрено\""),
        types.BotCommand("done", "Фильм из списка желаемого просмотрен"),
        types.BotCommand("to_watch_list", "Список \"Посмотреть позже\""),
        types.BotCommand("watched_list", "Список \"Просмотрено\""),
        types.BotCommand("delete", "Удалить фильм из библиотеки"),
    ])
