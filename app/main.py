"""
This is the main file for this project, url shortener.
It is power by FastAPI, jose, pydantic, passlib.
"""
import random
from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app import db

SECRET_KEY = "7de99a859d0920dfb46628ab5af61dad0d618072863c2005e22cf06390639ca3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class URLAdminInfo(BaseModel):
    """the BaseModel of url admin information"""

    original_url: str
    admin_url: str


class URLInfo(URLAdminInfo):
    """with clicks"""

    clicks: int


class User(BaseModel):
    """the BaseModel of user information"""

    username: str
    passwd: bytes
    full_name: Union[str, None] = None
    email: Union[str, None] = None
    disable: Union[bool, None] = None


class UserCreate(BaseModel):
    """the BaseModel of user creating"""

    username: str
    passwd: str
    full_name: Union[str, None] = None
    email: Union[str, None] = None


class Token(BaseModel):
    """the BaseModel of JWT token"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """the BaseModel of user data"""

    username: Union[str, None] = None


db.build_db()
app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def raise_bad_request(message):
    """raise bad request"""
    raise HTTPException(status_code=400, detail=message)


def create_random_url() -> str:
    """create a random url shortener admin code if user did not provide one"""
    res = ""
    lib = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    length = 8
    for _ in range(length):
        res += lib[random.randint(0, len(lib))]
    return res


def decode_token(token):
    """decode JWT token into user information"""
    try:
        user_info = db.get_user_info(token)
        return User(
            username=user_info[0],
            passwd=user_info[1],
            full_name=user_info[2],
            email=user_info[3],
            disable=user_info[4],
        )
    except ValueError as error:
        raise_bad_request(str(error))

    return None


def verify_password(plain_password, hashed_password):
    """verify password if it is correct or not"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """get the hashed password"""
    return pwd_context.hash(password)


def authenticate_user(username: str, passwd: str):
    """authenticate user to login"""
    user_info = decode_token(username)
    if not user_info:
        return None
    if not verify_password(passwd, user_info.passwd):
        return None

    return user_info


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """get current user information"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as exc:
        raise credentials_exception from exc

    user_info = decode_token(token_data.username)
    if user_info is None:
        raise credentials_exception
    return user_info


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """get current active user"""
    if not current_user.disable:
        raise_bad_request("inactive user")
    return current_user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


if db.check_username_is_available("admin"):
    db.insert_user("admin", get_password_hash("admin"), "Admin", "admin@admin")
if db.check_username_is_available("lltzpp"):
    db.insert_user(
        "lltzpp", get_password_hash("alternate"), "miohitokiri5474", "lltzpp@gmail.com"
    )


@app.get("/")
async def read_root():
    """root"""
    raise HTTPException(status_code=200, detail="Welcome to the URL shortener API")


@app.get("/r/{url}")
async def get_url(url: str):
    """temporary redirect"""
    if db.check_admin_code_is_available(url):
        raise HTTPException(status_code=404, detail="This admin url is not exist.")

    db.update_click_count(url)

    return RedirectResponse(db.query(url))


@app.get("/list/")
async def list_url(current_user: User = Depends(get_current_active_user)):
    """list url shortener which is create by current user"""
    raise HTTPException(status_code=200, detail=db.list_url(current_user.username))


@app.get("/{username}", response_model=User)
async def get_current_user_information(
    username: str, current_user: User = Depends(get_current_active_user)
):
    """get current user information"""
    if current_user.username == username:
        current_user.passwd = b"---"
    else:
        raise_bad_request("Permission Denied.")
    raise HTTPException(status_code=200, detail=current_user)


@app.post("/token")
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """user login"""
    user_info = authenticate_user(form_data.username, form_data.password)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_info.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/add_url")
async def adding_url_with_auth_token(
    url: URLAdminInfo, current_user: User = Depends(get_current_active_user)
):
    """add url shortener"""
    if url.admin_url == "":
        url.admin_url = create_random_url()
        while not db.check_admin_code_is_available(url.admin_url):
            url.admin_url = create_random_url()
    try:
        db.insert_url(url.admin_url, url.original_url, current_user.username)
        raise HTTPException(
            status_code=201,
            detail=f"{url.admin_url} -> {url.original_url} by. {current_user.username}",
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/")
async def create_user(info: UserCreate):
    """create a new user"""
    try:
        db.insert_user(
            info.username, get_password_hash(info.passwd), info.full_name, info.email
        )
        raise HTTPException(status_code=201, detail="User created successfully.")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.delete("/delete_url/{url}")
async def delete_url_with_auth_token(
    url: str, current_user: User = Depends(get_current_active_user)
):
    """delete url shortener with admin code"""
    try:
        db.delete_url(url, current_user.username)
        raise HTTPException(status_code=200, detail=url + " is successfully deleted.")
    except ValueError as error:
        raise_bad_request(str(error))


@app.delete("/{username}")
async def delete_user(
    username: str, current_user: User = Depends(get_current_active_user)
):
    """delete user"""
    if not username == current_user.username:
        raise_bad_request("Permission Denied.")
    try:
        db.delete_user(username)
        raise HTTPException(
            status_code=200, detail=username + " is successfully deleted."
        )

    except ValueError as error:
        raise_bad_request(str(error))


@app.on_event("shutdown")
def shutdown():
    """close db when the service shutdown"""
    db.close_database()
