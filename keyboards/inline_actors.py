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
    [InlineKeyboardButton(text='Кастинги в кино', callback_data='choice_p_films')],
    [InlineKeyboardButton(text='Кастинги в сериал', callback_data='choice_p_series')],
    [InlineKeyboardButton(text='Кастинги в рекламу', callback_data='choice_p_ads')],
    [InlineKeyboardButton(text='Театральные проекты', callback_data='choice_p_theater')],
    [InlineKeyboardButton(text='Некоммерческие проекты / фестивальные короткометражные фильмы молодых режиссёров',
                          callback_data='choice_p_free')],
    [InlineKeyboardButton(text='Главные и второстепенные роли', callback_data='choice_r_main_role')],
    [InlineKeyboardButton(text='Эпизоды', callback_data='choice_r_episode')],
    [InlineKeyboardButton(text='Групповка/массовка', callback_data='choice_r_mass')],
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

setup_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить возраст по паспорту', callback_data='setup_passport_age')],
    [InlineKeyboardButton(text='Изменить игровой возраст', callback_data='setup_playing_age')],
    [InlineKeyboardButton(text='Изменить образование', callback_data='setup_education')],
    [InlineKeyboardButton(text='Изменить город проживания', callback_data='setup_geo_location')],
    [InlineKeyboardButton(text='Изменить контактные данные', callback_data='setup_contacts')],
    [InlineKeyboardButton(text='Изменить контактные данные агента', callback_data='setup_agent_contact')],
    [InlineKeyboardButton(text='Изменить опыт', callback_data='setup_have_experience')],
    [InlineKeyboardButton(text='Изменить портфолио', callback_data='setup_portfolio')],
    [InlineKeyboardButton(text='Изменить соц. сети', callback_data='setup_social')],
    [InlineKeyboardButton(text='Изменить то, что интересует', callback_data='setup_roles_type_interest')],
])


async def button_for_casting(chat_id, message_id):
    """Клавиатура формирует кнопку для предоставления оригинала сообщения о кастинге"""
    buttons = [
        [InlineKeyboardButton(text='Показать оригинал', callback_data=f'origin_{chat_id}_{message_id}')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
