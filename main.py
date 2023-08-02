from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pydantic import BaseModel

from typing import Annotated, Union

import random, sqlite3, os, bcrypt

import url_db, user_db

class URLAdminInfo (BaseModel):
    original_url: str
    admin_url: str

class URLInfo (URLAdminInfo):
    clicks: int

class User (BaseModel):
    username: str
    passwd: bytes
    full_name: Union[str, None] = None
    email: Union[str, None] = None
    disable: Union[bool, None] = None

user_db.build_user_db()
url_db.build_url_db()
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer (tokenUrl = "token")

def raise_bad_request (message):
    raise HTTPException (status_code = 400, detail = message)

def create_random_url() -> str:
    res = ""
    lib = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    length = 8
    for i in range (8):
        res += lib[random.randint (0, len (lib))]
    return res

def hash_passwd (ori_passwd: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw (ori_passwd.encode ('utf-8'), salt)

def verify_user (name: str, passwd: str) -> bool:
    try:
        result = bcrypt.checkpw (passwd.encode ('utf-8'), user_db.get_passwd (name))
        return result
    except ValueError as error:
        raise ValueError (str (error))

def decode_token (token) -> User:
    user_info = user_db.get_user_info (token)
    return User (
            username = user_info[0],
            passwd = user_info[1],
            full_name = user_info[2],
            email = user_info[3],
            disable = user_info[4]
    )

async def get_current_user (token: str = Depends (oauth2_scheme)):
    user = decode_token (token)
    if not user:
        raise HTTPException (
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid authentication credentials",
                headers = {"WWW-Authenticate": "Bear"},
        )

    return user

async def get_current_active_user (current_user: User = Depends (get_current_user)):
    if current_user.disable:
        raise HTTPException (status_code = 400, detail = "Inactive user")
    return current_user

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

@app.get ('/items/')
async def read_item (current_user: User = Depends (get_current_user)):
    return current_user

@app.get ('/whoami/')
async def read_me (current_user: User = Depends (get_current_active_user)):
    return current_user

@app.post ('/token')
async def user_login (form_data: OAuth2PasswordRequestForm = Depends()):
    user_info = decode_token (form_data.username)

    if not user_info:
        raise HTTPEXception (status_code = 400, detail = "Incorrect username of password")

    if not verify_user (form_data.username, form_data.password):
        raise HTTPException (status_code = 400, detail = "Incorrect username or password")

    return {"access_token": user_info.username, "token_type": "bearer"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run (app, host = '0.0.0.0', port = 8000)
