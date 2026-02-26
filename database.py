import sqlite3
import time
import os

DB_NAME = os.getenv ('DB_PATH', 'data/work.db')

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )""")
        conn.commit()

def table_tokens():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS reset_tokens (
            token TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            exp INTEGER NOT NULL,
            used BOOLEAN NOT NULL
        )""")
        conn.commit()

def add_user_to_db(email, password):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO users (email, password) VALUES (?, ?)""", (email, password))
        conn.commit()

def get_user_by_email(email):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(""" SELECT * FROM users WHERE email = ?""", (email,))
        return cursor.fetchone() is not None
    
def update_user_password(email, password):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE users SET password = ? WHERE email = ?""", (password, email))
        conn.commit()

def set_as_used_token(token):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE reset_tokens SET used = 1 WHERE token = ?""", (token,))
        conn.commit()

def del_old_tokens(email):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM reset_tokens WHERE email = ? AND used = 0""", (email,))
        conn.commit()

def create_reset_token(email, token, exp):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        del_old_tokens(email)
        cursor.execute("""INSERT INTO reset_tokens (token, email, exp, used) VALUES (?, ?, ?, ?)""", (token, email, exp, False))

        conn.commit()

def get_reset_token(token):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT email, exp FROM reset_tokens WHERE token = ? AND used = 0""", (token,))
        row = cursor.fetchone()
        if row is None:
            return None
        
        email, exp = row

        if exp < time.time():
            return None
        
        return email

