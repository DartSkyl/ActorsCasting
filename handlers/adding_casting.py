from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.fsm.context import FSMContext

from loader import bot
from utils.admin_router import admin_router
from utils.users_router import users_router
from keyboards.reply import admin_main
from keyboards.inline_direct import *
from states import AddNewCasting
from config import MAIN_GROUP, ADMINS


@admin_router.message(F.text == 'Добавить кастинг')
async def add_new_casting_from_admin_and_director(msg: Message, state: FSMContext):
    """Начинаем добавления нового кастинга от админа или кастинг директора"""
    await msg.answer('Кастинг в какой проект вы хотите опубликовать?\nВыберите категорию:',
                     reply_markup=project_type_choice)
    await state.set_state(AddNewCasting.project_type)


@users_router.callback_query(F.data == 'director')
async def add_new_casting_from_director(callback: CallbackQuery, state: FSMContext):
    """Начинаем добавления нового кастинга от админа или кастинг директора"""
    await callback.answer()
    await callback.message.answer('Кастинг в какой проект вы хотите опубликовать?\nВыберите категорию:',
                                  reply_markup=project_type_choice)
    await state.set_state(AddNewCasting.project_type)


@users_router.callback_query(AddNewCasting.project_type)
async def project_type_saver(callback: CallbackQuery, state: FSMContext):
    """Ловим тип проекта"""
    await callback.answer()
    await state.set_data({'project_type': callback.data.replace('castpr_', '')})
    await callback.message.answer('Название проекта и краткое описание (например: сериал для ТНТ, комедия)')
    await state.set_state(AddNewCasting.project_name)


@users_router.message(AddNewCasting.project_name)
async def project_name_saver(msg: Message, state: FSMContext):
    """Ловим название проекта"""
    await state.update_data({'project_name': msg.text})
    await msg.answer('Даты съёмок?')
    await state.set_state(AddNewCasting.filming_dates)


@users_router.message(AddNewCasting.filming_dates)
async def filming_dates_saver(msg: Message, state: FSMContext):
    """Ловим даты съемок"""
    await state.update_data({'filming_dates': msg.text})
    await msg.answer('Город, где проходит кастинг')
    await state.set_state(AddNewCasting.geolocation)


@users_router.message(AddNewCasting.geolocation)
async def geolocation_saver(msg: Message, state: FSMContext):
    """Ловим город кастинга"""
    await state.update_data({'geolocation': msg.text})
    await msg.answer('На какую роль вы ищете актёра?', reply_markup=role_type_choice)
    await state.set_state(AddNewCasting.role_type)


@users_router.callback_query(AddNewCasting.role_type)
async def role_type_saver(callback: CallbackQuery, state: FSMContext):
    """Ловим тип роли"""
    await callback.answer()
    await state.update_data({'role_type': callback.data.replace('castrl_', '')})
    await callback.message.answer('Пол актёра / актрисы', reply_markup=sex_choice)
    await state.set_state(AddNewCasting.sex)


@users_router.callback_query(AddNewCasting.sex)
async def sex_saver(callback: CallbackQuery, state: FSMContext):
    """Ловим пол актера"""
    await callback.answer()
    await state.update_data({'sex': callback.data.replace('sex_', '')})
    await callback.message.answer('Игровой возраст (укажите диапазон)')
    await state.set_state(AddNewCasting.playing_age)


@users_router.message(AddNewCasting.playing_age)
async def playing_age_saver(msg: Message, state: FSMContext):
    """Ловим игровой возраст"""
    try:
        playing_age = [int(a) for a in msg.text.split('-')]
        if len(playing_age) != 2:
            raise ValueError
        await state.update_data({'playing_age': msg.text})
        await msg.answer('Напишите название роли:')
        await state.set_state(AddNewCasting.role_name)
    except ValueError:
        await msg.answer('Ошибка ввода!\nВведите диапазон, который вы можете играть через дефис')


@users_router.message(AddNewCasting.role_name)
async def role_name_saver(msg: Message, state: FSMContext):
    """Ловим название роли"""
    await state.update_data({'role_name': msg.text})
    await msg.answer('Описание роли (особенности внешности, характер):')
    await state.set_state(AddNewCasting.role_description)


