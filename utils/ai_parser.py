import hashlib
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
from config import OPENAI_API_KEY
from loader import base


class ProjectInfo(BaseModel):
    """Класс описывает информацию о проекте"""
    project_name: str = Field(description='Название проекта')
    project_type: str = Field(default='Не указано', description='Тип проекта, один из вариантов: полнометражный фильм, сериал, реклама,'
                                          'некоммерческий проект')
    filming_dates: str = Field(description='Даты съемок.')


class CastingForActors(BaseModel):
    """Класс описывает структуру кастингов для актеров"""

    class RoleDescription(BaseModel):
        """Класс описывает саму роль: пол, возраст, тип роли, описание роли и т.д."""
        actor_sex: str = Field(description='Требуемый пол актера, может быть явно не указано, но определить нужно')
        age_restrictions: str = Field(description='Возрастные ограничения')
        role_name: str = Field(description='Название роли или имя персонажа, которого предстоит сыграть')
        role_description: str = Field(description='Описание роли того, кого нужно сыграть')
        additional_requirements: str = Field(default='Не указан', description='Референс, описание сцен из фильма')
        fee: str = Field(default='0', description='Гонорар, который актер получит за роль. В тексте может '
                                                  'быть обозначена "ставка", эмодзи 💰 или что то подобное. '
                                                  'Если ничего не указано, то просто 0')

    # project_name: str = Field(description='Название проекта')
    # project_type: str = Field(description='Тип проекта, один из вариантов: полнометражный фильм, сериал, реклама,'
    #                                       'некоммерческий проект')
    # filming_dates: str = Field(description='Даты съемок.')
    role_description: List[RoleDescription] = Field(description='описывает саму роль: пол, возраст, тип роли, описание '
                                                                'роли и т.д.')


class ConfigurationParsing(BaseModel):
    """Класс описания схемы конфигураций для актерских кастингов"""
    project_type: str = Field(default='Unspecified',
                              description='Тип проекта. Реклама принимает значение "ads"; кино, фильмы имеют'
                                          'значение "films", сериалы тоже имеют значение "films"; '
                                          'Некоммерческие проекты / фестивальные короткометражные '
                                          'фильмы молодых режиссёров значение "free"')

    actor_sex: str = Field(description='Пол актера или персонажа. Мужской пол значение "male"; женский пол значение '
                                       '"female"')

    age_restrictions: str = Field(description='Возрастные ограничения, просто две цифры через дефис(например "30-40")')
    fee: int = Field(default=0, description='Гонорар за роль. В сообщении указан диапазон, '
                                            'то нужна нижняя граница')


class ContactsParsing(BaseModel):
    """Класс для извлечения контактов и правил оформления заявок для кастингов"""
    contacts: str = Field(default='комментарии',
                          description='Контакты, которые оставил автор кастинга для приема заявок. '
                                      'Это может быть номер телефона, контакт в мессенджере, email, '
                                      'ссылка на сторонний ресурс. Если контактных данных нет или '
                                      'написано "заявки оставлять в комментариях" или что то '
                                      'подобное, значение должно быть "комментарии".')
    # title: str = Field(default='неуказан', description='Для электронных писем часто указывают что написать в '
    #                                                    'заголовке или теме письма')
    rules: str = Field(default='Отсутствуют', description='Правила оформления заявок. Это может быть список того, что '
                                                          'необходимо указать в заявке: заголовок или тема письма,'
                                                          'перечень пунктов, которые необходимо заполнить и что в них '
                                                          'должно быть заполнено.')


class AdvertisingRights(BaseModel):
    """Класс для извлечения информации о правах на рекламу из сообщения о кастинге"""
    rights: str = Field(description='Описание прав. Там пишется срок и где будет размещено')


class ItCastingOrNot(BaseModel):
    """Описание ответа о том, кастинг это или нет"""
    it_casting: bool = Field(description='Если поступившее сообщение содержит информацию о кастинге тогда True, '
                                         'если нет тогда False')


class ProbeText(BaseModel):
    """Описание ответа с текстом для самопроб"""
    text: str = Field(default='Отсутствует', description='Текст для самопроб для актеров. Содержит описание сцены и диалог '
                                                         'или монолог. Если и есть, то только после фразы "текст для самопроб" '
                                                         'или похожей по смыслу фразы.')


