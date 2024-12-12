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

casting_bd_period = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='За сегодня', callback_data='period_today')],
    [InlineKeyboardButton(text='За прошедшие 7 дней', callback_data='period_week')],
    [InlineKeyboardButton(text='За прошедшие 30 дней', callback_data='period_month')],
    [InlineKeyboardButton(text='За весь период', callback_data='period_all_days')],
    [InlineKeyboardButton(text='Свой промежуток', callback_data='period_user_date')]
])


async def button_for_casting_admin(origin, casting_hash, viewing=False):
    """Клавиатура формирует кнопку для предоставления оригинала сообщения о кастинге"""
    if not viewing:
        buttons = [
            [InlineKeyboardButton(text='Подробнее', callback_data=f'view_{casting_hash}')],
            [InlineKeyboardButton(text='Показать оригинал', url=origin)],
            [InlineKeyboardButton(text='Удалить', callback_data=f'rm_admin_{casting_hash}')]
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text='Показать оригинал', url=origin)],
            [InlineKeyboardButton(text='Удалить', callback_data=f'rm_admin_{casting_hash}')]
        ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


check_new_casting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить описание кастинга', callback_data='new_casting_edit_text')],
    [InlineKeyboardButton(text='Изменить файл с текстом', callback_data='new_casting_edit_file')]
])
