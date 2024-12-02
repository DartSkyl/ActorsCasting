import asyncpg as apg
import datetime


class BotBase:
    """Через данный класс реализованы конект с базой данных и методы взаимодействия с БД"""

    def __init__(self, _db_user, _db_pass, _db_name, _db_host):
        self.db_name = _db_name
        self.db_user = _db_user
        self.db_pass = _db_pass
        self.db_host = _db_host
        self.pool = None

    async def connect(self):
        """Для использования БД будем использовать пул соединений.
        Иначе рискуем поймать asyncpg.exceptions._base.InterfaceError: cannot perform operation:
        another operation is in progress. А нам это не надо"""
        self.pool = await apg.create_pool(
            database=self.db_name,
            user=self.db_user,
            password=self.db_pass,
            host=self.db_host,
            max_inactive_connection_lifetime=10,
            min_size=1,
            max_size=100
        )

    async def check_db_structure(self) -> None:
        async with self.pool.acquire() as connection:
            # Таблица со всеми пользователями
            await connection.execute("CREATE TABLE IF NOT EXISTS all_actors"
                                     "(user_id BIGINT PRIMARY KEY,"
                                     "actor_name VARCHAR(155),"
                                     "passport_age INT,"
                                     "playing_age VARCHAR(155),"
                                     "education VARCHAR(155),"
                                     "sex VARCHAR(155),"
                                     "contacts VARCHAR(155),"
                                     "agent_contact VARCHAR(155),"
                                     "have_experience TEXT,"
                                     "projects_interest TEXT,"
                                     "roles_type_interest TEXT,"
                                     "geo_location TEXT,"
                                     "portfolio TEXT,"
                                     "social TEXT);")

            # Таблица со всеми кастингами
            await connection.execute("CREATE TABLE IF NOT EXISTS all_castings"
                                     "(casting_hash VARCHAR(155) PRIMARY KEY,"
                                     "time_added DATE,"
                                     "casting_data JSONB,"
                                     "casting_config JSONB);")

    # ====================
    # Операции с пользователями
    # ====================

    async def registry_new_actor(self, user_id, actor_name, passport_age, playing_age, education, sex, contacts,
                                 agent_contact, have_experience, roles_type_interest, geo_location, portfolio, social,
                                 projects_interest):
        """Сохраняем нового актера в БД"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"INSERT INTO public.all_actors"
                                     f"(user_id, actor_name, passport_age, playing_age, education, sex, contacts,"
                                     f"agent_contact, have_experience, roles_type_interest, geo_location, portfolio,"
                                     f"social, projects_interest) VALUES ({user_id}, '{actor_name}', {passport_age}, "
                                     f"'{playing_age}', '{education}', '{sex}', '{contacts}',"
                                     f"'{agent_contact}', '{have_experience}', '{roles_type_interest}', "
                                     f"'{geo_location}', '{portfolio}', '{social}', '{projects_interest}')")

    async def get_users_id(self):
        """Достаем все имеющиеся ID что бы посмотреть, зарегистрирован пользователь или нет"""
        async with self.pool.acquire() as connection:
            result = await connection.fetch("SELECT user_id FROM public.all_actors")
            return [i['user_id'] for i in result]  # Так как из БД возвращается объект Record

    async def get_all_actors(self):
        """Достаем всех актеров"""
        async with self.pool.acquire() as connection:
            result = await connection.fetch("SELECT * FROM public.all_actors")
            return result

    async def get_actor_info(self, user_id):
        """Достаем конкретного актера"""
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT * FROM public.all_actors WHERE user_id = {user_id}")
            return result

    async def setup_param(self, set_param, new_param_value, user_id):
        """Задаем новое значение для параметра"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.all_actors SET {set_param} = '{new_param_value}' "
                                     f"WHERE user_id = {user_id};")

    # ====================
    # Операции с кастингами
    # ====================

    async def add_new_casting(self, casting_hash, casting_data, casting_config):
        """Метод сохраняет новый кастинг в БД"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"INSERT INTO public.all_castings"
                                     f"(casting_hash, time_added, casting_data, casting_config)"
                                     f"VALUES ('{casting_hash}', '{datetime.date.today()}', "
                                     f"'{casting_data}','{casting_config}');")
