import asyncio
import json

from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMember
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid

from loader import base, techno_dict, dp, bot
from utils.users_router import users_router
from utils.user_bot_parser import check_paid
from states import ActorsState
from config import SUPPORT, CONTROL_GROUP
from keyboards.reply import main_menu_actor
from keyboards.inline_actors import (setup_keyboard, education_choice, paid_url,
                                     experience_choice, role_interested, button_for_casting)


@dp.message(F.forward_origin)
async def for_forward_message(msg: Message):
    """Дле перебрасывания сообщений, сам ты извращенец!"""
    if msg.from_user.id == techno_dict['parser_id']:
        user_for_drop = None
        for user in techno_dict['forwarding']:
            # У каждого элемента списка словарь с одним ключем и одним значением и что бы их извлечь делаем так:
            for user_id, user_request in user.items():
                user_request = [int(i) for i in user_request.split('_')]
                # Теперь проверяем, что бы переброшенное сообщение соответствовало запросу пользователя
                try:
                    if msg.forward_origin.message_id == user_request[1] and msg.forward_origin.chat.id == user_request[0]:
                        await msg.forward(user_id)
                        user_for_drop = user
                        break
                except AttributeError:  # Если пересылка из чата, то тут мы никак не проверим
                    await msg.forward(user_id)
                    user_for_drop = user
                    break

            techno_dict['forwarding'].remove(user_for_drop)
    else:
        await msg.answer('Нельзя пересылать боту сообщения!')


@users_router.callback_query(F.data.startswith('origin_'))
async def get_origin_request(callback: CallbackQuery, state: FSMContext):
    """Ловим запрос от пользователя на получение оригинала сообщения"""
    await callback.answer()
    # Извлекаем ID чата и сообщения из callback и формируем из них список
    origin_message = [int(i) for i in callback.data.replace('origin_', '').split('_')]

    # Отправляем сообщения в личку бота
    await techno_dict['parser'].forward_origin_message(
        origin_chat=origin_message[0],
        origin_message=origin_message[1],
        user_id=callback.from_user.id
    )
    # Так как для этих двух функций используется словарь с одним ключом, но разным значением, то сделаем небольшую паузу
    await asyncio.sleep(0.5)

    # Если есть текст для проб, в виде файла, идущем следующем сообщением в чате-источнике, то пробросим и его
    await techno_dict['parser'].check_text_for_prob(
        origin_chat=origin_message[0],
        next_origin_message=(origin_message[1] + 1),
        user_id=callback.from_user.id
    )


# ====================
# Работа с подписками
# ====================


@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> MEMBER))
async def catch_new_member(chat_member: ChatMember):
    """Если актер оплатил подписку, то он появиться в контрольной группе. Отловим это событие"""
    if chat_member.chat.id == CONTROL_GROUP:
        msg_text = ('Подписка оформлена, спасибо за доверие! Пошел подбирать для тебя кастинги. Как только найду '
                    'подходящий, моментально пришлю его тебе сюда. Подавай заявки и получай роли!')
        await bot.send_message(chat_id=chat_member.from_user.id, text=msg_text, reply_markup=main_menu_actor)


@users_router.message(F.text == 'Подписка')
async def open_subscription_page(msg: Message):
    """Отдаем ссылку на страницу с оплатой"""
    is_paid = await check_paid(msg.from_user.id)
    if is_paid:
        msg_text = 'Ваша подписка активна\n'
    else:
        msg_text = 'У вас нет подписки\n'

    await msg.answer((msg_text + 'Страница управления подпиской:'), reply_markup=await paid_url(msg.from_user.id, is_paid))


@users_router.message(Command('support'))
async def get_support_contact(msg: Message):
    """Отправляем контакт поддержки"""
    await msg.answer(f'Со всеми вопросами обращаться сюда {SUPPORT}')


# ====================
# Работа с "Избранным"
# ====================

@users_router.callback_query(F.data.startswith('favorites_'))
async def add_to_favorites(callback: CallbackQuery):
    """Добавляем кастинг в избранное"""
    await callback.answer()
    # Все кастинги в избранном хранятся в виде одной длинной строки с хэшами кастингов разделенных
    # символом "_". По этому, для удаления и добавления в избранное будем проводить операции со всей строкой ¯\_(ツ)_/¯
    user_favorites = (await base.get_actor_favorites(callback.from_user.id))[0]['favorites']
    # При первом добавлении из БД вернется None
    new_favorite = callback.data.replace('favorites_', '')
    try:
        user_favorites = user_favorites.split('_')
        if new_favorite not in user_favorites:
            user_favorites.append(new_favorite)
            user_favorites = '_'.join(user_favorites)
            await base.set_actor_favorites(callback.from_user.id, user_favorites)
            await callback.message.answer('Кастинг добавлен в "Избранное"')
        else:
            await callback.message.answer('Данный кастинг уже есть в избранном!')
    except AttributeError:  # Выскочит при пустом "Избранное"
        await base.set_actor_favorites(callback.from_user.id, new_favorite)
        await callback.message.answer('Кастинг добавлен в "Избранное"')


