import sqlite3, os

user_db_path = "users.db"

def build_user_db():
    if os.path.exists (user_db_path):
        return

    conn = sqlite3.connect (user_db_path)
    cursor = conn.cursor()
    cursor.execute ('''CREATE TABLE IF NOT EXISTS user_mapping (name TEXT PRIMARY KEY, passwd TEXT, disable BOOL DEFAULT True)''')
    conn.commit()
    conn.close()

def check_username_is_available (name: str):
    conn = sqlite3.connect (user_db_path)
    cursor = conn.cursor()
    cursor.execute ('''SELECT name FROM user_mapping WHERE name = ?''', (name,))
    result = cursor.fetchone()
    conn.close()

    return result is None

def insert_user (name: str, passwd: str):
    if not check_username_is_available (name):
        raise ValueError ("The chosen user name is alreadt taken, Please choose a different one.")

    conn = sqlite3.connect (user_db_path)
    cursor = conn.cursor()
    cursor.execute ('''INSERT INTO user_mapping (name, passwd) VALUES (?, ?)''', (name, passwd))
    conn.commit()
    conn.close()

def update_user_status (name: str, disable: bool):
    conn = sqlite3.connect (user_db_path)
    cursor = conn.cursor()
    cursor.execute ('''UPDATE user_mapping SET disable = ? WHERE name = ?''', (disable, name))
    conn.commit()
    conn.close()

