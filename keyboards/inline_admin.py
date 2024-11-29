from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup


add_user_bot = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить/Заменить юзер-бота', callback_data='add_user_bot')],
    [InlineKeyboardButton(text='Запустить парсер', callback_data='parser_start')],
    [InlineKeyboardButton(text='Остановить парсер', callback_data='parser_stop')],
    [InlineKeyboardButton(text='Статус парсера', callback_data='parser_status')]
])

check_data_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Все верно!', callback_data='correct')],
    [InlineKeyboardButton(text='Изменить api_id', callback_data='change_api_id')],
    [InlineKeyboardButton(text='Изменить api_hash', callback_data='change_api_hash')],
    [InlineKeyboardButton(text='Изменить номер телефона', callback_data='change_phone_number')]
])