# Промпт для извлечения информации о проекте
project_prompt_text = """Тебе будут приходить сообщения с кастингами для актеров. Твоя задача извлечь оттуда информацию о
проекте: название проекта, тип проекта, дата съемок. Отвечай в формате JSON, как описано в подсказке по форматированию 
{format_instructions}. Текст сообщения: {input}"""
project_prompt = PromptTemplate.from_template(project_prompt_text)
project_parser = JsonOutputParser(pydantic_object=ProjectInfo)

# Промпт для парсинга информации о кастингах из сообщений
prompt_text = """Тебе будут скидывать сообщения в которых будет содержаться описание 
кастингов. Твоя задача достать от туда всю необходимую информацию, как указано в подсказке по форматированию 
{format_instructions}. Обязательно использовать абсолютно все информацию из сообщения! Требуемый пол актера часто явно 
не указывают, по этому нужно определить по описанию персонажа. Если указано например "ищем мужчин и женщин в возрасте 
20-30 лет", то воспринимай это как две отдельные роли: мужчина 20-30 лет и женщина 20-30 лет, "мальчики и девочки" это
тоже две отдельные роли мужского и женского пола.
Сообщение с кастингом: {input}"""
prompt_text_ = """
Извлеки из сообщения о кастинге следующую информацию:
- пол актёра (если он не указан явно, определи его по тексту);
- возраст актёра или возрастной диапазон (если возраст не указан, поставь прочерк);
- описание роли;
- дополнительные требования к актёрам (если они есть);
- гонорар за роль.
Если указано например "ищем мужчин и женщин в возрасте 
20-30 лет", то разбей их на две отдельные роли: мужчина 20-30 лет и женщина 20-30 лет, "мальчики и девочки" это
тоже две отдельные роли мужского и женского пола. Учтите, что гонорар иногда может быть указан один на всех.
Тебе нужно строго структурировать ее в соответствии с подсказкой по форматированию {format_instructions}.
Текст сообщения: {input}
"""
prompt = PromptTemplate.from_template(prompt_text_)
parser = JsonOutputParser(pydantic_object=CastingForActors)

# Промпт для парсинга конфигураций из информации о кастингах
prompt_text_2 = """Тебе будет поступать информация о кастинга для актеров. Тебе нужно строго структурировать ее в 
в соответствии с подсказкой по форматированию {format_instructions}. Информация о кастинге: {input}"""
prompt_2 = PromptTemplate.from_template(prompt_text_2)
parser_2 = JsonOutputParser(pydantic_object=ConfigurationParsing)

# Промпт для извлечения контактных данных и правил оформления заявок для кастингов
prompt_text_3 = """Тебе будет поступать информация о кастинга для актеров. Тебе нужно будет извлечь контактные данные,
куда актеры должны отправлять заявки, если они там есть. Обычно они указываются в виде номера телефона, email, контакты
в мессенджерах или ссылки на сторонний ресурс. Так же, в сообщение еще могут быть указаны правила оформления заявок и
если они там есть, то их тоже нужно извлечь. Обычно, правила оформления заявок пишут после контактной информации,
обязательно учти это, это очень важно. Если указан email, то часто указываю что нужно написать в теме письма.
Всю информацию извлекать ровно в том виде, в котором она указана в сообщении. Тебе нужно строго структурировать ее в 
соответствии с подсказкой по форматированию {format_instructions}. Информация о кастинге: {input}"""
prompt_3 = PromptTemplate.from_template(prompt_text_3)
parser_3 = JsonOutputParser(pydantic_object=ContactsParsing)

# Промпт для проверки сообщения на тему кастинга
check_prompt_text = """Твоя задача определить содержит ли сообщение 
информацию о кастинге для актеров или нет. Учти, что сообщение с кастингом может не содержать в себе само слово 
"кастинг". Т.е. контекст сообщения должен описывать участие в 
съемках кино, сериалов, рекламы, некоммерческих проектов. Если сообщение содержит слово "кастинг" в качестве простого 
упоминания "о каком то там кастинге" и не содержит фактической информации и ролях и проекте, для которого проводят 
кастинг, то игнорируй это сообщение. ОБЯЗАТЕЛЬНО обращая внимание на содержание сообщения: если это похоже на кастинг -
значит кастинг, если не похоже значит нет. Если в сообщении упоминается гонорар, то скорее всего это кастинг
Отвечай как описано в подсказке по форматированию {format_instructions}.
Текст сообщения: {input}"""
check_prompt = PromptTemplate.from_template(check_prompt_text)
check_parser = JsonOutputParser(pydantic_object=ItCastingOrNot)

