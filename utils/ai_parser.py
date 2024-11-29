from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
from config import OPENAI_API_KEY


class CastingForActors(BaseModel):
    """Класс описывает структуру кастингов для актеров"""
    class RoleDescription(BaseModel):
        """Класс описывает саму роль: пол, возраст, тип роли, описание роли и т.д."""
        actor_sex: str = Field(description='Требуемый пол актера, определи по описываемому персонажу')
        age_restrictions: str = Field(description='Возрастные ограничения')
        role_name: str = Field(description='Название роли или имя персонажа, которого предстоит сыграть')
        role_type: str = Field(description='Тип роли (главная роль, второстепенная роль, массовка и т.д.')
        role_description: str = Field(description='Описание роли того, кого нужно сыграть')
        additional_requirements: str = Field(default='Не указан', description='Референс, описание сцен из фильма')
        fee: str = Field(default='Не указан', description='Гонорар, который актер получит за роль')
        text_for_testing: str = Field(default='Не указан',
                                      description='Текст для пробы (сам текст, либо ссылка на него)')

    project_name: str = Field(description='Название проекта')
    search_city: str = Field(default='Не указан', description='Город, где проходит кастинг')
    project_type: str = Field(description='Тип проекта (фильм, сериал, реклама, театр, некоммерческий проект и т.д.)')
    filming_dates: str = Field(description='Даты съемок')
    filming_location: str = Field(description='Место съемок')
    role_description: List[RoleDescription] = Field(description='описывает саму роль: пол, возраст, тип роли, описание '
                                                                'роли и т.д.')
    where_to_send_applications: str = Field(description='Ссылка, контакт или почта куда отправлять заявки и если есть, '
                                                        'то и тема письма')
    rules_for_submitting_an_application: str = Field(default='Не указан', description='Вся информация '
                                                                                      'касающаяся оформления заявки')


prompt_text = """Тебе будут скидывать сообщения в которых будет содержаться описание 
кастингов. Твоя задача достать от туда всю необходимую информацию, как указано в подсказке по форматированию 
{format_instructions}. Обязательно использовать абсолютно все информацию из сообщения! Сообщение с кастингом: {input}"""

prompt_text_2 = """"""

model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)
prompt = PromptTemplate.from_template(prompt_text)
parser = JsonOutputParser(pydantic_object=CastingForActors)


async def get_casting_data(casting_msg: str):
    """Цепочка с использованием JsonOutputParser"""
    chain = prompt | model | parser
    return await chain.ainvoke({'input': casting_msg, 'format_instructions': parser.get_format_instructions()})
