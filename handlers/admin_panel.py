import os
from datetime import date, timedelta
import json

from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import base
from utils.admin_router import admin_router
from keyboards.reply import admin_main, cancel_button
from keyboards.inline_admin import casting_bd_period, button_for_casting_admin, user_action_menu
from states import AdminStates


@admin_router.message(Command('admin'))
async def open_admin_panel(msg: Message, state: FSMContext):
    """Открываем админ-панель"""
    await state.clear()
    await msg.answer(f'Добрый день, {msg.from_user.first_name}!\nВыберете действие:', reply_markup=admin_main)


@admin_router.message(Command('drop'))
async def get_drop_messages(msg: Message):
    from aiogram.types import FSInputFile
    await msg.answer_document(document=FSInputFile('drop.log'))
    os.remove('drop.log')

# ====================
# Работа с пользователями
# ====================


@admin_router.message(F.text == 'Подписчики')
async def user_menu_open(msg: Message):
    """Открываем меню взаимодействия с пользователями"""
    await msg.answer('Выберете, что хотите сделать:', reply_markup=user_action_menu)


@admin_router.callback_query(F.data.startswith('sub_'))
async def sub_actions(callback: CallbackQuery, state: FSMContext):
    """Запускаем действие с подпиской"""
    if callback.data == 'sub_add':
        await state.set_state(AdminStates.sub_add)
        await callback.message.answer('Перешлите сообщение пользователя, которому хотите добавить подписку')
    else:
        await state.set_state(AdminStates.sub_del)
        await callback.message.answer('Перешлите сообщение пользователя, которому хотите удалить подписку')


@admin_router.message(AdminStates.sub_add)
async def add_sub_user(msg: Message, state: FSMContext):
    """Добавляем подписку пользователю через пересланное сообщение"""
    if msg.forward_from:
        await base.add_sub(msg.forward_from.id)
        await msg.answer('Подписка добавлена')
        await state.clear()


@admin_router.message(AdminStates.sub_del)
async def add_sub_user(msg: Message, state: FSMContext):
    """Добавляем подписку пользователю через пересланное сообщение"""
    if msg.forward_from:
        await base.del_sub(msg.forward_from.id)
        await msg.answer('Подписка удалена')
        await state.clear()


@admin_router.callback_query(F.data == 'show_user')
async def show_user_settings(callback: CallbackQuery, state: FSMContext):
    """Запускаем демонстрацию настроек пользователя"""
    await callback.message.answer('Перешлите сообщение пользователя, чьи настройки хотите посмотреть:')
    await state.set_state(AdminStates.show_user)


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


@admin_router.message(AdminStates.show_user)
async def show_user(msg: Message, state: FSMContext):
    """Показываем настройки пользователя"""
    if msg.forward_from:
        if msg.forward_from.id in await base.get_users_id():
            actor_data = (await base.get_actor_info(msg.forward_from.id))[0]
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
                        f'<b>То, что интересует:</b> {", ".join([dict_for_msg_build[a] for a in actor_data["projects_interest"].split("+")])}\n'
                        f'<b>Минимальный гонорар:</b> {actor_data["fee"]}')
            await msg.answer(msg_text)
        await state.clear()


# ====================
# Работа с базой кастингов
# ====================


@admin_router.message(F.text == 'База данных кастингов')
async def open_casting_bd_menu(msg: Message, state: FSMContext):
    """Открываем меню выбора отчетного периода БД с кастингами"""
    await msg.answer('Выберете отчетный период:', reply_markup=casting_bd_period)
    await state.set_state(AdminStates.set_period)


async def forming_casting_msg(casting_data, time_added, more_details=False):
    """Формирует сообщения с информацией о кастинге"""
    msg_text = (f'<i>Кастинг добавлен:</i> {time_added}\n\n'
                f'<b>Название проекта:</b> {casting_data["project_name"]}\n'
                f'<b>Тип проекта:</b> {casting_data["project_type"]}\n'
                f'<b>Дата съемок:</b> {casting_data["filming_dates"]}\n')
    if more_details:
        roles_info = 'Требуемые роли:\n\n'
        for role in casting_data['role_description']:
            additional_requirements = role["additional_requirements"] if role.get('additional_requirements') else 'Не указан'
            fee = role["fee"] if role.get('fee') else 'Не указан'
            roles_info += (f'<b>Пол актера:</b> {role["actor_sex"]}\n'
                           f'<b>Возраст актера:</b> {role["age_restrictions"]}\n'
                           f'<b>Название роли:</b> {role["role_name"]}\n'
                           f'<b>Описание роли:</b> {role["role_description"]}\n'
                           f'<b>Дополнительные требования:</b> {additional_requirements}\n'
                           f'<b>Гонорар:</b> {fee}\n\n')
        msg_text += roles_info
    return msg_text


