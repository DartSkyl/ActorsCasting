import json

from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER

from loader import base, techno_dict, dp, bot
from utils.users_router import users_router
from utils.user_bot_parser import check_paid
from states import ActorsState
from config import SUPPORT, CONTROL_GROUP, PUBLIC_CHANNEL
from keyboards.reply import main_menu_actor
from keyboards.inline_actors import (setup_keyboard, education_choice, paid_url,
                                     experience_choice, role_interested, button_for_casting)


@users_router.callback_query(F.data.startswith('origin_'))
async def get_origin_request(callback: CallbackQuery, state: FSMContext):
    """Ловим запрос от пользователя на получение оригинала сообщения"""
    await callback.answer()
    # После следующей операции получим список из 3 элементов:
    # ID в канале со всеми кастингами, username канала источника, ID сообщения в канале источнике
    msg_info = callback.data.replace('origin_', '').split('-')
    try:
        await bot.forward_message(
            chat_id=callback.from_user.id,
            from_chat_id=PUBLIC_CHANNEL,
            message_id=int(msg_info[0]))

        # Если есть текст для проб, в виде файла, идущем следующем сообщением в чате-источнике, то пробросим и его
        await techno_dict['parser'].check_text_for_prob(
            origin_chat=msg_info[1],
            next_origin_message=(int(msg_info[2]) + 1),
            user_id=callback.from_user.id
        )
    except ValueError:  # Если не одно фото, а ДВА
        msg_list = [int(i) for i in msg_info[0].split('&')]
        await bot.forward_messages(
            chat_id=callback.from_user.id,
            from_chat_id=PUBLIC_CHANNEL,
            message_ids=msg_list
        )
        # Если есть текст для проб, в виде файла, идущем следующем сообщением в чате-источнике, то пробросим и его
        await techno_dict['parser'].check_text_for_prob(
            origin_chat=msg_info[1],
            next_origin_message=(msg_list[-1] + 1),
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
        msg_text_2 = """
<b>Памятка актёру</b>

👁️‍🗨️ Внимательно читайте правила оформления заявки и отправляйте только ту информацию, которую просит кастинг-директор. Соблюдайте этику общения, и никогда не отправляйте заявки ночью.

👁️‍🗨️ Добавляйте кастинги, на которые вы откликнулись, в «Избранное». Чтобы к ним можно было вернуться в случае утверждения на роль и уточнить условия (гонорар, даты и т.д.). Так же это позволит вам отследить статистику и понять на сколько проектов вы откликнулись в этом месяце.

👁️‍🗨️ Не забывайте обновлять свои актерские материалы (фото и видео-визитку) раз в пол года. То, как вы выглядите в ваших материалах должно совпадать с тем, как вы выглядите, когда записываете пробу и отправляете её кастинг-директору.

👁️‍🗨️ Если вам приходит мало кастингов, – внесите изменения в настройки профиля /settings. Выберите больше типов проектов, которые вам интересны, или попробуйте сделать ниже минимальный гонорар.

👁️‍🗨️ Если вы отправляете много заявок, но вам приходит мало предложений, – попробуйте сделать новое портфолио или даже поменять немного стиль. Часто изменение маленькой детали в образе может сильно повлиять на результат.

👁️‍🗨️ Мы собираем для вас кастинги в том числе и с открытых источников, будте бдительны, остерегайтесь мошенников.
⚠️ Никогда не отправляйте обнажённые фото и не переводите деньги ни под каким предлогом. Таких требований в практике киноиндустрии быть не может.
В случае, если после подачи заявки, вам пришло неприличное предложение, сразу напишите нам в тех.поддержку /support

👁️‍🗨️ Мы развиваемся и внедряем новые опции, чтобы вам было удобнее работать с ботом. Если у вас есть предложение как улучшить наш проект, пишите нам, постараемся внедрить.

Желаем вам больших классных проектов и интересных ролей!

Спасибо, что вы с нами❤️
С уважением, команда Oh My Cast.
        """
        try:
            await bot.send_message(chat_id=chat_member.new_chat_member.user.id, text=msg_text)
            await bot.send_message(chat_id=chat_member.new_chat_member.user.id, text=msg_text_2, reply_markup=main_menu_actor)
        except TelegramForbiddenError:
            with open('msg_error.txt', 'a') as file:
                print(chat_member, file=file)


@users_router.message(Command('subscription'))
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
    # символом "&". По этому, для удаления и добавления в избранное будем проводить операции со всей строкой ¯\_(ツ)_/¯
    user_favorites = (await base.get_actor_favorites(callback.from_user.id))[0]['favorites']
    # При первом добавлении из БД вернется None
    new_favorite = callback.data.replace('favorites_', '')
    try:
        user_favorites = user_favorites.split('&')
        if new_favorite not in user_favorites:
            user_favorites.append(new_favorite)
            user_favorites = '&'.join(user_favorites)
            await base.set_actor_favorites(callback.from_user.id, user_favorites)
            await callback.message.answer('Кастинг добавлен в "Избранное"')
        else:
            await callback.message.answer('Данный кастинг уже есть в избранном!')
    except AttributeError:  # Выскочит при пустом "Избранное"
        await base.set_actor_favorites(callback.from_user.id, new_favorite)
        await callback.message.answer('Кастинг добавлен в "Избранное"')


@users_router.message(Command('favorites'))
@users_router.message(F.text == 'Избранное')
async def get_favorites_list(msg: Message):
    """Открываем список избранного"""
    user_favorites = (await base.get_actor_favorites(msg.from_user.id))[0]['favorites']
    user_favorites = user_favorites.split('&')
    if len(user_favorites) > 0 and user_favorites != ['']:
        for c_hash in user_favorites:
            try:
                casting = (await base.get_casting(c_hash))[0]
                casting_data = json.loads(casting['casting_data'])
                msg_text = (f'<i>Сохраненный кастинг</i>\n\n'
                            f'<b>Название проекта:</b> {casting_data["project_name"]}\n'
                            f'<b>Тип проекта:</b> {casting_data["project_type"]}\n'
                            f'<b>Дата съемок:</b> {casting_data["filming_dates"]}\n')
                await msg.answer(msg_text, reply_markup=await button_for_casting(casting['origin_for_user'],
                                                                                 casting_hash_rm=c_hash))
            except Exception as e:  # Если такого кастинга в базе больше нет, то удалим из избранного
                if msg.from_user.id == 1004280953:
                    await msg.answer(str(e))
                # user_favorites.remove(c_hash)
                # user_favorites = '&'.join(user_favorites)
                await base.set_actor_favorites(msg.from_user.id, user_favorites)
                await msg.answer('Кастинг был удален администрацией!')

    else:
        await msg.answer('В "Избранном" пусто!')


@users_router.callback_query(F.data.startswith('rm_favorites_'))
async def remove_favorite_casting(callback: CallbackQuery):
    """Удаляем кастинг из избранного"""
    await callback.answer()
    # Все кастинги в избранном хранятся в виде одной длинной строки с хэшами кастингов разделенных
    # символом "_". По этому, для удаления и добавления в избранное будем проводить операции со всей строкой ¯\_(ツ)_/¯
    user_favorites = (await base.get_actor_favorites(callback.from_user.id))[0]['favorites']
    rm_favorites = callback.data.replace('rm_favorites_', '')
    try:
        user_favorites = user_favorites.split('&')
        if rm_favorites in user_favorites:
            user_favorites.remove(rm_favorites)
            user_favorites = '&'.join(user_favorites)
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


@users_router.message(Command('settings'))
@users_router.message(F.text == 'Настройки профиля')
async def open_acc_setup_menu(msg: Message, state: FSMContext):
    """Открываем меню настройки профиля"""
    if msg.from_user.id in await base.get_users_id():
        actor_data = (await base.get_actor_info(msg.from_user.id))[0]
        msg_text = (f'Текущие настройки профиля:\n\n'
                    f'<b>ФИО:</b> {actor_data["actor_name"]}\n'
                    f'<b>Пол:</b> {dict_for_msg_build[actor_data["sex"]]}\n'
                    f'<b>Возраст по паспорту:</b> {actor_data["passport_age"]}\n'
                    f'<b>Игровой возраст:</b> {actor_data["playing_age"]}\n'
                    f'<b>Образование:</b> {dict_for_msg_build[actor_data["education"]]}\n'
                    f'<b>Опыт:</b> {dict_for_msg_build[actor_data["have_experience"]]}\n'
                    f'<b>Портфолио:</b> {actor_data["portfolio"]}\n'
                    f'<b>Соц. сети:</b> {actor_data["social"]}\n'
                    f'<b>То, что интересует:</b> {", ".join([dict_for_msg_build[a] for a in actor_data["projects_interest"].split("+")])}\n'
                    f'<b>Минимальный гонорар:</b> {actor_data["fee"]}')
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
                f'<b>Опыт:</b> {dict_for_msg_build[actor_data["have_experience"]]}\n'
                f'<b>Портфолио:</b> {actor_data["portfolio"]}\n'
                f'<b>Соц. сети:</b> {actor_data["social"]}\n'
                f'<b>То, что интересует:</b> {", ".join([dict_for_msg_build[a] for a in actor_data["projects_interest"].split("+")])}')
    await callback.message.answer(msg_text, reply_markup=setup_keyboard)


@users_router.message(Command('get_channels'))
async def get_channels(msg: Message):
    from pyrogram.enums.chat_type import ChatType  # noqa
    from aiogram.types import FSInputFile
    import os
    ch = techno_dict['parser']._client.get_dialogs()  # noqa
    with open('channels.txt', 'a', encoding='utf-8') as file:
        last_id = 0
        async for c in ch:
            if last_id != c.chat.id:
                if c.chat.type == ChatType.CHANNEL or c.chat.type == ChatType.SUPERGROUP or c.chat.type == ChatType.GROUP:
                    if c.chat.username:
                        file.write(f'https://t.me/{c.chat.username}\n')
                    else:
                        file.write(str(c.chat.title) + '\n')
                last_id = c.chat.id  # так как он сам не остановится
            else:
                break
    await msg.answer_document(document=FSInputFile('channels.txt'))
    os.remove('channels.txt')


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
        if len(projects_interest) > 0:
            await base.setup_param('projects_interest', '+'.join(projects_interest), callback.from_user.id)
            await state.clear()
            await review_all_data_after_setup(callback, state)
        else:
            await callback.message.answer('Нужно выбрать хотя бы один интерес!')
