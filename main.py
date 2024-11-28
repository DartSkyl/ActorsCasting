import asyncio
import datetime

import handlers  # noqa
from loader import dp, bot, db_connect


async def start_up():
    # Подключаемся к БД
    await db_connect()
    with open('bot.log', 'a') as log_file:
        log_file.write(f'\n========== New bot session {datetime.datetime.now()} ==========\n\n')
    print('Стартуем')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(start_up())
    except KeyboardInterrupt:
        print('Хорош, бро')
