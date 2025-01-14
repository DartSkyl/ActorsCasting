import os
import json
from pydantic_core._pydantic_core import ValidationError
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums.message_media_type import MessageMediaType
from pyrogram.enums.message_entity_type import MessageEntityType
from pyrogram import filters

from aiogram.types.chat_member_left import ChatMemberLeft
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder

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

    async def check_text_for_prob(self, user_id, origin_chat, next_origin_message):
        """Этим методом проверяем есть ли текст проб в следующем сообщении в виде файла"""
        prob_text = await self._client.get_messages(chat_id=origin_chat, message_ids=next_origin_message)
        if prob_text.media == MessageMediaType.DOCUMENT:
            f = await self._client.download_media(prob_text)
            await bot.send_document(chat_id=user_id, document=FSInputFile(f))
            os.remove(f)


async def check_paid(user_id):
    """Бот подключен к платежной системе paywall. У них контроль подписки осуществляется через контрольный "закрытый"
    канал. Т.е. если подписчик в этом канале есть, значит подписка оплачена и наоборот. Так что будем проверять наличие
    пользователя в группе на предмет оплаченной подписки. Если вы ничего не поняли, у меня для вас плохие новости"""
    is_paid = await bot.get_chat_member(chat_id=CONTROL_GROUP, user_id=user_id)
    if not isinstance(is_paid, ChatMemberLeft) or user_id == 1004280953 or user_id in await base.get_all_sub():
        return True
    return False


async def parser_load():
    if os.path.isfile('CastingParser.session'):
        techno_dict['parser'] = UserBotParser()
    else:
        print('Юзер бот не подключен')


async def for_tests(casting_data, casting_config, casting_contacts, casting_rights):
    print(casting_config)
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

    await bot.send_message(chat_id=1004280953, text=msg_text)


async def get_contact_link(cast_msg: Message):
    """Иногда ссылки на форму заполнения заявок форматируют прямо в текст, по этому их нужно доставать от туда"""
    if cast_msg.text:
        if cast_msg.entities:
            for e in cast_msg.entities:
                if e.type == MessageEntityType.TEXT_LINK:
                    if not e.url.startswith('https://t.me/'):
                        cast_text = cast_msg.text.replace(cast_msg.text[e.offset:(e.offset + e.length)], f'ссылка для заявок: {e.url}')
                        return cast_text.replace("'", '"'), False
        return cast_msg.text.replace("'", '"'), False
    elif cast_msg.media == MessageMediaType.PHOTO:
        if cast_msg.caption_entities:
            for e in cast_msg.caption_entities:
                if e.type == MessageEntityType.TEXT_LINK:
                    if not e.url.startswith('https://t.me/'):
                        cast_text = cast_msg.caption.replace(cast_msg.caption[e.offset:(e.offset + e.length)], f'ссылка для заявок: {e.url}')
                        return cast_text.replace("'", '"'), True
        return cast_msg.caption.replace("'", '"'), True


