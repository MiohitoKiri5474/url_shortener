from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import random, sqlite3, os, bcrypt

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

def create_random_url() -> str:
    res = ""
    lib = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    length = 8
    for i in range (8):
        res += lib[random.randint (0, len (lib))]
    return res

def hash_passwd (ori_passwd: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw (passwd.encode ('utf-8'), salt)

def verify_user (name: str, passwd: str) -> bool:
    try:
        result = bcrypt.checkpw (passwd.encode ('utf-8'), user_db.get_passwd (name))
        return result
    except ValueError as error:
        raise ValueError (str (error))

@app.get ('/')
async def read_root():
    return "Welcome to the URL shortener API"

@app.post ("/url")
async def create_url (url: URLAdminInfo):
    if url.admin_url == "":
        url.admin_url = create_random_url()
        while not url_db.check_admin_code_is_available (url.admin_url):
            url.admin_url = create_random_url()

    try:
        url_db.insert_url (url.admin_url, url.original_url)
        return url.admin_url + " -> " + url.original_url
    except ValueError as error:
        return str (error)

@app.get ("/r/{url}")
async def get_url (url: str):
    if url_db.check_admin_code_is_available (url):
        return "This admin url is not exist.\n"

    url_db.update_click_count (url)

    return RedirectResponse (url_db.query (url))

@app.get ("/list/")
async def list_url ():
    return url_db.list()

@app.delete ("/url_delete/{url}")
async def delete_url (url: str):
    try:
        url_db.delete (url)
        return url + " is successfully deleted.\n"
    except ValueError as error:
        return str (error)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run (app, host = '0.0.0.0', port = 8000)
