import sqlite3
from setings import UserManagerSetting


class User:
    def __init__(self, username, password, consular_post, category_of_consular_act, consular_act, is_registred=False):
        self.username = username
        self.password = password
        self.consular_post = consular_post
        self.category_of_consular_act = category_of_consular_act
        self.consular_act = consular_act
        self.is_registred = is_registred


def get_connection():
    return sqlite3.connect(UserManagerSetting.database_name)


def initial_actions():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            consular_post TEXT,
            category_of_consular_act TEXT,
            consular_act TEXT,
            is_registred INTEGER DEFAULT 0
        )
        """)
        conn.commit()


# ---------------- CRUD ----------------

def add_user(user: User):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users 
            (username, password, consular_post, category_of_consular_act, consular_act, is_registred)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user.username,
            user.password,
            user.consular_post,
            user.category_of_consular_act,
            user.consular_act,
            int(user.is_registred)
        ))
        conn.commit()


def delete_user(username: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        return cur.rowcount > 0


def update_user(username: str, **kwargs):
    """
    update_user("kia", password="1234", is_registred=True)
    """
    if not kwargs:
        return False

    fields = []
    values = []

    for key, value in kwargs.items():
        fields.append(f"{key} = ?")
        values.append(int(value) if key == "is_registred" else value)

    values.append(username)

    query = f"UPDATE users SET {', '.join(fields)} WHERE username = ?"

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, tuple(values))
        conn.commit()
        return cur.rowcount > 0


def get_user(username: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cur.fetchone()


def get_all_users():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        return cur.fetchall()


initial_actions()
