from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from pyrogram.errors.exceptions.bad_request_400 import ApiIdInvalid
from pyrogram.errors.exceptions.not_acceptable_406 import PhoneNumberInvalid

from utils.admin_router import admin_router
from utils.user_bot_parser import UserBotParser, parser_start, parser_stop, parser_status
from keyboards.inline_admin import add_user_bot, check_data_keyboard
from keyboards.reply import cancel_button
from states import AdminStates
from loader import techno_dict


@admin_router.message(Command('user_bot'))
@admin_router.message(F.text == 'Настройки парсера')
async def open_user_bot_menu(msg: Message):
    """Открываем меню взаимодействия с юзер-ботом"""
    await msg.answer('Выберете действие:', reply_markup=add_user_bot)


@admin_router.message(Command('restart'))
async def restart_bot(msg: Message):
    """Для непредвиденных случаев"""
    import os
    await msg.answer('Перезагрузка...')
    os.system('systemctl restart casting.service')


@admin_router.callback_query(F.data.startswith('parser_'))
async def parser_start_func(callback: CallbackQuery):
    """Запускаем парсер"""
    await callback.answer()
    try:
        if callback.data == 'parser_start':
            await parser_start()
            await callback.message.answer('Парсер запущен')
        elif callback.data == 'parser_stop':
            await parser_stop()
            await callback.message.answer('Парсер остановлен')
        else:
            await callback.message.answer(f'Парсер {"запущен" if await parser_status() else "остановлен"}')
    except KeyError:
        await callback.message.answer('Ошибка! Юзер-бот не установлен!')


# ====================
# Добавление юзер-бота
# ====================


@admin_router.callback_query(F.data == 'add_user_bot')
async def start_add_user_bot(callback: CallbackQuery, state: FSMContext):
    """Начинаем добавление/замену юзер-бота"""
    await callback.answer()
    await state.set_state(AdminStates.api_id_input)
    await callback.message.answer(text='Введите api_id:', reply_markup=cancel_button)


@admin_router.message(AdminStates.api_id_input, F.text.isdigit())
async def api_hash_input(msg: Message, state: FSMContext):
    """Здесь мы ловим api_id и предлагаем ввести api_hash"""
    await state.set_data({'api_id': msg.text})
    await state.set_state(AdminStates.api_hash_input)
    await msg.answer(text='Теперь введите api_hash:')


@admin_router.message(AdminStates.api_hash_input, F.text != 'Отмена')
async def phone_number_input(msg: Message, state: FSMContext):
    """Здесь мы ловим api_has и предлагаем ввести номер телефона"""
    await state.update_data({'api_hash': msg.text})
    await state.set_state(AdminStates.phone_number_input)

    await msg.answer(text='Теперь введите номер телефона в международном формате:')


@admin_router.message(AdminStates.phone_number_input, F.text.regexp(r'\+\d{10,}'))
async def phone_number_adding(msg: Message, state: FSMContext):
    """Вынесем ловлю телефона в отдельный хэндлер для удобства"""
    await state.update_data({'phone_number': msg.text})
    await state.set_state(AdminStates.check_data)
    await check_the_data(msg=msg, state=state)


async def check_the_data(msg: Message, state: FSMContext):
    """Даем пользователю проверить правильность введенных данных и возможность их исправить"""

    account_data = await state.get_data()
    msg_text = (f'Проверьте правильность введенных данных:\n\n'
                f'api_id: {account_data["api_id"]}\n'
                f'api_hash: {account_data["api_hash"]}\n'
                f'Номер телефона: {account_data["phone_number"]}')
    await msg.answer(text=msg_text, reply_markup=check_data_keyboard)


@admin_router.callback_query(AdminStates.check_data, F.data != 'correct')
async def change_the_data(callback: CallbackQuery, state: FSMContext):
    """Здесь пользователь либо меняет какие-нибудь данные либо идет дальше"""
    await callback.answer()
    change_states = {
        'change_api_id': (AdminStates.change_api_id, 'Введите api_id:'),
        'change_api_hash': (AdminStates.change_api_hash, 'Введите api_hash:'),
        'change_phone_number': (AdminStates.change_phone_number, 'Введите номер телефона')
    }
    await state.set_state(change_states[callback.data][0])
    await callback.message.answer(text=change_states[callback.data][1])


