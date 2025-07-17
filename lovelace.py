#!/usr/bin/env python

import sqlite3 as sql

con = sql.connect("baka.db")
cur = con.cursor()

# TODO: Use strict mode
create_users_q = """
    CREATE TABLE IF NOT EXISTS users
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL CHECK (length(name) > 0 AND length(name) <= 20),
        age INTEGER CHECK (age >= 12 AND age <= 100) NOT NULL,
        city TEXT NOT NULL CHECK (length(name) > 0 AND length(name) <= 20),
        text TEXT NOT NULL CHECK (length(text) >= 30 AND length(text) <= 200),
        photo TEXT NOT NULL,
        tg_id INTEGER UNIQUE NOT NULL,
        active INTEGER NOT NULL CHECK (active in (0, 1)) DEFAULT 1,
        banned INTEGER NOT NULL CHECK (banned in (0, 1)) DEFAULT 0
    );
"""

insert_users_q = """
    INSERT INTO users (name, age, city, text, photo, tg_id) VALUES
    ('Алан', 36, 'Лондон', 'Разработка концепции универсальной машины Тьюринга', 'aaa', 1000000),
    ('Ноам', 56, 'Вашингтон', 'Вклад в развитие теории формальных языков и грамматик', 'aaa', 2000000),
    ('Чарльз', 42, 'Лондон', 'Создание механического исполнителя алгоритмов', 'aaa', 3000000)
    ON CONFLICT (tg_id) DO NOTHING;
"""

def get_users():
    """
    List all users of the bot
    """
    users = con.execute(f"SELECT * FROM users").fetchall()
    return users

def get_user(tg_id):
    """
    Get a concrete user
    """
    user = con.execute(f"SELECT * FROM users WHERE tg_id = ?", (tg_id,)).fetchone()
    return user

def create_user(name: str, age: int, city: str, text: str, photo: str, tg_id: str):
    """
    Create user
    """
    cur.execute("INSERT INTO users (name, age, city, text, photo, tg_id) VALUES (?, ?, ?, ?, ?, ?)", (name, age, city, text, photo, tg_id))
    con.commit()

def ban_user(id_: int):
    """
    Ban user
    """
    cur.execute("UPDATE users SET banned = 1 WHERE id = ?", (id_,))
    con.commit()

def delete_user(id_: int):
    cur.execute("DELETE FROM users WHERE id = ?", (id_,))
    con.commit()

def search(user_tg_id):
    """
    Main search algorithm
    TODO: Add a city filter based on radius
    TODO: Add interests filter
    """
    user_city = get_user(user_tg_id)[3]
    q = """
        SELECT name, age, city, text, photo FROM users
        WHERE tg_id != ? AND city = ? AND active = 1 AND banned = 0
        ORDER BY random() LIMIT 1
    """
    users = cur.execute(q, (user_tg_id, user_city)).fetchall()
    return users

# TODO: Make one method - toggle_activation
def deactivate_user(tg_id: int):
    """
    Deactivate user
    """
    cur.execute("UPDATE users SET active = 0 WHERE tg_id = ?", (tg_id,))
    con.commit()

def activate_user(tg_id: int):
    """
    Activate user
    """
    cur.execute("UPDATE users SET active = 1 WHERE tg_id = ?", (tg_id,))
    con.commit()

if __name__ == "__main__":
    cur.execute(create_users_q)
    cur.execute(insert_users_q)
    con.commit()
    con.close()
