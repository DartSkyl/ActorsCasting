from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup


# ====================
# Администраторская клавиатура
# ====================

admin_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='База данных кастингов')],
    [KeyboardButton(text='Настройки парсера')],
    [KeyboardButton(text='Статистика')]
], resize_keyboard=True)

# ====================
# Пользовательская клавиатура
# ====================


role_choice = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Актёр, ищущий кастинги')],
    [KeyboardButton(text='Кастинг-директор, желающий разместить кастинг')]
], one_time_keyboard=True, resize_keyboard=True)

cancel_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🚫 Отмена')]
], one_time_keyboard=True, resize_keyboard=True)

skip_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Пропустить')]
], one_time_keyboard=True, resize_keyboard=True)

ready_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Готово')]
], one_time_keyboard=True, resize_keyboard=True)

registry_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Зарегистрироваться')]
], one_time_keyboard=True, resize_keyboard=True)

main_menu_actor = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Подписка'), KeyboardButton(text='Избранное')],
    [KeyboardButton(text='Настройки профиля')]
], resize_keyboard=True)
