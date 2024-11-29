import asyncpg as apg


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
        # Таблица со всеми пользователями
        async with self.pool.acquire() as connection:
            await connection.execute("CREATE TABLE IF NOT EXISTS all_actors"
                                     "(user_id BIGINT PRIMARY KEY,"
                                     "actor_name VARCHAR(155),"
                                     "passport_age INT,"
                                     "playing_age int4range,"
                                     "education VARCHAR(155),"
                                     "sex VARCHAR(155),"
                                     "contacts VARCHAR(155),"
                                     "agent_contact VARCHAR(155),"
                                     "have_experience TEXT,"
                                     "roles_type_interest TEXT,"
                                     "geo_location TEXT,"
                                     "portfolio TEXT,"
                                     "social TEXT);")

    async def registry_new_actor(self, user_id, actor_name, passport_age, playing_age, education, sex, contacts,
                                 agent_contact, have_experience, roles_type_interest, geo_location, portfolio, social):
        """Сохраняем нового актера в БД"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"INSERT INTO public.all_actors"
                                     f"(user_id, actor_name, passport_age, playing_age, education, sex, contacts,"
                                     f"agent_contact, have_experience, roles_type_interest, geo_location, portfolio,"
                                     f"social) VALUES ({user_id}, '{actor_name}', {passport_age}, "
                                     f"'[{playing_age[0]}, {playing_age[1]}]', '{education}', '{sex}', '{contacts}',"
                                     f"'{agent_contact}', '{have_experience}', '{roles_type_interest}', "
                                     f"'{geo_location}', '{portfolio}', '{social}')")

    async def get_users_id(self):
        """Достаем все имеющиеся ID что бы посмотреть, зарегистрирован пользователь или нет"""
        async with self.pool.acquire() as connection:
            result = await connection.fetch("SELECT user_id FROM public.all_actors")
            return [i['user_id'] for i in result]  # Так как из БД возвращается объект Record