async def parser_start():
    """Запускаем паресер"""
    app = await techno_dict['parser'].create_app()
    # Запускаем парсер
    await techno_dict['parser'].switch_status()

    @app.on_message()
    async def my_handler(client: Client, message: Message):
        """Сердце бота. Здесь мы отправляем сообщение ИИ, после чего отправляем результат актерам"""
        if message.chat.id != PUBLIC_CHANNEL:
            try:
                casting_text, pict = await get_contact_link(message)
                casting_data, casting_config, casting_contacts, casting_rights, casting_hash = await get_casting_data(casting_text)  # Возвращается кортеж

                # И публикуем в закрытом канале в качестве оригинала
                if not pict:
                    m = await bot.send_message(chat_id=PUBLIC_CHANNEL, text=casting_text)
                    m_id = m.message_id
                else:
                    if not message.media_group_id:  # Если в сообщении только одно фото
                        f = await app.download_media(message)
                        m = await bot.send_photo(chat_id=PUBLIC_CHANNEL, photo=FSInputFile(f), caption=casting_text)
                        m_id = m.message_id
                        os.remove(f)
                    else:  # Если фото несколько
                        # С каждой итерацией будем проверять на одно сообщение дальше,
                        # пока не закончиться общий media_group_id
                        next_msg_id = 0
                        # И соберем их все в один список
                        msg_photo_list = []
                        while True:
                            next_msg = await client.get_messages(chat_id=message.chat.id, message_ids=(message.id+next_msg_id))
                            if next_msg.media_group_id == message.media_group_id:
                                msg_photo_list.append(next_msg)
                                next_msg_id += 1
                            else:
                                break

                        # Теперь нужно сформировать годный к отправке список с фото
                        media_group = MediaGroupBuilder(caption=casting_text)
                        # И список с путями, что бы зачистить после себя
                        ph_list_path = []
                        for mess in msg_photo_list:
                            ph = await app.download_media(mess)
                            media_group.add(type='photo', media=FSInputFile(ph))
                            ph_list_path.append(ph)

                        m_list = await bot.send_media_group(chat_id=PUBLIC_CHANNEL, media=media_group.build())
                        # Формируем строку со списком ID
                        m_id = '&'.join([str(m.message_id) for m in m_list])
                        # Зачищаем после загрузки

                        for ph in ph_list_path:
                            os.remove(ph)
                # await for_tests(casting_data, casting_config, casting_contacts, casting_rights)
                try:
                    # Сохраняем в базу
                    print(f'try save {casting_hash} ... ', end='')
                    await base.add_new_casting(
                        casting_hash=casting_hash,
                        casting_data=json.dumps(casting_data),
                        casting_config=json.dumps(casting_config),
                        casting_origin=f'https://t.me/{message.chat.username}/{message.id}',
                        origin_for_user=f'{m_id}-{message.chat.username}-{message.id}'
                    )
                    print('success')
                except PostgresSyntaxError as ex:
                    with open('psql_er.log', 'a', encoding='utf-8') as file:
                        file.write(f'\n==================\n{casting_text}\n\n{json.dumps(casting_data)}\n\n{json.dumps(casting_config)}\n{str(ex)}\n==================\n\n')
                except Exception as e:
                    print(e)

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
                                    if (actor['fee'] <= role['fee']) or role['fee'] == 0 or ('free' in actor['projects_interest'].split('+') and role['project_type'] == 'free'):
                                        # Проверяем возраст актера
                                        # Игровой диапазон актера
                                        a = [int(i) for i in actor['playing_age'].split('-')]
                                        a.sort()
                                        try:
                                            # Возрастной диапазон для роли
                                            b = [int(i) for i in role['age_restrictions'].split('-')]
                                            b.sort()
                                            if a[0] <= b[0] <= a[1] or a[0] <= b[1] <= a[1]:
                                                role_list.append(casting_data['role_description'][role_index - 1])
                                        except ValueError:
                                            if '+' in role['age_restrictions']:  # Если возрастные требования в формате n+
                                                b = role['age_restrictions'].split('+')
                                                if int(b[0]) <= a[1]:
                                                    role_list.append(casting_data['role_description'][role_index - 1])
                                        except IndexError:
                                            b = [int(i) for i in role['age_restrictions'].split('-')]
                                            if a[0] <= int(b[0]) <= a[1]:
                                                role_list.append(casting_data['role_description'][role_index - 1])

                        if len(role_list) > 0:
                            msg_text = (f'<b>Название проекта:</b> {casting_data["project_name"]}\n'
                                        f'<b>Тип проекта:</b> {casting_data["project_type"]}\n'
                                        f'<b>Дата съемок:</b> {casting_data["filming_dates"]}\n\n')
                            for role_info in role_list:
                                additional_requirements = role_info["additional_requirements"] if role_info.get(
                                    'additional_requirements') else 'Не указан'
                                fee = role_info["fee"] if role_info.get('fee') else 'Не указан'
                                msg_text += (f'<b>Пол актера:</b> {role_info["actor_sex"]}\n'
                                             f'<b>Возраст актера:</b> {role_info["age_restrictions"]}\n'
                                             f'<b>Название роли:</b> {role_info["role_name"]}\n'
                                             f'<b>Описание роли:</b> {role_info["role_description"]}\n'
                                             f'<b>Дополнительные требования:</b> {additional_requirements}\n'
                                             f'<b>Гонорар:</b> {fee if fee != "0" else "-"}\n\n')
                            if casting_contacts["contacts"] != 'комментарии':
                                msg_text += (f'<b>Контакты:</b> {casting_contacts["contacts"]}\n'
                                             f'<b>Правила оформления заявки:</b> {casting_contacts["rules"]}\n')
                            else:
                                msg_text += (f'<b>Заявки оставлять в комментариях:</b> '
                                             f'https://t.me/{message.chat.username}/{message.id}\n'
                                             f'<b>Правила оформления заявки:</b> {casting_contacts["rules"]}\n')

                            if casting_rights:
                                msg_text += f'<b>Права:</b> {casting_rights["rights"]}\n'

                            msg_text += f'<b>Текст для проб:</b> {"есть" if "самопроб" in casting_text.lower() else "-"}\n'

                            await bot.send_message(
                                chat_id=actor['user_id'],
                                text=msg_text.replace('female', 'Женский').replace('male', 'Мужской'),
                                reply_markup=await button_for_casting(
                                    message_id=f'{m_id}-{message.chat.username}-{message.id}',
                                    casting_hash=casting_hash
                                )
                            )
            except TypeError as e:  # Значит не кастинг
                pass
            except UniqueViolationError as e:  # Проскачил уже имеющийся в базе
                pass
            except Exception as e:
                print(e)


async def parser_stop():
    """Останавливаем работу парсера"""
    # Если вернется True значит парсер включен
    if await techno_dict['parser'].check_status():
        await techno_dict['parser'].switch_status()


async def parser_status():
    """Проверяем статус парсера"""
    return await techno_dict['parser'].check_status()