@admin_router.callback_query(F.data.startswith('period_'))
async def set_statistic_period(callback: CallbackQuery, state: FSMContext):
    """Хэндлер достает из БД кастинги за соответствующий период,
    формирует удобочитаемую строку и сообщением отравляет пользователю"""
    await callback.answer()
    date_interval = {
        'period_week': [str(date.today() - timedelta(days=7)), str(date.today() - timedelta(days=1))],
        'period_month': [str(date.today() - timedelta(days=30)), str(date.today() - timedelta(days=1))],
    }
    castings = None  # Для дальнейшего использования
    if callback.data == 'period_today':
        castings = await base.get_today_statistic(date_today=str(date.today()))
        for cast in castings:
            msg_text = await forming_casting_msg(json.loads(cast['casting_data']), cast['time_added'])
            await callback.message.answer(text=msg_text, reply_markup=await button_for_casting_admin(
                origin=cast['casting_origin'],
                casting_hash=cast['casting_hash']
            ))

    elif callback.data in ['period_week', 'period_month']:
        # Получаем список со статистическими данными за выбранный период
        castings = await base.get_statistic_data(
            first_date=date_interval[callback.data][0],
            second_date=date_interval[callback.data][1]
        )
        for cast in castings:
            msg_text = await forming_casting_msg(json.loads(cast['casting_data']), cast['time_added'])
            await callback.message.answer(text=msg_text, reply_markup=await button_for_casting_admin(
                origin=cast['casting_origin'],
                casting_hash=cast['casting_hash']
            ))

    elif callback.data == 'period_all_days':
        castings = await base.get_statistic_for_all_period()
        for cast in castings:
            msg_text = await forming_casting_msg(json.loads(cast['casting_data']), cast['time_added'])
            await callback.message.answer(text=msg_text, reply_markup=await button_for_casting_admin(
                origin=cast['casting_origin'],
                casting_hash=cast['casting_hash']
            ))

    elif callback.data == 'period_user_date':
        await state.set_state(AdminStates.set_user_date)
        msg_text = ('Введите желаемый диапазон дат в формате\n"2024-01-01 2024-01-09"\n'
                    'без кавычек и первая дата меньше второй‼️')
        await callback.message.answer(text=msg_text, reply_markup=cancel_button)


@admin_router.message(AdminStates.set_user_date, F.text.regexp(r'\d{4}-\d{2}-\d{2}\s\d{4}-\d{2}-\d{2}'))
async def get_user_date_interval(msg: Message, state: FSMContext):
    user_date = msg.text.split()
    castings = await base.get_statistic_data(
        first_date=user_date[0],
        second_date=user_date[1]
    )
    for cast in castings:
        msg_text = await forming_casting_msg(json.loads(cast['casting_data']), cast['time_added'])
        await msg.answer(text=msg_text, reply_markup=await button_for_casting_admin(
            origin=cast['casting_origin'],
            casting_hash=cast['casting_hash']
        ))


@admin_router.callback_query(F.data.startswith('view_'))
async def show_more_details(callback: CallbackQuery):
    """Разворачиваем сообщение с кастингом подробнее"""
    await callback.answer()
    casting = (await base.get_casting(callback.data.replace('view_', '')))[0]
    msg_text = await forming_casting_msg(json.loads(casting['casting_data']), casting['time_added'], True)
    await callback.message.edit_text(msg_text, reply_markup=await button_for_casting_admin(
        origin=casting['casting_origin'],
        casting_hash=casting['casting_hash'],
        viewing=True
    ))


@admin_router.callback_query(F.data.startswith('rm_admin_'))
async def remove_casting_from_db(callback: CallbackQuery):
    """Удаляем кастинг из БД"""
    await callback.answer()
    await base.remove_casting(callback.data.replace('rm_admin_', ''))
    await callback.message.delete()
    await callback.message.answer('Кастинг удален')
