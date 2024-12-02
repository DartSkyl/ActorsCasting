import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import base, techno_dict, dp
from utils.users_router import users_router
from states import ActorsState
from keyboards.inline_actors import setup_keyboard, education_choice, experience_choice, role_interested


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
                if msg.forward_origin.message_id == user_request[1] and msg.forward_origin.chat.id == user_request[0]:
                    await msg.forward(user_id)
                    user_for_drop = user
                    break
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
                f'ФИО: {actor_data["actor_name"]}\n'
                f'Пол: {dict_for_msg_build[actor_data["sex"]]}\n'
                f'Возраст по паспорту: {actor_data["passport_age"]}\n'
                f'Игровой возраст: {actor_data["playing_age"]}\n'
                f'Образование: {dict_for_msg_build[actor_data["education"]]}\n'
                f'Город проживания: {actor_data["geo_location"]}\n'
                f'Контактные данные: {actor_data["contacts"]}\n'
                f'Контактные данные агента: {actor_data["agent_contact"] if actor_data["agent_contact"] != "empty" else "Отсутствует"}\n'
                f'Опыт: {dict_for_msg_build[actor_data["have_experience"]]}\n'
                f'Портфолио: {actor_data["portfolio"]}\n'
                f'Соц. сети: {actor_data["social"]}\n'
                f'То, что интересует: {", ".join([dict_for_msg_build[a] for a in actor_data["roles_type_interest"].split("+")])}'
                f', {", ".join([dict_for_msg_build[a] for a in actor_data["projects_interest"].split("+")])}')
    await state.set_data({'roles_type_interest': [], 'projects_interest': []})
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
                f'ФИО: {actor_data["actor_name"]}\n'
                f'Пол: {dict_for_msg_build[actor_data["sex"]]}\n'
                f'Возраст по паспорту: {actor_data["passport_age"]}\n'
                f'Игровой возраст: {actor_data["playing_age"]}\n'
                f'Образование: {dict_for_msg_build[actor_data["education"]]}\n'
                f'Город проживания: {actor_data["geo_location"]}\n'
                f'Контактные данные: {actor_data["contacts"]}\n'
                f'Контактные данные агента: {actor_data["agent_contact"] if actor_data["agent_contact"] != "empty" else "Отсутствует"}\n'
                f'Опыт: {dict_for_msg_build[actor_data["have_experience"]]}\n'
                f'Портфолио: {actor_data["portfolio"]}\n'
                f'Соц. сети: {actor_data["social"]}\n'
                f'То, что интересует: {", ".join([dict_for_msg_build[a] for a in actor_data["roles_type_interest"].split("+")])}'
                f', {", ".join([dict_for_msg_build[a] for a in actor_data["projects_interest"].split("+")])}')
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

        roles_type_interest: list = (await state.get_data())['roles_type_interest']
        projects_interest: list = (await state.get_data())['projects_interest']
        if callback.data.startswith('choice_r'):
            roles_type_choice = callback.data.replace('choice_r_', '')

            if roles_type_choice not in roles_type_interest:
                roles_type_interest.append(roles_type_choice)
            else:
                roles_type_interest.remove(roles_type_choice)

        else:
            projects_choice = callback.data.replace('choice_p_', '')

            if projects_choice not in projects_interest:
                projects_interest.append(projects_choice)
            else:
                projects_interest.remove(projects_choice)

        for elem in roles_type_interest:
            msg_text += dict_for_msg_build[elem] + '\n'
        for elem in projects_interest:
            msg_text += dict_for_msg_build[elem] + '\n'

        msg_text += '\nНажмите повторно что бы убрать выбранное\nНажмите "Готово" что бы продолжить'
        await state.update_data({'roles_type_interest': roles_type_interest, 'projects_interest': projects_interest})
        await callback.message.edit_text(msg_text, reply_markup=role_interested)
    else:
        roles_type_interest: list = (await state.get_data())['roles_type_interest']
        projects_interest: list = (await state.get_data())['projects_interest']
        await base.setup_param('roles_type_interest', '+'.join(roles_type_interest), callback.from_user.id)
        await base.setup_param('projects_interest', '+'.join(projects_interest), callback.from_user.id)
        await state.clear()
        await review_all_data_after_setup(callback, state)
