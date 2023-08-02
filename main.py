from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Annotated, Union
from datetime import datetime, timedelta

import random, sqlite3, os, bcrypt

import url_db, user_db

SECRET_KEY = "7de99a859d0920dfb46628ab5af61dad0d618072863c2005e22cf06390639ca3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

class Token (BaseModel):
    access_token: str
    token_type: str

class TokenData (BaseModel):
    username: Union[str, None] = None

user_db.build_user_db()
url_db.build_url_db()
app = FastAPI()

pwd_context =  CryptContext (schemes = ["bcrypt"], deprecated = "auto")
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

def decode_token (token) -> User:
    user_info = user_db.get_user_info (token)
    return User (
            username = user_info[0],
            passwd = user_info[1],
            full_name = user_info[2],
            email = user_info[3],
            disable = user_info[4]
    )

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user (username: str, passwd: str):
    user_info = decode_token (username)
    if not user_info:
        return False
    if not verify_password (passwd, user_info.passwd):
        return False

    return user_info

async def get_current_user (token: str = Depends (oauth2_scheme)):
    credentials_exception = HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode (token, SECRET_KEY, algorithms = [ALGORITHM])
        username: str = payload.get ("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData (username = username)
    except JWTError:
        raise credentials_exception

    user_info = decode_token (token_data.username)
    if user_info is None:
        raise credentials_exceptino
    return user_info

async def get_current_active_user (current_user: User = Depends (get_current_user)):
    if current_user.disable:
        raise HTTPException (status_code = 400, detail = "Inactive user")
    return current_user

def create_access_token (data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta (minutes = 15)
    to_encode.update ({"exp": expire})
    encode_jwt = jwt.encode (to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encode_jwt

if user_db.check_username_is_available ('admin'):
    user_db.insert_user ('admin', get_password_hash ('admin'), 'Admin', 'admin@admin')
if user_db.check_username_is_available ('lltzpp'):
    user_db.insert_user ('lltzpp', get_password_hash ('alternate'), 'miohitokiri5474', 'lltzpp@gmail.com')

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

@app.get ('/whoami/', response_model = User)
async def read_me (current_user: User = Depends (get_current_active_user)):
    current_user.passwd = b"---"
    return current_user

@app.post ('/token')
async def user_login (form_data: OAuth2PasswordRequestForm = Depends()):
    user_info = authenticate_user (form_data.username, form_data.password)

    if not user_info:
        raise HTTPEXception (
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username of password",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta (minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token (
        data = {"sub": user_info.username},
        expires_delta = access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run (app, host = '0.0.0.0', port = 8000)
