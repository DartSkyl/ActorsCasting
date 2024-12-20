import asyncio
import datetime
from aiogram.types import BotCommand

from utils.admin_router import admin_router
from utils.users_router import users_router
from utils.user_bot_parser import parser_load, parser_start
from utils.sales_funnel import SalesFunnel
import handlers  # noqa
from loader import dp, bot, db_connect, get_bot_id, techno_dict


async def start_up():
    # Подключаемся к БД
    await db_connect()
    # Подключаем парсер, если он есть
    await parser_load()
    # Сохраняем ID бота для дальнейших операций
    await get_bot_id()
    # Для напоминания о себе
    techno_dict['sales_funnel'] = SalesFunnel()
    # Подключаем роутеры
    dp.include_router(admin_router)
    dp.include_router(users_router)
    await bot.set_my_commands([
        # BotCommand(command='start', description='Главное меню и рестарт'),
        BotCommand(command='favorites', description='Избранное'),
        BotCommand(command='subscription', description='Управление подпиской'),
        BotCommand(command='support', description='Контакт службы поддержки'),
        BotCommand(command='settings', description='Настройки аккаунта')
    ])
    await parser_start()
    with open('bot.log', 'a') as log_file:
        log_file.write(f'\n========== New bot session {datetime.datetime.now()} ==========\n\n')
    print('Стартуем')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(start_up())
    except KeyboardInterrupt:
        print('Хорош, бро')