@users_router.message(AddNewCasting.role_description)
async def role_description_saver(msg: Message, state: FSMContext):
    """Ловим описание роли"""
    await state.update_data({'role_description': msg.text})
    await msg.answer('Есть ли дополнительные требования к кандидату (спец.навыки)?')
    await state.set_state(AddNewCasting.additional_requirements)


@users_router.message(AddNewCasting.additional_requirements)
async def additional_requirements_saver(msg: Message, state: FSMContext):
    """Ловим дополнительные требования"""
    await state.update_data({'additional_requirements': msg.text})
    await msg.answer('Какой гонорар за смену?')
    await state.set_state(AddNewCasting.fee)


@users_router.message(AddNewCasting.fee)
async def fee_saver(msg: Message, state: FSMContext):
    """Ловим гонорар"""
    await state.update_data({'fee': msg.text})
    await msg.answer('Есть ли текст для проб?', reply_markup=prob_text_have)
    await state.set_state(AddNewCasting.have_prob)


@users_router.callback_query(AddNewCasting.have_prob)
async def have_prob_saver(callback: CallbackQuery, state: FSMContext):
    """Ловим текст для проб"""
    await callback.answer()
    if callback.data == 'prob_yes':
        await callback.message.answer('Прикрепите файл с текстом для проб:')
        await state.set_state(AddNewCasting.probe_file)
    else:
        await callback.message.answer('Куда отправлять заявки? (Укажите почту или удобный мессенджер)')
        await state.update_data({'have_prob': 'no'})
        await state.set_state(AddNewCasting.contacts)


@users_router.message(AddNewCasting.probe_file)
async def file_saver(msg: Message, state: FSMContext):
    """Ловим файл с текстом"""
    if msg.document:
        await state.update_data({'file_id': msg.document.file_id, 'have_prob': 'yes'})
        await msg.answer('Куда отправлять заявки? (Укажите почту или удобный мессенджер)')
        await state.set_state(AddNewCasting.contacts)
    else:
        await msg.answer('Должен быть текстовый документ')


@users_router.message(AddNewCasting.contacts)
async def contacts_saver(msg: Message, state: FSMContext):
    """Ловим контакты"""
    await state.update_data({'contacts': msg.text})
    await msg.answer('Что указать в заявке? (Например: ФИО, возраст, ссылка на портфолио, ссылка на пробу, контакты)')
    await state.set_state(AddNewCasting.rules)


@users_router.message(AddNewCasting.rules)
async def rules_saver(msg: Message, state: FSMContext):
    """Ловим правила оформления заявок"""
    await state.update_data({'rules': msg.text})
    await msg.answer('Дополнительная информация. Например: дедлайн по заявкам / '
                     'права (для рекламы) / возможные переработка и т.д.:')
    await state.set_state(AddNewCasting.dop_info)


dict_for_msg = {
    'films': 'Кино / сериал',
    'ads': 'Реклама / клип',
    'free': 'Некоммерч. проект/короткий метр',
    'main': 'Главная',
    'second': 'Второстепенная',
    'episode': 'Эпизод',
    'mass': 'Групповка / массовка',
    'male': 'Мужской',
    'female': 'Женский',
    'yes': 'Усть',
    'no': 'Нет',
}


@users_router.message(AddNewCasting.dop_info)
async def dop_info_saver(msg: Message, state: FSMContext):
    """Ловим дополнительную информацию"""
    await state.update_data({'dop_info': msg.text})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_msg(msg, state)


