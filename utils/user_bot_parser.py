import os
import json
from pydantic_core._pydantic_core import ValidationError
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums.message_media_type import MessageMediaType
from pyrogram.errors.exceptions.not_acceptable_406 import ChatForwardsRestricted

from aiogram.types.chat_member_member import ChatMemberMember
from aiogram.types.chat_member_left import ChatMemberLeft
from aiogram.types import FSInputFile

from asyncpg.exceptions import UniqueViolationError, PostgresSyntaxError

from loader import techno_dict, bot, base
from utils.ai_parser import get_casting_data
from keyboards.inline_actors import button_for_casting
from config import CONTROL_GROUP, PUBLIC_CHANNEL


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

    async def forward_origin_message(self, user_id, origin_chat, origin_message):
        """Метод перебрасывает оригинальное сообщение из чата в личку к боту,
        что бы оттуда перебросить к пользователю"""
        # Что бы перебросить сообщение от бота к пользователю будем использовать эту причудливую
        # конструкцию. Сохраним в заранее созданный список словарь, где ключ это ID пользователя,
        # который запросил оригинал, а значение это информация об источнике и искомом сообщении.
        # Когда переброшенное сообщение прейдет от парсера к боту, мы достанем информацию из пересланного сообщения и
        # сравним ее с той что храниться в списке
        techno_dict['forwarding'].append({user_id: str(origin_chat) + '_' + str(origin_message)})
        try:
            await self._client.forward_messages(
                chat_id=techno_dict['bot_id'],
                from_chat_id=origin_chat,
                message_ids=origin_message
            )
        except ChatForwardsRestricted:  # Если пересылка запрещена
            techno_dict['forwarding'].remove({user_id: str(origin_chat) + '_' + str(origin_message)})
            msg_text = await self._client.get_messages(
                chat_id=origin_chat,
                message_ids=origin_message
            )
            try:
                await bot.send_message(chat_id=user_id, text=msg_text.text)
            except ValidationError:
                await bot.send_message(chat_id=user_id, text=msg_text.caption)

        except Exception as e:  # Проблема новых каналов\групп
            with open('print.log', 'a') as log_file:
                log_file.write(f'\n====================\n{str(e)}\n')
            await bot.send_message(chat_id=user_id, text='Оригинал больше не доступен!')
            techno_dict['forwarding'].remove({user_id: str(origin_chat) + '_' + str(origin_message)})

    async def check_text_for_prob(self, user_id, origin_chat, next_origin_message):
        """Этим методом проверяем есть ли текст проб в следующем сообщении в виде файла"""
        try:
            prob_text = await self._client.get_messages(chat_id=origin_chat, message_ids=next_origin_message)
            if prob_text.media == MessageMediaType.DOCUMENT:
                techno_dict['forwarding'].append({user_id: str(origin_chat) + '_' + str(next_origin_message)})
                await self._client.forward_messages(
                    chat_id=techno_dict['bot_id'],
                    from_chat_id=origin_chat,
                    message_ids=next_origin_message
                )
                return True
            return False
        except Exception as e:
            print(e)
            return False


async def check_paid(user_id):
    """Бот подключен к платежной системе paywall. У них контроль подписки осуществляется через контрольный "закрытый"
    канал. Т.е. если подписчик в этом канале есть, значит подписка оплачена и наоборот. Так что будем проверять наличие
    пользователя в группе на предмет оплаченной подписки. Если вы ничего не поняли, у меня для вас плохие новости"""
    is_paid = await bot.get_chat_member(chat_id=CONTROL_GROUP, user_id=user_id)
    if not isinstance(is_paid, ChatMemberLeft):
        return True
    return False


async def parser_load():
    if os.path.isfile('CastingParser.session'):
        techno_dict['parser'] = UserBotParser()
    else:
        print('Юзер бот не подключен')