@users_router.message(F.text == 'Избранное')
async def get_favorites_list(msg: Message):
    """Открываем список избранного"""
    user_favorites = (await base.get_actor_favorites(msg.from_user.id))[0]['favorites']
    try:
        user_favorites = user_favorites.split('_')
        for c_hash in user_favorites:
            casting = (await base.get_casting(c_hash))[0]
            casting_data = json.loads(casting['casting_data'])
            casting_origin = [int(i) for i in casting['casting_origin'].split('_')]
            msg_text = (f'<i>Сохраненный кастинг</i>\n\n<b>Город кастинга:</b> {casting_data["search_city"]}\n'
                        f'<b>Название проекта:</b> {casting_data["project_name"]}\n'
                        f'<b>Тип проекта:</b> {casting_data["project_type"]}\n'
                        f'<b>Дата съемок:</b> {casting_data["filming_dates"]}\n'
                        f'<b>Место съемок:</b> {casting_data["filming_location"]}\n')
            await msg.answer(msg_text, reply_markup=await button_for_casting(casting_origin[0], casting_origin[1],
                                                                             casting_hash_rm=c_hash))

    except AttributeError:  # Выскочит при пустом "Избранное"
        await msg.answer('В "Избранном" пусто')
    except IndexError:
        await msg.answer('В "Избранном" пусто')
    except Exception as e:
        await msg.answer('Кастинг был удален администрацией!')
        print(e)


@users_router.callback_query(F.data.startswith('rm_favorites_'))
async def remove_favorite_casting(callback: CallbackQuery):
    """Удаляем кастинг из избранного"""
    await callback.answer()
    # Все кастинги в избранном хранятся в виде одной длинной строки с хэшами кастингов разделенных
    # символом "_". По этому, для удаления и добавления в избранное будем проводить операции со всей строкой ¯\_(ツ)_/¯
    user_favorites = (await base.get_actor_favorites(callback.from_user.id))[0]['favorites']
    rm_favorites = callback.data.replace('rm_favorites_', '')
    try:
        user_favorites = user_favorites.split('_')
        if rm_favorites in user_favorites:
            user_favorites.remove(rm_favorites)
            user_favorites = '_'.join(user_favorites)
            await base.set_actor_favorites(callback.from_user.id, user_favorites)
            await callback.message.answer('Кастинг удален из "Избранное"')
        else:
            await callback.message.answer('Кастинг уже удален!')
    except Exception as e:  # Выскочит при пустом "Избранное"
        print(e)
        await callback.message.answer('Кастинг уже удален!')


# ====================
# Настройки профиля
# ====================

# Словарь со значениями для формирования сообщений
dict_for_msg_build = {
        # Роли
        'films': 'Кастинги в кино',
        'series': 'Кастинг в сериал',
        'ads': 'Кастинги в рекламу',
        'theater': 'Театральные проекты',
        'main_role': 'Главные и второстепенные роли',
        'episode': 'Эпизоды',
        'mass': 'Групповка/массовка',
        'free': 'Некоммерческие проекты / фестивальные короткометражные фильмы молодых режиссёров',
        # Образование
        'vuz': 'Получил диплом. гос. образца',
        'curs': 'Прошёл курсы актерского мастерства',
        'none': 'Актерского образования нет',
        # Опыт
        'null': 'Опыта нет, я - новичок',
        'ads_': 'Снималась(ся) только в рекламе / массовках/групповках',
        'free_': 'Снималась(ся) в эпизодах / некоммерческих проектах',
        'main': 'Есть второстепенные / главные роли в полнометражных фильмах/сериалах',
        # Пол
        'male': 'Мужской',
        'female': 'Женский'
    }


