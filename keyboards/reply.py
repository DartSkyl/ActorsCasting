from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup


# ====================
# Администраторская клавиатура
# ====================

admin_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='База данных кастингов'), KeyboardButton(text='Подписчики')],
    [KeyboardButton(text='Настройки парсера')],
    [KeyboardButton(text='Добавить кастинг')]
], resize_keyboard=True)

add_new_casting = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Опубликовать кастинг')]
], one_time_keyboard=True, resize_keyboard=True)

# ====================
# Пользовательская клавиатура
# ====================

pay_choice = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Подписка на месяц - 599₽')],
    [KeyboardButton(text='Подписка на 3 месяца - 1370₽ (-24%)')]
], one_time_keyboard=True, resize_keyboard=True)


# role_choice = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Актёр, ищущий кастинги')],
#     [KeyboardButton(text='Кастинг-директор, желающий разместить кастинг')]
# ], one_time_keyboard=True, resize_keyboard=True)

# first_answer_button = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Да, было бы здорово! А что, так можно было?')]
# ], one_time_keyboard=True, resize_keyboard=True)


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
