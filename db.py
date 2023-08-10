"""database relate"""
import os
import sqlite3

DB_PATH = "url_shortener.db"


def build_db():
    """create database if DB_PATH is not exist"""
    if os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS url_mapping (
        code TEXT PRIMARY KEY,
        url TEXT,
        username TEXT,
        clicks INTEGER DEFAULT 0
        )"""
    )
    conn.commit()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS user_mapping (
        name TEXT PRIMARY KEY,
        passwd BLOB,
        full_name TEXT DEFAULT Nont,
        email TEXT DEFAULT None,
        disable BOOL DEFAULT Fals
        )"""
    )
    conn.commit()
    conn.close()


def check_admin_code_is_available(admin_url: str):
    """check admin code is available of not before adding a new url shortenet into database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code FROM url_mapping WHERE code = ?", (admin_url,))
    result = cursor.fetchone()
    conn.close()

    return result is None


def insert_url(admin_url: str, ori: str, username: str):
    """add an url shortener into database"""
    if not check_admin_code_is_available(admin_url):
        raise ValueError(
            "The chosen short code is already taken. Please choose a different one."
        )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO url_mapping (code, url, username) VALUES (?, ?, ?)",
        (admin_url, ori, username),
    )
    conn.commit()
    conn.close()


def update_click_count(admin_url: str):
    """update click count after every redirect"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE url_mapping SET clicks = clicks + ? WHERE code = ?", (1, admin_url)
    )
    conn.commit()
    conn.close()


def query(url: str):
    """query original url by admin code from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM url_mapping WHERE code = ?", (url,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    return None


def delete_url(url: str, username: str):
    """delete url shortener by target user from database"""
    if check_admin_code_is_available(url):
        raise ValueError("This admin url is not exist.\n")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT url FROM url_mapping WHERE code = ? AND username = ?",
        (url, username),
    )
    result = cursor.fetchone()
    if result is None:
        raise ValueError("This admin url is not exist or is not created by this user.")
    cursor.execute(
        "DELETE FROM url_mapping WHERE code = ? AND username = ?", (url, username)
    )
    conn.commit()
    conn.close()


def list_url(username: str):
    """list out all url shortener create by target user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT code, url, clicks FROM url_mapping WHERE username = ?", (username,)
    )
    all_mappings = cursor.fetchall()
    cursor.close()

    return all_mappings


def check_username_is_available(name: str):
    """check username is available or not before add a new user into database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM user_mapping WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()

    return result is None


def insert_user(name: str, passwd, full_name: str, email: str):
    """add a new user information into database"""
    if not check_username_is_available(name):
        raise ValueError(
            "The chosen user name is alreadt taken, Please choose a different one."
        )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_mapping (name, passwd, full_name, email) VALUES (?, ?, ?, ?)",
        (name, passwd, full_name, email),
    )
    conn.commit()
    conn.close()


def update_user_status(name: str, disable: bool):
    """update user status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user_mapping SET disable = ? WHERE name = ?", (disable, name)
    )
    conn.commit()
    conn.close()


def get_passwd(name: str):
    """get hashed password of target user"""
    if check_username_is_available(name):
        raise ValueError("User not found.")

    try:
        result = get_user_info(name)[1]
        if result:
            return result
        raise ValueError("User information not found.")
    except ValueError as error:
        raise ValueError(str(error)) from error


def get_user_info(name: str):
    """get user information from database"""
    if check_username_is_available(name):
        raise ValueError("User not found.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, passwd, full_name, email, disable FROM user_mapping WHERE name = ?",
        (name,),
    )
    result = cursor.fetchall()
    conn.close()

    if result:
        return result[0]
    raise ValueError("User information not found.")
