import os
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid

from config import ADMINS
from loader import techno_dict, bot, base
from utils.ai_parser import get_casting_data


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
    techno_dict['parser_id'] = (await app.get_me()).id
    await bot.send_message(chat_id=techno_dict['parser_id'], text='Hi!')

    @app.on_message()
    async def my_handler(client: Client, message: Message):
        try:
            casting_data, casting_config = await get_casting_data(message.text)  # Возвращается кортеж
            # Если пришел новый кастинг, то достаем всех актеров и начинаем проверять подходит он им или нет
            all_actors = await base.get_all_actors()
            print(casting_data)
            print(casting_config)
            print()
            print()
            for actor in all_actors:
                print()
                print(actor)
                role_index = 0  # Индекс роли, для списка из casting_data
                for role in casting_config:
                    role_index += 1
                    # Сначала проверяем пол актера
                    if actor['sex'] == role['actor_sex']:
                        print('Sex true')
                        # Проверяем, подходит ли проект актеру
                        if role['project_type'] in actor['projects_interest'].split('+'):
                            print('Project type true')
                            # Проверяем, подходит ли тип роли
                            if role['role_type'] in actor['roles_type_interest'].split('+'):
                                print('Role type true')
                                # Проверяем возраст актера
                                a = [int(i) for i in actor['playing_age'].split('-')]  # Игровой диапазон актера
                                a.sort()
                                b = [int(i) for i in
                                     role['age_restrictions'].split('-')]  # Возрастной диапазон для роли
                                b.sort()
                                if a[0] >= b[0] >= a[1] or a[0] <= b[1] <= a[1]:  # noqa
                                    # print(actor)
                                    print(role)
                                    role_info = casting_data['role_description'][role_index - 1]
                                    msg_text = (f'Пол актера: {role_info["actor_sex"]}\n'
                                                f'Возраст актера: {role_info["age_restrictions"]}\n'
                                                f'Название роли: {role_info["role_name"]}\n'
                                                f'Тип роли: {role_info["role_type"]}\n'
                                                f'Описание роли: {role_info["role_description"]}\n'
                                                f'Дополнительные требования: {role_info["additional_requirements"]}\n'
                                                f'Гонорар: {role_info["fee"]}\n')
                                    await bot.send_message(chat_id=actor['user_id'], text=msg_text)
                                else:
                                    print(a, b)
                            else:
                                print(role['role_type'], actor['roles_type_interest'].split('+'))
                        else:
                            print(role['project_type'], actor['projects_interest'].split('+'))
                    else:
                        print(actor['sex'], role['actor_sex'])


        except TypeError as e:  # Значит не кастинг
            print(e)
            pass


async def parser_stop():
    """Останавливаем работу парсера"""
    # Если вернется True значит парсер включен
    if await techno_dict['parser'].check_status():
        await techno_dict['parser'].switch_status()


async def parser_status():
    """Проверяем статус парсера"""
    return await techno_dict['parser'].check_status()
