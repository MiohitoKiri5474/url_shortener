from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import random, sqlite3, os

import url_db, user_db

class URLAdminInfo (BaseModel):
    original_url: str
    admin_url: str

class URLInfo (URLAdminInfo):
    clicks: int

user_db.build_user_db()
url_db.build_url_db()
app = FastAPI()

def raise_bad_request (message):
    raise HTTPException (status_code = 400, detail = message)

def query (url: str):
    conn = sqlite3.connect (url_db.url_db_path)
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
    conn = sqlite3.connect (url_db.url_db_path)
    cursor = conn.cursor()
    cursor.execute ('''SELECT code, url, clicks FROM url_mapping''')
    all_mappings = cursor.fetchall()
    cursor.close()

    return all_mappings

@app.delete ("/url_delete/{url}")
async def delete_url (url: str):
    if check_admin_code_is_available (url):
        return "This admin url is not exist.\n"

    conn = sqlite3.connect (url_db.url_db_path)
    cursor = conn.cursor()
    cursor.execute ('''DELETE FROM url_mapping WHERE code = ?''', (url,))
    conn.commit()
    conn.close()

    return url + " is successfully deleted.\n"
