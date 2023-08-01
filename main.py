from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

import random, sqlite3, os

class URLAdminInfo (BaseModel):
    original_url: str
    admin_url: str

class URLInfo (URLAdminInfo):
    clicks: int

db_path = "url_data.db"

def build_db():
    if os.path.exists (db_path):
        return
    conn = sqlite3.connect (db_path)
    cursor = conn.cursor()
    cursor.execute ('''CREATE TABLE IF NOT EXISTS url_mapping (code TEXT PRIMARY KEY, url TEXT, clicks INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def check_admin_code_is_available (admin_url: str):
    conn = sqlite3.connect (db_path)
    cursor = conn.cursor()
    cursor.execute ('''SELECT code FROM url_mapping WHERE code = ?''', (admin_url,))
    result = cursor.fetchone()
    conn.close()

    return result is None

def insert_url (admin_url: str, ori: str):
    if not check_admin_code_is_available (admin_url):
        raise ValueError ("The chosen short code is already taken. Please choose a different one.")

    conn = sqlite3.connect (db_path)
    cursor = conn.cursor()
    cursor.execute ('''INSERT INTO url_mapping (code, url) VALUES (?, ?)''', (admin_url, ori))
    conn.commit()
    conn.close()

def update_click_count (admin_url: str):
    conn = sqlite3.connect (db_path)
    cursor = conn.cursor()
    cursor.execute ('''UPDATE url_mapping SET clicks = clicks + ? WHERE code = ?''', (1, admin_url))
    conn.commit()
    conn.close()

build_db()
app = FastAPI()

def raise_bad_request (message):
    raise HTTPException (status_code = 400, detail = message)

def query (url: str):
    conn = sqlite3.connect (db_path)
    cursor = conn.cursor()
    cursor.execute ('''SELECT url FROM url_mapping WHERE code = ?''', (url,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    return None

def create_random_url() -> str:
    res = ""
    lib = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    length = 8
    for i in range (8):
        res += lib[random.randint (0, len (lib))]
    return res

@app.get ('/')
async def read_root():
    return "Welcome to the URL shortener API"

@app.post ("/url")
async def create_url (url: URLAdminInfo):
    if url.admin_url == "":
        url.admin_url = create_random_url()

    try:
        insert_url (url.admin_url, url.original_url)
        return url.admin_url + " -> " + url.original_url
    except ValueError as error:
        return str (error)

@app.get ("/r/{url}")
async def get_url (url: str):
    if check_admin_code_is_available (url):
        return "This admin url is not exist.\n"

    update_click_count (url)

    return RedirectResponse (query (url))

@app.get ("/list/")
async def list_url ():
    conn = sqlite3.connect (db_path)
    cursor = conn.cursor()
    cursor.execute ('''SELECT code, url, clicks FROM url_mapping''')
    all_mappings = cursor.fetchall()
    cursor.close()

    return all_mappings

@app.delete ("/url_delete/{url}")
async def delete_url (url: str):
    if check_admin_code_is_available (url):
        return "This admin url is not exist.\n"

    conn = sqlite3.connect (db_path)
    cursor = conn.cursor()
    cursor.execute ('''DELETE FROM url_mapping WHERE code = ?''', (url,))
    conn.commit()
    conn.close()

    return url + " is successfully deleted.\n"
