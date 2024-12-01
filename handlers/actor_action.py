import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import base, techno_dict, dp
from utils.users_router import users_router
from states import ActorsState


@dp.message(F.forward_origin)
async def for_forward_message(msg: Message):
    """Дле перебрасывания сообщений, сам ты извращенец!"""
    if msg.from_user.id == techno_dict['parser_id']:
        user_for_drop = None
        for user in techno_dict['forwarding']:
            # У каждого элемента списка словарь с одним ключем и одним значением и что бы их извлечь делаем так:
            for user_id, user_request in user.items():
                user_request = [int(i) for i in user_request.split('_')]
                # Теперь проверяем, что бы переброшенное сообщение соответствовало запросу пользователя
                if msg.forward_origin.message_id == user_request[1] and msg.forward_origin.chat.id == user_request[0]:
                    await msg.forward(user_id)
                    user_for_drop = user
                    break
            break
        techno_dict['forwarding'].remove(user_for_drop)
    else:
        await msg.answer('Нельзя пересылать боту сообщения!')


@users_router.callback_query(F.data.startswith('origin_'))
async def get_origin_request(callback: CallbackQuery, state: FSMContext):
    """Ловим запрос от пользователя на получение оригинала сообщения"""
    await callback.answer()
    # Извлекаем ID чата и сообщения из callback и формируем из них список
    origin_message = [int(i) for i in callback.data.replace('origin_', '').split('_')]

    # Отправляем сообщения в личку бота
    await techno_dict['parser'].forward_origin_message(
        origin_chat=origin_message[0],
        origin_message=origin_message[1],
        user_id=callback.from_user.id
    )
    # Так как для этих двух функций используется словарь с одним ключом, но разным значением, то сделаем небольшую паузу
    await asyncio.sleep(0.5)

    # Если есть текст для проб, в виде файла, идущем следующем сообщением в чате-источнике, то пробросим и его
    await techno_dict['parser'].check_text_for_prob(
        origin_chat=origin_message[0],
        next_origin_message=(origin_message[1] + 1),
        user_id=callback.from_user.id
    )
