import psycopg2
import psycopg2.extras

from config import DB_CONFIG


class DatabaseError(Exception):
    """Ошибка работы с базой данных с понятным пользователю текстом."""


def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as error:
        raise DatabaseError(
            "Не удалось подключиться к базе данных.\n"
            "Проверьте, что сервер PostgreSQL запущен, а параметры подключения "
            "в файле config.py указаны верно."
        ) from error


def fetch_all(query, params=None):
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    except psycopg2.Error as error:
        raise DatabaseError(f"Ошибка при чтении данных из базы:\n{error}") from error
    finally:
        connection.close()


def fetch_one(query, params=None):
    rows = fetch_all(query, params)
    if rows:
        return rows[0]
    return None


def run_in_transaction(action):
    """Выполняет action(cursor) в одной транзакции: при любой ошибке все изменения откатываются."""
    connection = get_connection()
    try:
        with connection:
            with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                return action(cursor)
    except psycopg2.Error as error:
        raise DatabaseError(f"Ошибка при сохранении данных в базу:\n{error}") from error
    finally:
        connection.close()