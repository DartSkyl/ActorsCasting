from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from langchain_core.exceptions import OutputParserException

from loader import dp, techno_dict, bot
from utils.admin_router import admin_router
from utils.ai_parser import get_casting_data


@dp.message(F.forward_origin)
async def for_forward_message(msg: Message):
    """Дле перебрасывания сообщений, сам ты извращенец!"""
    if msg.from_user.id == techno_dict['parser_id']:
        print(msg.forward_origin)
        await msg.forward(6724839493)
        # await bot.forward_message(chat_id=6724839493,)


# @admin_router.message()
async def test_func(msg: Message):
    try:
        casting_data = await get_casting_data(msg.text)

        roles_info = 'Требуемые роли:\n\n'
        for role in casting_data['role_description']:
            roles_info += (f'Пол актера: {role["actor_sex"]}\n'
                           f'Возраст актера: {role["age_restrictions"]}\n'
                           f'Название роли: {role["role_name"]}\n'
                           f'Тип роли: {role["role_type"]}\n'
                           f'Описание роли: {role["role_description"]}\n'
                           f'Дополнительные требования: {role["additional_requirements"]}\n'
                           f'Гонорар: {role["fee"]}\n')
                           # f'Текст для пробы: {role["text_for_testing"]}\n\n')
        msg_text = (f'Новый кастинг!\n\nГород кастинга: {casting_data["search_city"]}\n'
                    f'Название проекта: {casting_data["project_name"]}\n'
                    f'Тип проекта: {casting_data["project_type"]}\n'
                    f'Дата съемок: {casting_data["filming_dates"]}\n'
                    f'Место съемок: {casting_data["filming_location"]}\n'
                    f'{roles_info}')
                    # f'Куда отправлять заявки: {casting_data["where_to_send_applications"]}\n'
                    # f'Правила оформления заявок: {casting_data["rules_for_submitting_an_application"]}\n')
        try:
            await msg.answer(msg_text)
        except TelegramBadRequest:
            await msg.answer(msg_text[:3000])
            await msg.answer(msg_text[3000:])
    except OutputParserException as e:
        print(e)
