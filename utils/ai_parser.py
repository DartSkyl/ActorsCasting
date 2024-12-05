import hashlib

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
        actor_sex: str = Field(description='Требуемый пол актера, может быть явно не указано, но определить нужно')
        age_restrictions: str = Field(description='Возрастные ограничения')
        role_name: str = Field(description='Название роли или имя персонажа, которого предстоит сыграть')
        role_type: str = Field(default='Не указан', description='Тип роли (главная роль, второстепенная роль, массовка и т.д.')
        role_description: str = Field(description='Описание роли того, кого нужно сыграть')
        additional_requirements: str = Field(default='Не указан', description='Референс, описание сцен из фильма')
        fee: str = Field(default='Не указан', description='Гонорар, который актер получит за роль')

    project_name: str = Field(description='Название проекта')
    search_city: str = Field(default='Не указан', description='Город, где проходит кастинг')
    project_type: str = Field(description='Тип проекта, один из вариантов: полнометражный фильм, сериал, реклама, театр, '
                                          'некоммерческий проект')
    filming_dates: str = Field(description='Даты съемок')
    filming_location: str = Field(description='Место съемок')
    role_description: List[RoleDescription] = Field(description='описывает саму роль: пол, возраст, тип роли, описание '
                                                                'роли и т.д.')


class ConfigurationParsing(BaseModel):
    """Класс описания схемы конфигураций для актерских кастингов"""
    project_type: str = Field(default='Unspecified', description='Тип проекта. Реклама принимает значение "ads"; кино или фильм значение '
                                          '"films"; сериал значение "series";если театр или постановка значение '
                                          '"theater"; Некоммерческие проекты / фестивальные короткометражные фильмы'
                                          ' молодых режиссёров значение "free"')
    role_type: str = Field(default='Unspecified', description='Тип роли. Главные и второстепенные роли принимают значение "main_role";'
                                       'эпизодическая роль имеет значение "episode"; групповка и массовка имеют значение'
                                       '"mass"')
    actor_sex: str = Field(description='Пол актера или персонажа. Мужской пол значение "male"; женский пол значение '
                                       '"female"')
    age_restrictions: str = Field(description='Возрастные ограничения, просто две цифры через дефис(например "30-40")')


class ItCastingOrNot(BaseModel):
    """Описание ответа о том, кастинг это или нет"""
    it_casting: bool = Field(description='Если поступившее сообщение содержит информацию о кастинге тогда True, '
                                         'если нет тогда False')


# Промпт для парсинга информации о кастингах из сообщений
prompt_text = """Тебе будут скидывать сообщения в которых будет содержаться описание 
кастингов. Твоя задача достать от туда всю необходимую информацию, как указано в подсказке по форматированию 
{format_instructions}. Обязательно использовать абсолютно все информацию из сообщения! Требуемый пол актера часто явно 
не указывают, по этому нужно определить по описанию персонажа. Если указано например "ищем мужчин и женщин в возрасте 
20-30 лет", то воспринимай это как две отдельные роли: мужчина 20-30 лет и женщина 20-30 лет.
 Сообщение с кастингом: {input}"""
prompt = PromptTemplate.from_template(prompt_text)
parser = JsonOutputParser(pydantic_object=CastingForActors)

# Промпт для парсинга конфигураций из информации о кастингах
prompt_text_2 = """Тебе будет поступать информация о кастинга для актеров. Тебе нужно строго структурировать ее в 
в соответствии с подсказкой по форматированию {format_instructions}. Информация о кастинге: {input}"""
prompt_2 = PromptTemplate.from_template(prompt_text_2)
parser_2 = JsonOutputParser(pydantic_object=ConfigurationParsing)

# Промпт для проверки сообщения на тему кастинга
check_prompt_text = """Тебе будут приходить сообщения разного содержания. Твоя задача определить содержит ли сообщение 
информацию о кастинге для актеров или нет. Учти, что сообщение с кастингом может не содержать в себе само слово 
"кастинг". В место этого там могут встречаться такие фразы как "для съемок требуется", "рассматриваем актеров", 
"приглашаем актеров" и т.д. Т.е. ты обязательно должен учитывать контекст сообщения. От этого зависят жизни людей!
Отвечай как описано в подсказке по форматированию {format_instructions}.
Текст сообщения: {input}"""
check_prompt = PromptTemplate.from_template(check_prompt_text)
check_parser = JsonOutputParser(pydantic_object=ItCastingOrNot)

model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)


# В этом множестве будем хранить хэши отработанных сообщений, так как они могут повторяться
executed_hash = set()


async def get_casting_data(casting_msg: str):
    """Первая цепочка проверяет, содержит ли сообщение информацию о кастинге. Если содержит, то вторая достает ее и
    группирует, а третья формирует конфигурации по этому кастингу"""
    # Проверяем сообщение на наличие кастинга
    check_chain = check_prompt | model | check_parser
    check_response = await check_chain.ainvoke({'input': casting_msg,
                                                'format_instructions': check_parser.get_format_instructions()})
    if check_response['it_casting']:

        # Для учета уникальности кастингов будем использовать хэширование первых ста символов сообщения

        str_for_hashing = casting_msg[:100].encode()
        casting_hash = hashlib.sha256(str_for_hashing).hexdigest()
        if casting_hash not in executed_hash:
            # Сначала достаем всю информацию о кастинге из сообщения
            chain = prompt | model | parser
            casting_data = await chain.ainvoke({'input': casting_msg, 'format_instructions': parser.get_format_instructions()})
            casting_config = []
            # Из получившейся информации нужно сформировать сообщение для формирования конфигураций

            for role in casting_data['role_description']:
                input_text_for_prompt_2 = f'Тип проекта: {casting_data["project_type"]}\n'
                input_text_for_prompt_2 += (f'Тип роли: {role["role_type"]}\n'
                                            f'Пол актера: {role["actor_sex"]}\n'
                                            f'Возраст актера:{role["age_restrictions"]}')
                chain_2 = prompt_2 | model | parser_2
                casting_config.append(await chain_2.ainvoke({'input': input_text_for_prompt_2,
                                                             'format_instructions': parser_2.get_format_instructions()}))
                executed_hash.add(casting_hash)
                # Далее будем использовать обрезанную часть хэша
            return casting_data, casting_config, casting_hash[:10]
        else:
            return False
    else:
        with open('drop_messages.log', 'a') as log_file:
            log_file.write(f'\n=================================\n\n{casting_msg}\n=================================\n\n')
        return False