async def for_tests(casting_data, casting_config, casting_contacts, casting_rights):
    msg_text = (f'<b>Название проекта:</b> {casting_data["project_name"]}\n'
                f'<b>Даты съемок:</b> {casting_data["filming_dates"]}\n'
                f'<b>Тип проекта:</b> {casting_data["project_type"]}\n\n')

    for role_info in casting_data['role_description']:
        additional_requirements = role_info["additional_requirements"] if role_info.get(
            'additional_requirements') else 'Не указан'
        msg_text += (f'<b>Пол актера:</b> {role_info["actor_sex"]}\n'
                     f'<b>Возраст актера:</b> {role_info["age_restrictions"]}\n'
                     f'<b>Название роли:</b> {role_info["role_name"]}\n'
                     f'<b>Описание роли:</b> {role_info["role_description"]}\n'
                     f'<b>Дополнительные требования:</b> {additional_requirements}\n'
                     f'<b>Гонорар:</b> {role_info["fee"]}\n\n')
    msg_text += (f'<b>Заявки отправлять:</b> {casting_contacts["contacts"]}\n'
                 f'<b>Правила оформления заявок:</b> {casting_contacts["rules"]}\n')

    if casting_rights:
        msg_text += f'<b>Права:</b> {casting_rights["rights"]}\n'
    print(casting_config)
    await bot.send_message(chat_id=1004280953, text=msg_text)


