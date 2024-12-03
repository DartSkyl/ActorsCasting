import os
from dotenv import load_dotenv, find_dotenv
import logging

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('bot_token')
ADMINS = {int(i) for i in os.getenv('admins_id').split()}
MAIN_GROUP = int(os.getenv('main_group'))

DB_INFO = (
    os.getenv('db_user'),
    os.getenv('db_pass'),
    os.getenv('db_name'),
    os.getenv('db_host')
)

PG_URI = f'postgresql+psycopg2://{DB_INFO[0]}:{DB_INFO[1]}@{DB_INFO[3]}/{DB_INFO[2]}'

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

logging.basicConfig(
    filename='avito_ai.log',
    filemode='a',
    format="%(asctime)s %(levelname)s %(message)s"
)
logging.getLogger().setLevel(logging.ERROR)