@admin_router.callback_query(AdminStates.check_data, F.data == 'correct')
async def auth_function(callback: CallbackQuery, state: FSMContext):
    """Здесь начинается авторизация добавляемого аккаунта"""
    await callback.answer()
    account_data = await state.get_data()
    new_account = UserBotParser(
        api_id=account_data['api_id'],
        api_hash=account_data['api_hash'],
        phone_number=account_data['phone_number']
    )

    try:
        await callback.message.answer(text='Сейчас вам придет код для авторизации на аккаунт, который вы добавляете!\n'
                                           'Введите его:')
        # Ловим и сохраняем хэш кода авторизации для дальнейшего использования
        code_hash = await new_account.start_session()
        await state.update_data({'code_hash': code_hash, 'new_account': new_account})

        await state.set_state(AdminStates.code_input)

    except ApiIdInvalid:
        await callback.message.answer(text='Вы ввели неверный <b>api_id или api_hash</b>!\n'
                                           'Перепроверьте все и введи заново')
        await state.set_state(AdminStates.check_data)

    except PhoneNumberInvalid:
        await callback.message.answer(text='Вы ввели неверный <b>номер телефона</b>!\n'
                                           'Перепроверьте все и введи заново')
        await state.set_state(AdminStates.check_data)


@admin_router.message(AdminStates.code_input, F.text.regexp(r'\d{5}'))
async def auth_code_input(msg: Message, state: FSMContext):
    """Пользователь вводит код авторизации и здесь мы его ловим"""
    account_data = await state.get_data()
    await account_data['new_account'].authorization_and_start(code_hash=account_data['code_hash'], code=str(msg.text))

    # Сохраняем получившегося юзер-бота в словарь
    techno_dict['parser'] = account_data['new_account']

    await msg.answer(text='Юзер-бот добавлен!')
    await state.clear()


@admin_router.message(AdminStates.code_input, F.text != '🚫 Отмена')
async def code_error_input(msg: Message):
    """Некорректный ввод кода"""
    await msg.answer(text='Код содержит пять цифр! Повторите ввод:')


@admin_router.message(AdminStates.change_api_id, F.text.isdigit())
async def change_api_id(msg: Message, state: FSMContext):
    """Здесь мы пользователь меняет api_id"""
    await state.update_data({'api_id': msg.text})
    await check_the_data(msg=msg, state=state)
    await state.set_state(AdminStates.check_data)


@admin_router.message(AdminStates.change_api_id, F.text != '🚫 Отмена')
@admin_router.message(AdminStates.api_id_input, F.text != '🚫 Отмена')
async def api_error_input(msg: Message):
    """При не правильном вводе api_id"""
    await msg.answer(text='api_id состоит только из цифр! Повторите ввод')


@admin_router.message(AdminStates.change_api_hash, F.text != '🚫 Отмена')
async def change_api_hash(msg: Message, state: FSMContext):
    """Здесь мы пользователь меняет api_hash"""
    await state.update_data({'api_hash': msg.text})
    await check_the_data(msg=msg, state=state)
    await state.set_state(AdminStates.check_data)


@admin_router.message(AdminStates.change_phone_number, F.text.regexp(r'\+\d{10,}'))
async def change_phone_number(msg: Message, state: FSMContext):
    """Здесь мы пользователь меняет телефонный номер"""
    await state.update_data({'phone_number': msg.text})
    await check_the_data(msg=msg, state=state)
    await state.set_state(AdminStates.check_data)


@admin_router.message(AdminStates.change_phone_number, F.text != '🚫 Отмена')
@admin_router.message(AdminStates.phone_number_input, F.text != '🚫 Отмена')
async def phone_nuber_error_input(msg: Message):
    """При не правильном вводе телефонного номера"""
    await msg.answer(text='Телефонный номер должен быть в международном формате!\n'
                          'Пример +79221110500\nПовторите ввод!')
