from database.connection import fetch_all, fetch_one

USER_SELECT = """
    SELECT u.user_id, u.last_name, u.first_name, u.middle_name, u.login, u.role AS role_name
    FROM users u
"""


def find_user_by_login(login):
    return fetch_one(USER_SELECT + " WHERE u.login = %s", (login,))


def get_all_users():
    return fetch_all(USER_SELECT + " ORDER BY u.last_name, u.first_name")


def get_full_name(user):
    parts = [user["last_name"], user["first_name"], user["middle_name"]]
    return " ".join(part for part in parts if part)