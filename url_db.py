import sqlite3, os

url_db_path = "url_data.db"

def build_url_db():
    if os.path.exists (url_db_path):
        return
    conn = sqlite3.connect (url_db_path)
    cursor = conn.cursor()
    cursor.execute ('''CREATE TABLE IF NOT EXISTS url_mapping (code TEXT PRIMARY KEY, url TEXT, clicks INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def check_admin_code_is_available (admin_url: str):
    conn = sqlite3.connect (url_db_path)
    cursor = conn.cursor()
    cursor.execute ('''SELECT code FROM url_mapping WHERE code = ?''', (admin_url,))
    result = cursor.fetchone()
    conn.close()

    return result is None

def insert_url (admin_url: str, ori: str):
    if not check_admin_code_is_available (admin_url):
        raise ValueError ("The chosen short code is already taken. Please choose a different one.")

    conn = sqlite3.connect (url_db_path)
    cursor = conn.cursor()
    cursor.execute ('''INSERT INTO url_mapping (code, url) VALUES (?, ?)''', (admin_url, ori))
    conn.commit()
    conn.close()

def update_click_count (admin_url: str):
    conn = sqlite3.connect (url_db_path)
    cursor = conn.cursor()
    cursor.execute ('''UPDATE url_mapping SET clicks = clicks + ? WHERE code = ?''', (1, admin_url))
    conn.commit()
    conn.close()
