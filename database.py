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
                                     "fee INT,"
                                     "geo_location TEXT,"
                                     "portfolio TEXT,"
                                     "social TEXT,"
                                     "favorites TEXT);")

            # Таблица со всеми кастингами
            await connection.execute("CREATE TABLE IF NOT EXISTS all_castings"
                                     "(casting_hash VARCHAR(155) PRIMARY KEY,"
                                     "time_added DATE,"
                                     "casting_data TEXT,"
                                     "casting_config TEXT,"
                                     "casting_origin TEXT,"
                                     "origin_for_user TEXT);")

            # Таблица с текстами кастингов для проверки на уникальность
            await connection.execute("CREATE TABLE IF NOT EXISTS all_castings_texts"
                                     "(id SERIAL PRIMARY KEY,"
                                     "casting_text TEXT);")

            # Таблица с подписками для "своих"
            await connection.execute("CREATE TABLE IF NOT EXISTS subscription"
                                     "(user_id BIGINT PRIMARY KEY);")

    # ====================
    # Операции с пользователями
    # ====================

    async def registry_new_actor(self, user_id, actor_name, passport_age, playing_age, education, sex,
                                 have_experience, fee, portfolio, social,
                                 projects_interest):
        """Сохраняем нового актера в БД"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"INSERT INTO public.all_actors"
                                     f"(user_id, actor_name, passport_age, playing_age, education, sex,"
                                     f"have_experience, fee, portfolio,"
                                     f"social, projects_interest) VALUES ({user_id}, '{actor_name}', {passport_age}, "
                                     f"'{playing_age}', '{education}', '{sex}', "
                                     f"'{have_experience}', {fee}, "
                                     f"'{portfolio}', '{social}', '{projects_interest}')")

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

    async def get_actor_favorites(self, user_id):
        """Достаем из базы избранное актера"""
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT favorites FROM public.all_actors WHERE user_id = {user_id}")
            return result

    async def set_actor_favorites(self, user_id, new_favorites):
        """Добавляем обновленные кастинги в избранном"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.all_actors SET favorites = '{new_favorites}' "
                                     f"WHERE user_id = {user_id};")

    async def delete_user(self, user_id):
        """Удаление пользователя из базы"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"DELETE FROM public.all_actors WHERE user_id = {user_id};")

    # ====================
    # Операции с кастингами
    # ====================

    async def add_new_casting(self, casting_hash, casting_data, casting_config, casting_origin, origin_for_user):
        """Метод сохраняет новый кастинг в БД"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"INSERT INTO public.all_castings"
                                     f"(casting_hash, time_added, casting_data, casting_config, casting_origin, origin_for_user)"
                                     f"VALUES ('{casting_hash}', '{datetime.date.today()}', "
                                     f"'{casting_data}','{casting_config}', '{casting_origin}', '{origin_for_user}');")

    async def get_casting(self, casting_hash):
        """Достаем кастинг из базы"""
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT * "
                                            f"FROM public.all_castings WHERE casting_hash = '{casting_hash}'")
            return result

    async def get_statistic_data(self, first_date: str, second_date: str):
        """Метод возвращает выборку по заданным датам"""
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT * FROM public.all_castings WHERE time_added "
                                            f"BETWEEN '{first_date}' AND '{second_date}'")
            return result

    async def get_statistic_for_all_period(self):
        """Метод возвращает статистику канала за весь период"""
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT * FROM public.all_castings")
            return result

    async def get_today_statistic(self, date_today: str):
        """Метод возвращает статистику за текущий день"""
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT * FROM public.all_castings "
                                            f"WHERE time_added = '{date_today}'")
            return result

    async def remove_casting(self, casting_hash):
        """Удаляем кастинг из базы"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"DELETE FROM public.all_castings WHERE casting_hash = '{casting_hash}';")

    # ====================
    # Операции с текстами кастингов
    # ====================

    async def add_new_text(self, casting_text):
        """Добавляем новый текст в базу"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"INSERT INTO public.all_castings_texts (casting_text) VALUES ('{casting_text}');")

    async def get_all_texts(self):
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT casting_text FROM public.all_castings_texts ORDER BY id DESC LIMIT 200;")
            return result

    async def get_all_texts_2(self):
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT casting_text FROM public.all_castings_texts;")
            return result

    # ====================
    # Операции с подписками для "своих"
    # ====================

    async def add_sub(self, user_id):
        async with self.pool.acquire() as connection:
            await connection.execute(f"INSERT INTO public.subscription (user_id) VALUES ({user_id});")

    async def del_sub(self, user_id):
        async with self.pool.acquire() as connection:
            await connection.execute(f"DELETE FROM public.subscription WHERE user_id = {user_id};")

    async def get_all_sub(self):
        async with self.pool.acquire() as connection:
            result = await connection.fetch(f"SELECT * FROM public.subscription;")
            return [i['user_id'] for i in result]