# Промпт для извлечения информации о правах из кастинга
rights_prompt_text = """Тебе будут приходить сообщения с информацией о кастингах для актеров для съемок рекламы.
Твоя задача извлечь из этих сообщений информацию о правах. Там пишется срок, например 2 года, и где будет размещено, 
к примеру тв и соц сети. Вот несколько примеров такой информации:
----
ПРАВА:
 3 месяца с 13.12.2024, Digital, РФ, интернет (весь мир)
- 1 день для способов: сообщение в эфир, сообщение по кабелю, прокат, запись, импорт, публичное исполнение/показ.

ПРАВА ПО АКТЁРАМ, КОТОРЫЕ В ВИДЕО, и которые снимаются 25 ноября:
ВИДЕО - 2 года, ТВ РФ, Интернет, места продаж и обслуживания клиентов + архивное хранение в соц сетях.
----
Отвечай как описано в подсказке по форматированию {format_instructions}. Информация о кастинге: {input}
"""
rights_prompt = PromptTemplate.from_template(rights_prompt_text)
rights_parser = JsonOutputParser(pydantic_object=AdvertisingRights)

# Промпт для проверки на наличие текста для самопроб
prob_prompt_text = """Извлекайте только текст, который явно маркирован или отмечен как текст для самопробы. 
Игнорируйте все описания ролей и другие информационные блоки. Фокусируйтесь исключительно на тексте, который может 
быть использован актерами для прохождения самопроб. Если такого текста в сообщении нет, то просто скажи "Отсутствует"
Отвечай как описано в подсказке по форматированию 
{format_instructions}. Сообщение с кастингом: {input}"""
prob_prompt = PromptTemplate.from_template(prob_prompt_text)
prob_parser = JsonOutputParser(pydantic_object=ProbeText)

model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)


async def extract_json_from_string(input_string):
    try:
        input_string = input_string.replace('For troubleshooting, visit: https://python.langchain.com/docs/troubleshooting/errors/OUTPUT_PARSING_FAILURE', '')
        input_string = input_string.replace('Invalid json output:', '')
        input_string = input_string.replace(',\n}', '}').replace('\n', '')
        json_data = json.loads(input_string)
        return json_data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


async def uniqueness_check(cast_text):
    """Проверка на уникальность будет производиться через индекс Жаккара"""
    async def jaccard(x: set, y: set):
        shared = x.intersection(y)  # выбираем пересекающиеся токены
        return len(shared) / len(x.union(y))

    #  Получаем последние 200 текстов
    last_200_castings = await base.get_all_texts()
    for t in last_200_castings:
        first = set(t['casting_text'].split())
        second = set(cast_text.split())
        uniq = await jaccard(first, second)
        if uniq > 0.8:
            return False
    return True


