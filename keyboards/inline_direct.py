from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup


project_type_choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Кино / сериал', callback_data='castpr_films')],
    [InlineKeyboardButton(text='Реклама / клип', callback_data='castpr_ads')],
    [InlineKeyboardButton(text='Некоммерч. проект/короткий метр', callback_data='castpr_free')]
])

role_type_choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Главная', callback_data='castrl_main')],
    [InlineKeyboardButton(text='Второстепенная', callback_data='castrl_second')],
    [InlineKeyboardButton(text='Эпизод', callback_data='castrl_episode')],
    [InlineKeyboardButton(text='Групповка / массовка', callback_data='castrl_mass')]
])

sex_choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Мужской', callback_data='sex_male')],
    [InlineKeyboardButton(text='Женский', callback_data='sex_female')]
])

prob_text_have = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Есть', callback_data='prob_yes')],
    [InlineKeyboardButton(text='Нету', callback_data='prob_no')]
])

redactor_keys = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить "Тип проекта"', callback_data='edit_project_type')],
    [InlineKeyboardButton(text='Изменить "Название проекта"', callback_data='edit_project_name')],
    [InlineKeyboardButton(text='Изменить "Даты съемок"', callback_data='edit_filming_dates')],
    [InlineKeyboardButton(text='Изменить "Город, где проходит кастинг"', callback_data='edit_geolocation')],
    [InlineKeyboardButton(text='Изменить "Тип Роли"', callback_data='edit_role_type')],
    [InlineKeyboardButton(text='Изменить "Пол актера/актрисы"', callback_data='edit_sex')],
    [InlineKeyboardButton(text='Изменить "Игровой возраст"', callback_data='edit_playing_age')],
    [InlineKeyboardButton(text='Изменить "Название роли"', callback_data='edit_role_name')],
    [InlineKeyboardButton(text='Изменить "Описание роли"', callback_data='edit_role_description')],
    [InlineKeyboardButton(text='Изменить "Дополнительные требования к кандидату"', callback_data='edit_additional_requirements')],
    [InlineKeyboardButton(text='Изменить "Гонорар за смену"', callback_data='edit_fee')],
    [InlineKeyboardButton(text='Изменить "текст для проб"', callback_data='edit_have_prob')],
    [InlineKeyboardButton(text='Изменить "Куда отправлять заявки"', callback_data='edit_contacts')],
    [InlineKeyboardButton(text='Изменить "Что указать в заявке"', callback_data='edit_rules')],
    [InlineKeyboardButton(text='Изменить "Дополнительная информация"', callback_data='edit_dop_info')],
    [InlineKeyboardButton(text='✅ Опубликовать кастинг', callback_data='get_public')]
])

recycle = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Опубликовать кастинг', callback_data='director')]
])
