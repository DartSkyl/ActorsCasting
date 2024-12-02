import asyncio
import datetime

from utils.admin_router import admin_router
from utils.users_router import users_router
from utils.user_bot_parser import parser_load
import handlers  # noqa
from loader import dp, bot, db_connect, get_bot_id


async def start_up():
    # Подключаемся к БД
    await db_connect()
    await parser_load()
    await get_bot_id()
    # Подключаем роутеры
    dp.include_router(admin_router)
    dp.include_router(users_router)
    with open('bot.log', 'a') as log_file:
        log_file.write(f'\n========== New bot session {datetime.datetime.now()} ==========\n\n')
    print('Стартуем')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(start_up())
    except KeyboardInterrupt:
        print('Хорош, бро')