@users_router.message(F.text == 'Настройки профиля')
async def open_acc_setup_menu(msg: Message, state: FSMContext):
    """Открываем меню настройки профиля"""
    actor_data = (await base.get_actor_info(msg.from_user.id))[0]
    msg_text = (f'Текущие настройки профиля:\n\n'
                f'<b>ФИО:</b> {actor_data["actor_name"]}\n'
                f'<b>Пол:</b> {dict_for_msg_build[actor_data["sex"]]}\n'
                f'<b>Возраст по паспорту:</b> {actor_data["passport_age"]}\n'
                f'<b>Игровой возраст:</b> {actor_data["playing_age"]}\n'
                f'<b>Образование:</b> {dict_for_msg_build[actor_data["education"]]}\n'
                f'<b>Город проживания:</b> {actor_data["geo_location"]}\n'
                f'<b>Контактные данные:</b> {actor_data["contacts"]}\n'
                f'<b>Опыт:</b> {dict_for_msg_build[actor_data["have_experience"]]}\n'
                f'<b>Портфолио:</b> {actor_data["portfolio"]}\n'
                f'<b>Соц. сети:</b> {actor_data["social"]}\n'
                f'<b>То, что интересует:</b> {", ".join([dict_for_msg_build[a] for a in actor_data["projects_interest"].split("+")])}')
    await state.set_data({'projects_interest': actor_data["projects_interest"].split("+")})
    await msg.answer(msg_text, reply_markup=setup_keyboard)


@users_router.callback_query(F.data.startswith('setup_'))
async def start_acc_setup(callback: CallbackQuery, state: FSMContext):
    """Начинаем изменения параметров аккаунта"""
    setup_dict = {
        'setup_passport_age': (ActorsState.passport_age_setup, 'Возраст по паспорту', None),
        'setup_playing_age': (
        ActorsState.playing_age_setup, 'Игровой возраст (диапазон, который вы можете играть через дефис)', None),
        'setup_education': (ActorsState.education_setup, 'Выберете образование', education_choice),
        'setup_geo_location': (ActorsState.geo_location_setup, 'Введите город проживания', None),
        'setup_contacts': (ActorsState.contacts_setup, 'Введите контактные данные (телефон, email через запятую)', None),
        'setup_agent_contact': (
        ActorsState.agent_contact_setup, 'Контактные данные вашего агента (телефон, email через запятую)', None),
        'setup_have_experience': (ActorsState.have_experience_setup, 'Какой у вас опыт?', experience_choice),
        'setup_portfolio': (ActorsState.portfolio_setup, 'Введите ссылку на ваше портфолио', None),
        'setup_social': (ActorsState.social_setup, 'Введите ссылку на страницу в соц. сети', None),
        'setup_fee': (ActorsState.fee_setup, 'Укажите минимальный гонорар в рублях:', None),
        'setup_roles_type_interest': (ActorsState.roles_type_interest_setup,
                                      'Выбери из списка то, что тебя интересует (можно выбрать несколько вариантов):',
                                      role_interested),
    }
    await callback.answer()
    await state.set_state(setup_dict[callback.data][0])
    await callback.message.answer(text=setup_dict[callback.data][1], reply_markup=setup_dict[callback.data][2])


async def review_all_data_after_setup(callback: CallbackQuery, state: FSMContext):
    """Выводим все введенные данные и даем возможность исправить"""
    await callback.answer()
    actor_data = (await base.get_actor_info(callback.from_user.id))[0]
    msg_text = (f'Текущие настройки профиля:\n\n'
                f'<b>ФИО:</b> {actor_data["actor_name"]}\n'
                f'<b>Пол:</b> {dict_for_msg_build[actor_data["sex"]]}\n'
                f'<b>Возраст по паспорту:</b> {actor_data["passport_age"]}\n'
                f'<b>Игровой возраст:</b> {actor_data["playing_age"]}\n'
                f'<b>Образование:</b> {dict_for_msg_build[actor_data["education"]]}\n'
                f'<b>Город проживания:</b> {actor_data["geo_location"]}\n'
                f'<b>Контактные данные:</b> {actor_data["contacts"]}\n'
                f'<b>Опыт:</b> {dict_for_msg_build[actor_data["have_experience"]]}\n'
                f'<b>Портфолио:</b> {actor_data["portfolio"]}\n'
                f'<b>Соц. сети:</b> {actor_data["social"]}\n'
                f'<b>То, что интересует:</b> {", ".join([dict_for_msg_build[a] for a in actor_data["projects_interest"].split("+")])}')
    await callback.message.answer(msg_text, reply_markup=setup_keyboard)


@users_router.message(ActorsState.passport_age_setup)
async def setup_passport_age_func(msg: Message, state: FSMContext):
    """Сохраняем изменения Возраст по паспорту"""
    await base.setup_param('passport_age', msg.text, msg.from_user.id)
    await msg.answer('Изменения сохранены')
    await state.clear()
    await open_acc_setup_menu(msg, state)


