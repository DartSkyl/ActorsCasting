from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from aiogram.types import Message
from keyboards.reply import pay_choice
from loader import techno_dict


async def send_message(msg: Message, user_id):
    """Отправляем пользователю сообщение с напоминанием о себе"""
    msg_text = ('В нашей базе на данный момент 184 канала с кастингами. И я моментально отслеживаю появление новых, '
                'поэтому можешь быть уверен, что ничего не пропустишь.\nК тому же, на нашей платформе '
                'кастинг-директора публикуют проекты, которых нет в открытом доступе. А это значит, что ты первый '
                'о них узнаешь.')
    await msg.answer(msg_text)
    await msg.answer('Выбери подходящий вариант нашего дальнейшего взаимодействия:',
                     reply_markup=pay_choice)
    await techno_dict['first_contact'].remove_job(user_id)


class FirstContact:
    """Класс для создания функции "первого контакта". Если после регистрации и выходе предложения об оплате
    пользователь бездействует, то через 2 минуты реагируем"""

    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._scheduler.start()

    async def wait_answer(self, user_id, message: Message):
        try:
            self._scheduler.remove_job(user_id)
        except JobLookupError:
            pass
        self._scheduler.add_job(
            id=user_id,
            func=send_message,
            kwargs={'user_id': user_id, 'msg': message},
            trigger='interval',
            seconds=120,
            max_instances=1,
        )

    async def remove_job(self, user_id):
        try:
            self._scheduler.remove_job(user_id)
        except JobLookupError:
            pass
