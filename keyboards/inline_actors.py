from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup


sex_choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Мужской', callback_data='sex_male')],
    [InlineKeyboardButton(text='Женский', callback_data='sex_female')]
])

education_choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Получил диплом. гос. образца', callback_data='educ_vuz')],
    [InlineKeyboardButton(text='Прошёл курсы актерского мастерства', callback_data='educ_curs')],
    [InlineKeyboardButton(text='Актерского образования нет', callback_data='educ_none')]
])

experience_choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Опыта нет, я - новичок', callback_data='exp_null')],
    [InlineKeyboardButton(text='Снималась(ся) только в рекламе / массовках/групповках', callback_data='exp_ads_')],
    [InlineKeyboardButton(text='Снималась(ся) в эпизодах / некоммерческих проектах', callback_data='exp_free_')],
    [InlineKeyboardButton(text='Есть второстепенные / главные роли в полнометражных фильмах/сериалах', callback_data='exp_main')]
])

role_interested = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Кастинги в кино', callback_data='choice_films')],
    [InlineKeyboardButton(text='Кастинги в рекламу', callback_data='choice_ads')],
    [InlineKeyboardButton(text='Театральные проекты', callback_data='choice_theater')],
    [InlineKeyboardButton(text='Главные и второстепенные роли', callback_data='choice_main_role')],
    [InlineKeyboardButton(text='Эпизоды', callback_data='choice_episode')],
    [InlineKeyboardButton(text='Групповка/массовка', callback_data='choice_mass')],
    [InlineKeyboardButton(text='Некоммерческие проекты / фестивальные короткометражные фильмы молодых режиссёров', callback_data='choice_free')],
    [InlineKeyboardButton(text='Готово', callback_data='ready')]
])


editor_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить ФИО', callback_data='edit_actor_name')],
    [InlineKeyboardButton(text='Изменить пол', callback_data='edit_sex')],
    [InlineKeyboardButton(text='Изменить возраст по паспорту', callback_data='edit_passport_age')],
    [InlineKeyboardButton(text='Изменить игровой возраст', callback_data='edit_playing_age')],
    [InlineKeyboardButton(text='Изменить образование', callback_data='edit_education')],
    [InlineKeyboardButton(text='Изменить город проживания', callback_data='edit_geo_location')],
    [InlineKeyboardButton(text='Изменить контактные данные', callback_data='edit_contacts')],
    [InlineKeyboardButton(text='Изменить контактные данные агента', callback_data='edit_agent_contact')],
    [InlineKeyboardButton(text='Изменить опыт', callback_data='edit_have_experience')],
    [InlineKeyboardButton(text='Изменить портфолио', callback_data='edit_portfolio')],
    [InlineKeyboardButton(text='Изменить соц. сети', callback_data='edit_social')],
    [InlineKeyboardButton(text='Изменить то, что интересует', callback_data='edit_roles_type_interest')],
])