async def get_casting_data(casting_msg: str):
    """Первая цепочка проверяет, содержит ли сообщение информацию о кастинге. Если содержит, то вторая достает ее и
    группирует, а третья формирует конфигурации по этому кастингу, четвертая достает информацию по контактам и правилам
    оформления заявок, пятая достает права из кастингов для рекламы. Каждый этап взаимодействия с ИИ обернут в
    бесконечный цикл While True, а внутри try except. Сделано это потому, что очень часто вылазит ошибка output parser
    error на ровном месте"""
    # Проверяем сообщение на наличие кастинга
    while True:  # Так как ошибка output parser очень любит вылазить на ровном месте
        try:
            check_chain = check_prompt | model | check_parser
            check_response = await check_chain.ainvoke({'input': casting_msg,
                                                        'format_instructions': check_parser.get_format_instructions()})
            break
        except Exception as e:
            print(e)
    if check_response['it_casting']:

        # А это для создания ID
        str_for_hashing = casting_msg[:100].encode()
        casting_hash = hashlib.sha256(str_for_hashing).hexdigest()
        if await uniqueness_check(casting_msg):  # Для учета уникальности кастингов будем использовать индекс Жаккара
            while True:  # Иногда вылазит ошибка KeyError: 'fee', а это нам нельзя
                try:
                    # Сначала достаем всю информацию о кастинге из сообщения, разобьем в два этапа,
                    # что бы уменьшить вероятность ошибки
                    while True:  # Так как ошибка output parser очень любит вылазить на ровном месте
                        try:
                            project_chain = project_prompt | model | project_parser
                            casting_data_1 = await project_chain.ainvoke({'input': casting_msg,
                                                                'format_instructions': project_parser.get_format_instructions()}
                                                                         )
                            break
                        except Exception as e:
                            # Ингода, ошибка вылазит из лишней запитой в конце.
                            # С помощью следующей функции попробуем сократить последствия данной ошибки
                            casting_data_1 = await extract_json_from_string(str(e))
                            if casting_data_1:
                                break
                            print(e)
                    while True:  # Так как ошибка output parser очень любит вылазить на ровном месте
                        try:
                            chain = prompt | model | parser
                            casting_data = await chain.ainvoke({'input': casting_msg,
                                                                'format_instructions': parser.get_format_instructions()})
                            break
                        except Exception as e:
                            # Ингода, ошибка вылазит из лишней запитой в конце.
                            # С помощью следующей функции попробуем сократить последствия данной ошибки
                            casting_data = await extract_json_from_string(str(e))
                            if casting_data:
                                break
                            print(e)
                    casting_config = []
                    casting_data.update(casting_data_1)
                    # Из получившейся информации нужно сформировать сообщение для формирования конфигураций
                    for role in casting_data['role_description']:
                        input_text_for_prompt_2 = f'Тип проекта: {casting_data["project_type"]}\n'
                        input_text_for_prompt_2 += (f'Пол актера: {role["actor_sex"]}\n'
                                                    f'Возраст актера:{role["age_restrictions"]}\n'
                                                    f'Гонорар: {role["fee"]}')
                        while True:  # Так как ошибка output parser очень любит вылазить на ровном месте
                            try:
                                chain_2 = prompt_2 | model | parser_2
                                casting_config.append(await chain_2.ainvoke({'input': input_text_for_prompt_2,
                                                                             'format_instructions': parser_2.get_format_instructions()}))
                                break
                            except Exception as e:
                                print(e)
                    break
                except KeyError as e:
                    print(e)
            while True:  # Так как ошибка output parser очень любит вылазить на ровном месте
                try:
                    chain_3 = prompt_3 | model | parser_3
                    casting_contacts = await chain_3.ainvoke({'input': casting_msg,
                                                              'format_instructions': parser_3.get_format_instructions()})
                    break
                except Exception as e:
                    # Ингода, ошибка вылазит из лишней запитой в конце.
                    # С помощью следующей функции попробуем сократить последствия данной ошибки
                    casting_contacts = await extract_json_from_string(str(e))
                    if casting_contacts:
                        break
                    print(e)

            while True:  # Так как ошибка output parser очень любит вылазить на ровном месте
                try:
                    probe_chain = prob_prompt | model | prob_parser
                    casting_prob = await probe_chain.ainvoke({'input': casting_msg,
                                                              'format_instructions': prob_parser.get_format_instructions()})
                    break
                except Exception as e:
                    # Ингода, ошибка вылазит из лишней запитой в конце.
                    # С помощью следующей функции попробуем сократить последствия данной ошибки
                    casting_prob = await extract_json_from_string(str(e))
                    if casting_prob:
                        break
                    print(e)

            casting_rights = None
            # Если это реклама, то извлечем информацию о правах
            if casting_config[0]['project_type'] == 'ads':
                while True:  # Так как ошибка output parser очень любит вылазить на ровном месте
                    try:
                        rights_chain = rights_prompt | model | rights_parser
                        casting_rights = await rights_chain.ainvoke({'input': casting_msg,
                                                                     'format_instructions': rights_parser.get_format_instructions()})
                        break
                    except Exception as e:
                        # Ингода, ошибка вылазит из лишней запитой в конце.
                        # С помощью следующей функции попробуем сократить последствия данной ошибки
                        casting_rights = await extract_json_from_string(str(e))
                        if casting_rights:
                            break
                        print(e)
            await base.add_new_text(casting_msg)
            # Далее будем использовать обрезанную часть хэша
            return casting_data, casting_config, casting_contacts, casting_rights, casting_prob, casting_hash[:10]
        else:
            return False
    else:
        with open('drop.log', 'a', encoding='utf-8') as file:
            file.write(
                f'\n==================\n{casting_msg}\n==================\n\n')
        return False