async def show_cast_data_msg(msg: Message, state: FSMContext):
    """Демонстрируем кастинг"""
    cast_data = await state.get_data()
    await msg.answer('Принято, шеф! Вот как будет выглядеть кастинг:')
    await msg.answer(f'<b>Тип проекта:</b> {dict_for_msg[cast_data["project_type"]]}\n'
                     f'<b>Название проекта:</b> {cast_data["project_name"]}\n'
                     f'<b>Даты съемок:</b> {cast_data["filming_dates"]}\n'
                     f'<b>Город, где проходит кастинг:</b> {cast_data["geolocation"]}\n'
                     f'<b>Тип Роли:</b> {dict_for_msg[cast_data["role_type"]]}\n'
                     f'<b>Пол актера/актрисы:</b> {dict_for_msg[cast_data["sex"]]}\n'
                     f'<b>Игровой возраст:</b> {cast_data["playing_age"]}\n'
                     f'<b>Название роли:</b> {cast_data["role_name"]}\n'
                     f'<b>Описание роли:</b> {cast_data["role_description"]}\n'
                     f'<b>Дополнительные требования к кандидату:</b> {cast_data["additional_requirements"]}\n'
                     f'<b>Гонорар за смену:</b> {cast_data["fee"]}\n'
                     f'<b>Есть ли текст для проб:</b> {dict_for_msg[cast_data["have_prob"]]}\n'
                     f'<b>Куда отправлять заявки:</b> {cast_data["contacts"]}\n'
                     f'<b>Что указать в заявке:</b> {cast_data["rules"]}\n'
                     f'<b>Дополнительная информация:</b> {cast_data["dop_info"]}\n', reply_markup=preview_keys)


async def show_cast_data_callback(callback: CallbackQuery, state: FSMContext):
    """Демонстрируем кастинг"""
    cast_data = await state.get_data()
    await callback.message.answer('Принято, шеф! Вот как будет выглядеть кастинг:')
    await callback.message.answer(f'<b>Тип проекта:</b> {dict_for_msg[cast_data["project_type"]]}\n'
                                  f'<b>Название проекта:</b> {cast_data["project_name"]}\n'
                                  f'<b>Даты съемок:</b> {cast_data["filming_dates"]}\n'
                                  f'<b>Город, где проходит кастинг:</b> {cast_data["geolocation"]}\n'
                                  f'<b>Тип Роли:</b> {dict_for_msg[cast_data["role_type"]]}\n'
                                  f'<b>Пол актера/актрисы:</b> {dict_for_msg[cast_data["sex"]]}\n'
                                  f'<b>Игровой возраст:</b> {cast_data["playing_age"]}\n'
                                  f'<b>Название роли:</b> {cast_data["role_name"]}\n'
                                  f'<b>Описание роли:</b> {cast_data["role_description"]}\n'
                                  f'<b>Дополнительные требования к кандидату:</b> {cast_data["additional_requirements"]}\n'
                                  f'<b>Гонорар за смену:</b> {cast_data["fee"]}\n'
                                  f'<b>Есть ли текст для проб:</b> {dict_for_msg[cast_data["have_prob"]]}\n'
                                  f'<b>Куда отправлять заявки:</b> {cast_data["contacts"]}\n'
                                  f'<b>Что указать в заявке:</b> {cast_data["rules"]}\n'
                                  f'<b>Дополнительная информация:</b> {cast_data["dop_info"]}\n',
                                  reply_markup=preview_keys)


