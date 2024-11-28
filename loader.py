from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, DB_INFO
from database import BotBase

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
    # parse_mode='MarkdownV2',
    link_preview_is_disabled=True))

dp = Dispatcher(bot=bot, storage=MemoryStorage())
base = BotBase(DB_INFO[0], DB_INFO[1], DB_INFO[2], DB_INFO[3])


async def db_connect():
    """В этой функции идет подключение к БД и проверка ее структуры"""
    await base.connect()
    await base.check_db_structure()
