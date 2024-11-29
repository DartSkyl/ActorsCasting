import os
from pyrogram import Client
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid

from loader import techno_dict


class UserBotParser:
    def __init__(self, api_id: int = None, api_hash: str = None, phone_number: str = None):
        self._name = 'CastingParser'
        self._api_id = api_id
        self._api_hash = api_hash
        self._phone_number = phone_number
        self._client = Client(name=f'{self._name}', api_id=api_id, api_hash=api_hash, phone_number=phone_number)
        self.status = False

    async def start_session(self):
        """Здесь происходит авторизация аккаунта. Запрашиваем код и возвращаем хэш кода"""
        await self._client.connect()
        code_info = await self._client.send_code(self._phone_number)
        return code_info.phone_code_hash

    async def authorization_and_start(self, code_hash: str, code: str):
        """Здесь заканчиваем авторизацию и запускаемся"""
        await self._client.sign_in(phone_number=self._phone_number, phone_code_hash=code_hash, phone_code=code)
        await self._client.disconnect()

    async def create_app(self):
        """Возвращаем клиента для создания приложения"""
        return self._client

    async def check_status(self):
        """Возвращает статус парсера, True если запущен"""
        return self.status

    async def switch_status(self):
        """Переключаем статус парсера"""
        if self.status:
            self.status = False
            await self._client.stop()
        else:
            self.status = True
            await self._client.start()


async def parser_load():
    if os.path.isfile('CastingParser.session'):
        techno_dict['parser'] = UserBotParser()
    else:
        print('Юзер бот не подключен')


async def parser_start():
    """Запускаем паресер"""
    app = await techno_dict['parser'].create_app()
    # Запускаем парсер
    await techno_dict['parser'].switch_status()

    @app.on_message()
    async def my_handler(client, message):
        print(message)
        # await message.forward("me")


async def parser_stop():
    """Останавливаем работу парсера"""
    # Если вернется True значит парсер включен
    if await techno_dict['parser'].check_status():
        await techno_dict['parser'].switch_status()


async def parser_status():
    """Проверяем статус парсера"""
    return await techno_dict['parser'].check_status()
