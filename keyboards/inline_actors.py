from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from config import PAYWALL_URL


first_start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Актёр (искать кастинги)', callback_data='actor')],
    [InlineKeyboardButton(text='Кастинг-директор (разместить кастинг)', callback_data='director')]
])

cycle_for_direct = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да, с радостью 😊', callback_data='director')]
])

first_answer = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да, было бы здорово!', callback_data='reg_start')],
    [InlineKeyboardButton(text='А что, так можно было?', callback_data='reg_start')]
])

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
    [InlineKeyboardButton(text='Съёмки в рекламе/ массовках/групповках', callback_data='exp_ads_')],
    [InlineKeyboardButton(text='Эпизоды/ некоммерч. проекты', callback_data='exp_free_')],
    [InlineKeyboardButton(text='Есть второстеп./ главные роли', callback_data='exp_main')]
])

role_interested = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Кастинги в кино', callback_data='choice_films')],
    [InlineKeyboardButton(text='Кастинги в рекламу', callback_data='choice_ads')],
    [InlineKeyboardButton(text='Некоммерческие / фестивальные проекты',
                          callback_data='choice_free')],
    [InlineKeyboardButton(text='Готово', callback_data='ready')]
])

editor_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить ФИО', callback_data='edit_actor_name')],
    [InlineKeyboardButton(text='Изменить пол', callback_data='edit_sex')],
    [InlineKeyboardButton(text='Изменить возраст по паспорту', callback_data='edit_passport_age')],
    [InlineKeyboardButton(text='Изменить игровой возраст', callback_data='edit_playing_age')],
    [InlineKeyboardButton(text='Изменить образование', callback_data='edit_education')],
    [InlineKeyboardButton(text='Изменить опыт', callback_data='edit_have_experience')],
    [InlineKeyboardButton(text='Изменить портфолио', callback_data='edit_portfolio')],
    [InlineKeyboardButton(text='Изменить соц. сети', callback_data='edit_social')],
    [InlineKeyboardButton(text='Изменить гонорар', callback_data='edit_fee')],
    [InlineKeyboardButton(text='Изменить то, что интересует', callback_data='edit_roles_type_interest')],
    [InlineKeyboardButton(text='✅ Зарегистрироваться', callback_data='registration')]
])

setup_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить возраст по паспорту', callback_data='setup_passport_age')],
    [InlineKeyboardButton(text='Изменить игровой возраст', callback_data='setup_playing_age')],
    [InlineKeyboardButton(text='Изменить образование', callback_data='setup_education')],
    [InlineKeyboardButton(text='Изменить опыт', callback_data='setup_have_experience')],
    [InlineKeyboardButton(text='Изменить портфолио', callback_data='setup_portfolio')],
    [InlineKeyboardButton(text='Изменить соц. сети', callback_data='setup_social')],
    [InlineKeyboardButton(text='Изменить гонорар', callback_data='setup_fee')],
    [InlineKeyboardButton(text='Изменить то, что интересует', callback_data='setup_roles_type_interest')],
])


async def button_for_casting(message_id, casting_hash=None, casting_hash_rm=None):
    """Клавиатура формирует кнопку для предоставления оригинала сообщения о кастинге"""
    if casting_hash:
        buttons = [
            [InlineKeyboardButton(text='Показать оригинал', callback_data=f'origin_{message_id}')],
            [InlineKeyboardButton(text='Добавить в избранное', callback_data=f'favorites_{casting_hash}')]
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text='Показать оригинал', callback_data=f'origin_{message_id}')],
            [InlineKeyboardButton(text='Удалить из избранного', callback_data=f'rm_favorites_{casting_hash_rm}')]
        ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def paid_url(user_id, is_paid):
    """Возвращает кнопку со ссылкой для оплаты"""
    if not is_paid:
        button = [[InlineKeyboardButton(text='Оплатить подписку', url=f'{PAYWALL_URL + str(user_id)}')]]
    else:
        button = [[InlineKeyboardButton(text='Управление подпиской', url=f'{PAYWALL_URL + str(user_id)}')]]
    return InlineKeyboardMarkup(inline_keyboard=button)


i_want_1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🤩 Хочу получать кастинги', callback_data='i_want')]
])

i_want_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='😎 Выбрать вариант подписки', callback_data='i_want')]
])

i_want_3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎬 Оформить подписку', callback_data='i_want')]
])

i_want_4 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Я сам(а) могу поискать кастинги', callback_data='i_can')],
    [InlineKeyboardButton(text='Для меня это дорого', callback_data='i_expensive')],
    [InlineKeyboardButton(text='Не доверяю роботам', callback_data='i_not_trust')]
])

i_want_5 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='☕ Угостить бота кофе', callback_data='i_want')]
])


async def pay_page(user_id):
    """Возвращает кнопку со ссылкой для оплаты"""
    buttons = [
        [InlineKeyboardButton(text='Подписка на месяц - 599₽', url=f'{PAYWALL_URL + str(user_id)}')],
        [InlineKeyboardButton(text='Подписка на 3 месяца - 1370₽ (-24%)', url=f'{PAYWALL_URL + str(user_id)}')],
        [InlineKeyboardButton(text='Бесплатная пробная неделя', url=f'{PAYWALL_URL + str(user_id)}')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