async def parser_start():
    """Запускаем паресер"""
    app = await techno_dict['parser'].create_app()
    # Запускаем парсер
    await techno_dict['parser'].switch_status()
    techno_dict['parser_id'] = (await app.get_me()).id
    await bot.send_message(chat_id=techno_dict['parser_id'], text='Hi!')

    @app.on_message()
    async def my_handler(client: Client, message: Message):
        """Сердце бота. Здесь мы отправляем сообщение ИИ, после чего отправляем результат актерам"""
        try:
            pict = False
            casting_text = message.text
            # Если файл с описанием, то текст будет None. Значит возьмем его из caption
            if message.media == MessageMediaType.PHOTO:
                pict = True
                casting_text = message.caption
            casting_data, casting_config, casting_contacts, casting_rights, casting_hash = await get_casting_data(casting_text)  # Возвращается кортеж
            # if message.forward_from_chat:
            #     chat_id, message_id = message.forward_from_chat.id, message.forward_from_message_id
            # else:
            #     chat_id, message_id = message.chat.id, message.id

            # await for_tests(casting_data, casting_config, casting_contacts, casting_rights)
            try:
                # И публикуем в закрытом канале в качестве оригинала
                if not pict:
                    m = await bot.send_message(chat_id=PUBLIC_CHANNEL, text=casting_text)
                else:
                    m = await bot.send_photo(chat_id=PUBLIC_CHANNEL, photo=message.photo.file_id, caption=casting_text)
                # Сохраняем в базу
                await base.add_new_casting(
                    casting_hash=casting_hash,
                    casting_data=json.dumps(casting_data),
                    casting_config=json.dumps(casting_config),
                    casting_origin=f'https://t.me/{message.chat.username}/{message.id}',
                    origin_for_user=m.message_id
                )
                # Если пришел новый кастинг, то достаем всех актеров и начинаем проверять подходит он им или нет
                all_actors = await base.get_all_actors()
                for actor in all_actors:
                    if await check_paid(actor['user_id']):
                        role_index = 0  # Индекс роли, для списка из casting_data
                        role_list = []  # Формируем список из подходящих ролей
                        for role in casting_config:
                            role_index += 1
                            # Сначала проверяем пол актера
                            if actor['sex'] == role['actor_sex']:
                                # Проверяем, подходит ли проект актеру
                                if role['project_type'] in actor['projects_interest'].split('+') or role['project_type'] == 'Unspecified':
                                    # Проверяем, подходит гонорар
                                    if (actor['fee'] <= role['fee']) or role['fee'] == 0 or 'free' in actor['projects_interest'].split('+'):
                                        # Проверяем возраст актера
                                        # Игровой диапазон актера
                                        a = [int(i) for i in actor['playing_age'].split('-')]
                                        a.sort()
                                        # Возрастной диапазон для роли
                                        try:
                                            b = [int(i) for i in role['age_restrictions'].split('-')]
                                            b.sort()
                                            if a[0] >= b[0] >= a[1] or a[0] <= b[1] <= a[1]:  # noqa
                                                role_list.append(casting_data['role_description'][role_index - 1])
                                        except ValueError:
                                            if '+' in role['age_restrictions']:  # Если возрастные требования в формате n+
                                                b = role['age_restrictions'].split('+')
                                                if int(b[0]) <= a[1]:
                                                    role_list.append(casting_data['role_description'][role_index - 1])
                                        except IndexError:
                                            b = [int(i) for i in role['age_restrictions'].split('-')]
                                            if int(b[0]) <= a[1]:
                                                role_list.append(casting_data['role_description'][role_index - 1])

                        if len(role_list) > 0:
                            msg_text = (f'<b>Название проекта:</b> {casting_data["project_name"]}\n'
                                        # f'<b>Место проведения кастинга:</b> {casting_data["search_city"]}\n'
                                        f'<b>Тип проекта:</b> {casting_data["project_type"]}\n'
                                        f'<b>Дата съемок:</b> {casting_data["filming_dates"]}\n\n')
                                        # f'<b>Место съемок:</b> {casting_data["filming_location"]}\n\n')
                            for role_info in role_list:
                                additional_requirements = role_info["additional_requirements"] if role_info.get(
                                    'additional_requirements') else 'Не указан'
                                fee = role_info["fee"] if role_info.get('fee') else 'Не указан'
                                msg_text += (f'<b>Пол актера:</b> {role_info["actor_sex"]}\n'
                                             f'<b>Возраст актера:</b> {role_info["age_restrictions"]}\n'
                                             f'<b>Название роли:</b> {role_info["role_name"]}\n'
                                             f'<b>Описание роли:</b> {role_info["role_description"]}\n'
                                             f'<b>Дополнительные требования:</b> {additional_requirements}\n'
                                             f'<b>Гонорар:</b> {fee}\n\n')
                            if casting_contacts["contacts"] != 'комментарии':
                                msg_text += (f'<b>Контакты:</b> {casting_contacts["contacts"]}\n'
                                             f'<b>Заголовок письма:</b> {casting_contacts["title"]}\n'
                                             f'<b>Правила оформления заявки:</b> {casting_contacts["rules"]}\n')
                            else:
                                msg_text += (f'<b>Заявки оставлять в комментариях:</b> '
                                             f'https://t.me/{message.chat.username}/{message.id}\n'
                                             f'<b>Правила оформления заявки:</b> {casting_contacts["rules"]}\n')

                            if casting_rights:
                                msg_text += f'<b>Права:</b> {casting_rights["rights"]}'

                            await bot.send_message(
                                chat_id=actor['user_id'],
                                text=msg_text,
                                reply_markup=await button_for_casting(
                                    message_id=m.message_id,
                                    casting_hash=casting_hash
                                )
                            )
            except PostgresSyntaxError as e:
                with open('psql_er.log', 'a', encoding='utf-8') as file:
                    file.write(f'\n==================\n{casting_text}\n\n{json.dumps(casting_data)}\n\n{json.dumps(casting_config)}\n{str(e)}\n==================\n\n')

        except TypeError as e:  # Значит не кастинг
            pass
        except UniqueViolationError:  # Проскачил уже имеющийся в базе
            pass


async def parser_stop():
    """Останавливаем работу парсера"""
    # Если вернется True значит парсер включен
    if await techno_dict['parser'].check_status():
        await techno_dict['parser'].switch_status()


async def parser_status():
    """Проверяем статус парсера"""
    return await techno_dict['parser'].check_status()
