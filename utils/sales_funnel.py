import asyncio
from datetime import date, datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError

from keyboards.inline_actors import i_want_1, i_want_2, i_want_3, i_want_4, i_want_5
from loader import techno_dict
from utils.user_bot_parser import check_paid


async def first_message(msg: Message, user_id):
    """Отправляем пользователю сообщение с напоминанием о себе"""
    try:
        await techno_dict['sales_funnel'].remove_job('1_', user_id)
        if not await check_paid(int(user_id)):
            msg_text = """
Смотри, как это работает:
• Я <b>собираю кастинги</b> со всех популярных источников (включая те, о которых знают только самые хитренькие).
• <b>Фильтрую нерелевантное</b>, чтобы не присылать тебе роли “дуб в рекламе удобрений”.
• <b>Договариваюсь с кастинг-директорами</b> о публикации кастингов  напрямую на нашей платформе, чтобы ты узнал о них первым.
• И <b>присылаю тебе</b> только то, что подходит, с учетом гонораров, которые ты хочешь получать и проектов, в которых хочешь сниматься.

🤖Хочешь?
После подписки я включаюсь и начинаю работать на полную мощность!
            """
            await msg.answer(msg_text, reply_markup=i_want_1)
            await asyncio.sleep(3600)  # Через час
            if not await check_paid(int(user_id)):
                await second_message(msg, user_id)

    except TelegramForbiddenError:
        pass


async def second_message(msg: Message, user_id):
    """Отправляем пользователю сообщение с напоминанием о себе"""
    try:
        msg_text = """
Привет, звезда! Я уже всё про тебя знаю: возраст, типаж, твои интересы. Всё, что осталось — это найти тебе роль.
Но тут небольшая загвоздка… У меня лапки. Вернее, подписка. Без неё я не могу включить свой суперрадар и находить кастинги специально для тебя.
    """
        await msg.answer(msg_text, reply_markup=i_want_2)
        await asyncio.sleep(1800)  # Через полчаса
        if not await check_paid(int(user_id)):
            await third_message(msg, user_id)
    except TelegramForbiddenError:
        pass


async def third_message(msg: Message, user_id):
    """Отправляем пользователю сообщение с напоминанием о себе"""
    try:
        msg_text = """
<b>Вас утвердили на роль!</b>

Заветные слова, которые хочет услышать каждый актёр. И я здесь для того, чтобы тебе в этом помочь.
Пока ты читаешь это сообщение, где-то уже опубликовали новый кастинг. Возможно, именно тот, который станет для тебя стартом в большой карьере.
Не упускай возможности. Подпишись, и я сразу начну искать для тебя кастинги.
    """
        await msg.answer(msg_text, reply_markup=i_want_3)
        await asyncio.sleep(3600)  # Через час
        if not await check_paid(int(user_id)):
            await fourth_message(msg, user_id)
    except TelegramForbiddenError:
        pass


async def fourth_message(msg: Message, user_id):
    """Отправляем пользователю сообщение с напоминанием о себе"""
    try:
        msg_text = 'Давай поговорим по душам?\n\nПочему ты меня не хочешь?'
        await msg.answer(msg_text, reply_markup=i_want_4)
        if not await check_paid(int(user_id)):
            await techno_dict['sales_funnel'].second_step(user_id=user_id, message=msg)
    except TelegramForbiddenError:
        pass


async def messages_with_objections(msg: Message, user_id):
    """Запуск каскада сообщений с возражениями на следующий день при отсутствии активности"""
    try:
        if not await check_paid(int(user_id)):
            msg_text_1 = ('Давай посчитаем. Если ты тратишь хотя бы <b>2 часа в день</b> на поиск кастингов, это уже <b>60 '
                          'часов в месяц.</b> '
                          'Эти часы ты мог(ла) бы потратить на репетиции, прокачку своих актерских навыков или просто отдых. '
                          'Пока ты листаешь десятки сообщений в чатах, кто-то уже подаёт заявку на роль. '
                          'А это значит, что я не только экономлю твоё время, но и увеличиваю твои шансы на успех.\n\n'
                          '🤖 Так что вопрос: зачем тратить время, если я могу это сделать лучше и быстрее?')
            await msg.answer(msg_text_1, reply_markup=i_want_2)  # Отправляется в 9 по МСК
            await techno_dict['sales_funnel'].remove_job('2_', user_id)

            await asyncio.sleep(10800)  # Отправляется в 12 по МСК
            if not await check_paid(int(user_id)):
                msg_text_2 = ('Моя подписка стоит как пара чашек латте в кафе. Съемка даже в одном небольшом эпизоде '
                              'тебе окупит её на месяцы вперёд. Я уже не говорю о том, что ты можешь получить ту '
                              'самую роль, которую так давно ищешь. А там и моргнуть не успеешь, как тебя уже '
                              'фотографируют у стенда на премьере фильма.\n\n'
                              '🤖 Неужели это не стоит того, чтобы угостить меня кофе?')
                await msg.answer(msg_text_2, reply_markup=i_want_5)

                await asyncio.sleep(3600)  # Отправляется в 13 по МСК
                if not await check_paid(int(user_id)):
                    msg_text_3 = (
                        'Я не просто робот, я ИИ. И у меня есть значительные преимущества, это как <b>супер-сила, '
                        'которой ты'
                        'можешь воспользоваться</b>. Некоторые уже попробовали и оценили. Вот, смотри, что они пишут:\n\n'
                        '“Я думал, что это очередной бесполезный сервис, но когда он мне начал присылать кастинги, '
                        'я был удивлен, как точно под мой запрос он их находит. И присылает намного больше, чем я '
                        'находил самостоятельно. Видимо действительно, я не о всех чатах знаю.”\n\n'
                        '“Удобно, что бот присылает кастинги сразу в личку. Теперь я первая, кто подаёт '
                        'заявку)) Блин, где вы были раньше?)».')
                    await msg.answer(msg_text_3, reply_markup=i_want_1)
    except TelegramForbiddenError:
        pass


class SalesFunnel:
    """Класс для создания воронки продаж. Если после регистрации и выходе предложения об оплате
    пользователь бездействует"""

    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._scheduler.start()

    async def first_step(self, user_id, message: Message):
        """Первая ступень воронки продаж"""
        self._scheduler.add_job(
            id='1_' + user_id,
            func=first_message,
            kwargs={'user_id': user_id, 'msg': message},
            trigger='interval',
            minutes=15,
            max_instances=1,
        )

    async def second_step(self, user_id, message: Message):
        """Вторая ступень воронки продаж. Активируется на следующий день в 9 утра"""
        # Создаём объект datetime для сегодняшней даты и времени 00:00
        current_date = datetime.combine(date.today(), datetime.min.time())
        # Добавляем один день и 9 часов к текущей дате
        tomorrow = current_date + timedelta(days=1, hours=9)
        self._scheduler.add_job(
            id='2_' + user_id,
            func=messages_with_objections,
            kwargs={'user_id': user_id, 'msg': message},
            trigger='date',
            run_date=tomorrow,
            max_instances=1,
        )

    async def remove_job(self, step, user_id):
        """step это всегда строковое значение с цифрой и нижним подчеркиванием. Цифра - номер шага, например '1_' """
        try:
            self._scheduler.remove_job(step + user_id)
        except JobLookupError:
            pass
