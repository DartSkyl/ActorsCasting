from datetime import date, timedelta
import json

from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from loader import dp, techno_dict, bot, base
from utils.admin_router import admin_router
from keyboards.reply import admin_main, cancel_button
from keyboards.inline_admin import casting_bd_period, button_for_casting_admin
from states import AdminStates


@admin_router.message(Command('admin'))
async def open_admin_panel(msg: Message):
    """Открываем админ-панель"""
    await msg.answer(f'Добрый день, {msg.from_user.first_name}!\nВыберете действие:', reply_markup=admin_main)


@admin_router.message(F.text == 'База данных кастингов')
async def open_casting_bd_menu(msg: Message, state: FSMContext):
    """Открываем меню выбора отчетного периода БД с кастингами"""
    await msg.answer('Выберете отчетный период:', reply_markup=casting_bd_period)
    await state.set_state(AdminStates.set_period)


async def forming_casting_msg(casting_data, time_added, more_details=False):
    """Формирует сообщения с информацией о кастинге"""
    msg_text = (f'Кастинг добавлен: {time_added}\n\nГород кастинга: {casting_data["search_city"]}\n'
                f'Название проекта: {casting_data["project_name"]}\n'
                f'Тип проекта: {casting_data["project_type"]}\n'
                f'Дата съемок: {casting_data["filming_dates"]}\n'
                f'Место съемок: {casting_data["filming_location"]}\n')
    if more_details:
        roles_info = 'Требуемые роли:\n\n'
        for role in casting_data['role_description']:
            roles_info += (f'Пол актера: {role["actor_sex"]}\n'
                           f'Возраст актера: {role["age_restrictions"]}\n'
                           f'Название роли: {role["role_name"]}\n'
                           f'Тип роли: {role["role_type"]}\n'
                           f'Описание роли: {role["role_description"]}\n'
                           f'Дополнительные требования: {role["additional_requirements"]}\n'
                           f'Гонорар: {role["fee"]}\n')
        msg_text += roles_info
    return msg_text


@admin_router.callback_query(F.data.startswith('period_'))
async def set_statistic_period(callback: CallbackQuery, state: FSMContext):
    """Хэндлер достает из БД кастинги за соответствующий период,
    формирует удобочитаемую строку и сообщением отравляет пользователю"""
    await callback.answer()
    date_interval = {
        'week': [str(date.today() - timedelta(days=7)), str(date.today() - timedelta(days=1))],
        'month': [str(date.today() - timedelta(days=30)), str(date.today() - timedelta(days=1))],
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

