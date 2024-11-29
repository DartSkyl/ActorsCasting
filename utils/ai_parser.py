from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from config import OPENAI_API_KEY


model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ('system', 'Tell me about your self'),
    ('human', '{input}')
])

chain = prompt | model

response = chain.invoke({'input': 'Hi'})
print(response)
