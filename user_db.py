import sqlite3, os

user_db_path = "users.db"

def build_user_db():
    if os.path.exists (user_db_path):
        return

    conn = sqlite3.connect (user_db_path)
    cursor = conn.cursor()
    cursor.execute ('''CREATE TABLE IF NOT EXISTS user_mapping (name TEXT PRIMARY KEY, passwd BLOB, full_name TEXT DEFAULT Nont, email TEXT DEFAULT None, disable BOOL DEFAULT False)''')
    conn.commit()
    conn.close()

def check_username_is_available (name: str):
    conn = sqlite3.connect (user_db_path)
    cursor = conn.cursor()
    cursor.execute ('''SELECT name FROM user_mapping WHERE name = ?''', (name,))
    result = cursor.fetchone()
    conn.close()

    return result is None

def insert_user (name: str, passwd, full_name: str, email: str):
    if not check_username_is_available (name):
        raise ValueError ("The chosen user name is alreadt taken, Please choose a different one.")

    conn = sqlite3.connect (user_db_path)
    cursor = conn.cursor()
    cursor.execute ('''INSERT INTO user_mapping (name, passwd, full_name, email) VALUES (?, ?, ?, ?)''', (name, passwd, full_name, email))
    conn.commit()
    conn.close()

def update_user_status (name: str, disable: bool):
    conn = sqlite3.connect (user_db_path)
    cursor = conn.cursor()
    cursor.execute ('''UPDATE user_mapping SET disable = ? WHERE name = ?''', (disable, name))
    conn.commit()
    conn.close()

def get_passwd (name: str):
    if check_username_is_available (name):
        raise ValueError ("User not found.")

    try:
        result = get_user_info (name)[1]
        if result:
            return result
        raise ValueError ("User information not found.")
    except ValueError as error:
        raise ValueError (str(error))

def get_user_info (name: str):
    if check_username_is_available (name):
        raise ValueError ("User not found.")

    conn = sqlite3.connect (user_db_path)
    cursor = conn.cursor()
    cursor.execute ('''SELECT name, passwd, full_name, email, disable FROM user_mapping WHERE name = ?''', (name,))
    result = cursor.fetchall()
    conn.close()

    if result:
        return result[0]
    raise ValueError ("User information not found.")