@users_router.callback_query(AddNewCasting.preview, F.data == 'get_edit')
async def get_edit_panel(callback: CallbackQuery):
    """Панель изменений"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=redactor_keys)


@users_router.callback_query(AddNewCasting.preview, F.data == 'get_public')
async def get_public_casting(callback: CallbackQuery, state: FSMContext):
    """Публикуем кастинг"""
    await callback.answer()
    cast_data = await state.get_data()
    casting_text = (f'<b>Тип проекта:</b> {dict_for_msg[cast_data["project_type"]]}\n'
                    f'<b>Название проекта:</b> {cast_data["project_name"]}\n'
                    f'<b>Даты съемок:</b> {cast_data["filming_dates"]}\n'
                    f'<b>Город, где проходит кастинг:</b> {cast_data["geolocation"]}\n'
                    f'<b>Тип Роли:</b> {dict_for_msg[cast_data["role_type"]]}\n'
                    f'<b>Пол актера/актрисы:</b> {dict_for_msg[cast_data["sex"]]}\n'
                    f'<b>Игровой возраст:</b> {cast_data["playing_age"]}\n'
                    f'<b>Название роли:</b> {cast_data["role_name"]}\n'
                    f'<b>Описание роли:</b> {cast_data["role_description"]}\n'
                    f'<b>Дополнительные требования к кандидату:</b> {cast_data["additional_requirements"]}\n'
                    f'<b>Гонорар за смену:</b> {cast_data["fee"]}\n'
                    f'<b>Есть ли текст для проб:</b> {dict_for_msg[cast_data["have_prob"]]}\n'
                    f'<b>Куда отправлять заявки:</b> {cast_data["contacts"]}\n'
                    f'<b>Что указать в заявке:</b> {cast_data["rules"]}\n'
                    f'<b>Дополнительная информация:</b> {cast_data["dop_info"]}\n')
    await bot.send_message(chat_id=MAIN_GROUP, text=casting_text)
    if cast_data['have_prob'] == 'yes':
        await bot.send_document(chat_id=MAIN_GROUP, document=cast_data['file_id'])
    await state.clear()
    if callback.from_user.id not in ADMINS:
        await callback.message.answer('Готово! Кастинг отправлен всем подходящим кандидатам.\n'
                                      'Отслеживайте заявки у себя на почте / в мессенджере\n'
                                      '<blockquote>🤖 Скоро заявки можно будет принимать прямо здесь, мы работаем над '
                                      'созданием удобного личного кабинета, оставайтесь с нами.</blockquote>')
        await callback.message.answer('Разместить ещё один кастинг?', reply_markup=recycle)
    else:
        await callback.message.answer('Выберете действие:', reply_markup=admin_main)


@users_router.callback_query(AddNewCasting.preview, F.data != 'get_public')
async def start_edit_cast(callback: CallbackQuery, state: FSMContext):
    """Запуск редактора"""
    await callback.answer()
    edit_dict = {
        'edit_project_type': (
            'Кастинг в какой проект вы хотите опубликовать?\nВыберите категорию:', project_type_choice,
            AddNewCasting.edit_project_type),
        'edit_project_name': ('Название проекта и краткое описание (например: сериал для ТНТ, комедия)', None,
                              AddNewCasting.edit_project_name),
        'edit_filming_dates': ('Даты съемок', None, AddNewCasting.edit_filming_dates),
        'edit_geolocation': ('Город, где проходит кастинг:', None, AddNewCasting.edit_geolocation),
        'edit_role_type': ('На какую роль вы ищете актёра?', role_type_choice, AddNewCasting.edit_role_type),
        'edit_sex': ('Пол актера/актрисы:', sex_choice, AddNewCasting.edit_sex),
        'edit_playing_age': ('Игровой возраст (укажите диапазон)', None, AddNewCasting.edit_playing_age),
        'edit_role_name': ('Название роли:', None, AddNewCasting.edit_role_name),
        'edit_role_description': (
            'Описание роли (особенности внешности, характер):', None, AddNewCasting.edit_role_description),
        'edit_additional_requirements': (
            'Дополнительные требования к кандидату (спец.навыки)', None, AddNewCasting.edit_additional_requirements),
        'edit_fee': ('Какой гонорар за смену?', None, AddNewCasting.edit_fee),
        'edit_have_prob': ('Есть ли текст для проб?', prob_text_have, AddNewCasting.edit_have_prob),
        'edit_contacts': (
            'Куда отправлять заявки? (Укажите почту или удобный мессенджер)', None, AddNewCasting.edit_contacts),
        'edit_rules': (
            'Что указать в заявке? (Например: ФИО, возраст, ссылка на портфолио, ссылка на пробу, контакты)', None,
            AddNewCasting.edit_rules),
        'edit_dop_info': ('Дополнительная информация. Например: дедлайн по заявкам / '
                          'права (для рекламы) / возможные переработка и т.д.:', None, AddNewCasting.edit_dop_info),
    }
    await callback.message.answer(text=edit_dict[callback.data][0], reply_markup=edit_dict[callback.data][1])
    await state.set_state(edit_dict[callback.data][2])


@users_router.message(AddNewCasting.edit_project_name)
async def edit_project_name(msg: Message, state: FSMContext):
    """Редактируем название проекта"""
    await state.update_data({'project_name': msg.text})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_msg(msg, state)


@users_router.message(AddNewCasting.edit_filming_dates)
async def edit_filming_dates(msg: Message, state: FSMContext):
    """Редактируем дату съемок"""
    await state.update_data({'filming_dates': msg.text})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_msg(msg, state)


@users_router.message(AddNewCasting.edit_geolocation)
async def edit_geolocation(msg: Message, state: FSMContext):
    """Редактируем город кастинга"""
    await state.update_data({'geolocation': msg.text})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_msg(msg, state)


@users_router.message(AddNewCasting.edit_playing_age)
async def edit_playing_age(msg: Message, state: FSMContext):
    """Редактируем игровой возраст"""
    try:
        playing_age = [int(a) for a in msg.text.split('-')]
        if len(playing_age) != 2:
            raise ValueError
        await state.update_data({'playing_age': msg.text})
        await state.set_state(AddNewCasting.preview)
        await show_cast_data_msg(msg, state)
    except ValueError:
        await msg.answer('Ошибка ввода!\nВведите диапазон, который вы можете играть через дефис')


@users_router.message(AddNewCasting.edit_role_name)
async def edit_role_name(msg: Message, state: FSMContext):
    """Редактируем название роли"""
    await state.update_data({'role_name': msg.text})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_msg(msg, state)


@users_router.message(AddNewCasting.edit_role_description)
async def edit_role_description(msg: Message, state: FSMContext):
    """Редактируем описание роли"""
    await state.update_data({'role_description': msg.text})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_msg(msg, state)


@users_router.message(AddNewCasting.edit_additional_requirements)
async def edit_additional_requirements(msg: Message, state: FSMContext):
    """Редактируем дополнительные требования"""
    await state.update_data({'additional_requirements': msg.text})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_msg(msg, state)


@users_router.message(AddNewCasting.edit_fee)
async def edit_fee(msg: Message, state: FSMContext):
    """Редактируем гонорар"""
    await state.update_data({'fee': msg.text})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_msg(msg, state)


@users_router.message(AddNewCasting.edit_contacts)
async def edit_contacts(msg: Message, state: FSMContext):
    """Редактируем контакты"""
    await state.update_data({'contacts': msg.text})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_msg(msg, state)


@users_router.message(AddNewCasting.edit_rules)
async def edit_rules(msg: Message, state: FSMContext):
    """Редактируем правила заявки"""
    await state.update_data({'rules': msg.text})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_msg(msg, state)


@users_router.message(AddNewCasting.edit_dop_info)
async def edit_dop_info(msg: Message, state: FSMContext):
    """Редактируем дополнительную информацию"""
    await state.update_data({'dop_info': msg.text})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_msg(msg, state)


@users_router.callback_query(AddNewCasting.edit_project_type)
async def edit_project_type(callback: CallbackQuery, state: FSMContext):
    """Редактируем проекта"""
    await callback.answer()
    await state.update_data({'project_type': callback.data.replace('castpr_', '')})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_callback(callback, state)


@users_router.callback_query(AddNewCasting.edit_sex)
async def edit_sex(callback: CallbackQuery, state: FSMContext):
    """Редактируем пол актера"""
    await callback.answer()
    await state.update_data({'sex': callback.data.replace('sex_', '')})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_callback(callback, state)


@users_router.callback_query(AddNewCasting.edit_have_prob)
async def edit_have_prob(callback: CallbackQuery, state: FSMContext):
    """Редактируем текст для проб"""
    await callback.answer()
    if callback.data == 'prob_yes':
        await state.set_state(AddNewCasting.new_text_file)
        await callback.message.answer('Прикрепите файл с текстом для проб:')
    else:
        await state.update_data({'have_prob': 'no'})
        await state.set_state(AddNewCasting.preview)
        await show_cast_data_callback(callback, state)


@users_router.message(AddNewCasting.new_text_file)
async def catch_new_text_prob(msg: Message, state: FSMContext):
    """Ловим новый текстовый файл"""
    await state.update_data({'file_id': msg.document.file_id, 'have_prob': 'yes'})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_msg(msg, state)


@users_router.callback_query(AddNewCasting.edit_role_type)
async def edit_role_type(callback: CallbackQuery, state: FSMContext):
    """Редактируем тип роли"""
    await callback.answer()
    await state.update_data({'role_type': callback.data.replace('castrl_', '')})
    await state.set_state(AddNewCasting.preview)
    await show_cast_data_callback(callback, state)