@users_router.message(ActorsState.playing_age_setup)
async def setup_playing_age_func(msg: Message, state: FSMContext):
    """Сохраняем изменения Игровой возраст"""
    try:
        playing_age = [int(a) for a in msg.text.split('-')]
        if len(playing_age) != 2:
            raise ValueError
        await base.setup_param('playing_age', msg.text, msg.from_user.id)
        await msg.answer('Изменения сохранены')
        await state.clear()
        await open_acc_setup_menu(msg, state)
    except ValueError:
        await msg.answer('Ошибка ввода!\nВведите диапазон, который вы можете играть через дефис')


@users_router.message(ActorsState.geo_location_setup)
async def setup_geo_location_func(msg: Message, state: FSMContext):
    """Сохраняем изменения город проживания"""
    await base.setup_param('geo_location', msg.text, msg.from_user.id)
    await msg.answer('Изменения сохранены')
    await state.clear()
    await open_acc_setup_menu(msg, state)


@users_router.message(ActorsState.contacts_setup)
async def setup_contacts_func(msg: Message, state: FSMContext):
    """Сохраняем изменения контактные данные"""
    await base.setup_param('contacts', msg.text, msg.from_user.id)
    await msg.answer('Изменения сохранены')
    await state.clear()
    await open_acc_setup_menu(msg, state)


@users_router.message(ActorsState.agent_contact_setup)
async def setup_agent_contact_func(msg: Message, state: FSMContext):
    """Сохраняем изменения Контактные данные агента"""
    await base.setup_param('agent_contact', msg.text, msg.from_user.id)
    await msg.answer('Изменения сохранены')
    await state.clear()
    await open_acc_setup_menu(msg, state)


@users_router.message(ActorsState.portfolio_setup)
async def setup_portfolio_func(msg: Message, state: FSMContext):
    """Сохраняем изменения портфолио"""
    await base.setup_param('portfolio', msg.text, msg.from_user.id)
    await msg.answer('Изменения сохранены')
    await state.clear()
    await open_acc_setup_menu(msg, state)


@users_router.message(ActorsState.social_setup)
async def setup_social_func(msg: Message, state: FSMContext):
    """Сохраняем изменения соц. сети"""
    await base.setup_param('social', msg.text, msg.from_user.id)
    await msg.answer('Изменения сохранены')
    await state.clear()
    await open_acc_setup_menu(msg, state)


@users_router.message(ActorsState.fee_setup)
async def setup_social_func(msg: Message, state: FSMContext):
    """Сохраняем изменения гонорар"""
    try:
        await base.setup_param('fee', int(msg.text), msg.from_user.id)
        await msg.answer('Изменения сохранены')
        await state.clear()
        await open_acc_setup_menu(msg, state)
    except ValueError:
        await msg.answer('Нужно ввести целое число! Повторите!')


@users_router.callback_query(ActorsState.education_setup)
async def setup_education_func(callback: CallbackQuery, state: FSMContext):
    """Сохраняем изменения образование"""
    await callback.answer()
    await base.setup_param('education', callback.data.replace('educ_', ''), callback.from_user.id)
    await callback.message.answer('Изменения сохранены')
    await state.clear()
    await review_all_data_after_setup(callback, state)


@users_router.callback_query(ActorsState.have_experience_setup)
async def setup_have_experience_func(callback: CallbackQuery, state: FSMContext):
    """Сохраняем изменения опыт"""
    await callback.answer()
    await base.setup_param('have_experience', callback.data.replace('exp_', ''), callback.from_user.id)
    await callback.message.answer('Изменения сохранены')
    await state.clear()
    await review_all_data_after_setup(callback, state)


@users_router.callback_query(ActorsState.roles_type_interest_setup)
async def setup_roles_type_interest_func(callback: CallbackQuery, state: FSMContext):
    """Сохраняем изменения """
    await callback.answer()
    if callback.data != 'ready':
        msg_text = 'Выбери из списка то, что тебя интересует (можно выбрать несколько вариантов)\nУже выбрано:\n\n'

        projects_interest: list = (await state.get_data())['projects_interest']

        projects_choice = callback.data.replace('choice_', '')

        if projects_choice not in projects_interest:
            projects_interest.append(projects_choice)
        else:
            projects_interest.remove(projects_choice)

        for elem in projects_interest:
            msg_text += dict_for_msg_build[elem] + '\n'

        msg_text += '\nНажмите повторно что бы убрать выбранное\nНажмите "Готово" что бы продолжить'
        await state.update_data({'projects_interest': projects_interest})
        await callback.message.edit_text(msg_text, reply_markup=role_interested)
    else:
        projects_interest: list = (await state.get_data())['projects_interest']
        await base.setup_param('projects_interest', '+'.join(projects_interest), callback.from_user.id)
        await state.clear()
        await review_all_data_after_setup(callback, state)
