"""database relate"""

from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_PATH = "sqlite:///data.db"
BASE = declarative_base()


class URLData(BASE):
    __tablename__ = "URL_data"

    username = Column(String)
    url = Column(String)
    admin_url = Column(String, primary_key=True)
    clicks = Column(Integer)


class UserData(BASE):
    __tablename__ = "user_data"

    username = Column(String, primary_key=True)
    full_name = Column(String)
    passwd = Column(String)
    email = Column(String)
    disable = Column(Boolean)


SESSION = None
ENGINE = None


def build_db():
    """create database if DB_PATH is not exist"""

    global BASE, SESSION, ENGINE

    ENGINE = create_engine(DB_PATH, echo=True)
    BASE.metadata.create_all(bind=ENGINE)
    session = sessionmaker(bind=ENGINE)
    SESSION = session()


def close_database():
    """close the session when the service shutdown"""

    global SESSION

    SESSION.close()


def check_admin_code_is_available(admin_url: str):
    """check admin code is available of not before adding a new url shortenet into database"""

    session = sessionmaker(bind=ENGINE)

    result = session().query(URLData).filter_by(admin_url=admin_url).first()

    return result is None


def insert_url(admin_url: str, ori: str, username: str):
    """add an url shortener into database"""
    if not check_admin_code_is_available(admin_url):
        raise ValueError(
            "The chosen short code is already taken. Please choose a different code."
        )

    global SESSION

    new_data = URLData(
        username=username,
        url=ori,
        admin_url=admin_url,
        clicks=0,
    )

    SESSION.add(new_data)
    SESSION.commit()


def update_click_count(admin_url: str):
    """update click count after every redirect"""

    global SESSION

    modify_data = SESSION.query(URLData).filter_by(admin_url=admin_url).first()

    if modify_data:
        modify_data.clicks = modify_data.clicks + 1
        SESSION.commit()


def query(admin_url: str):
    """query original url by admin code from database"""

    global SESSION

    result = SESSION.query(URLData).filter_by(admin_url=admin_url).first()

    if result:
        return result.url

    return None


def delete_url(url: str, username: str):
    """delete url shortener by target user from database"""

    global SESSION

    result = SESSION.query(URLData).filter_by(admin_url=url, username=username).first()

    if result:
        SESSION.delete(result)
        SESSION.commit()
    else:
        raise ValueError("This admin url is not exist or is not created by this user.")


def list_url(username: str):
    """list out all url shortener create by target user"""

    global SESSION

    result = SESSION.query(URLData).filter_by(username=username).all()
    res = []
    for i in result:
        res.append([i.admin_url, i.url, i.clicks])

    return res


def check_username_is_available(name: str):
    """check username is available or not before add a new user into database"""

    global SESSION

    result = SESSION.query(UserData).filter_by(username=name).first()

    return result is None


def insert_user(name: str, passwd, full_name: str, email: str):
    """add a new user information into database"""

    if not check_username_is_available(name):
        raise ValueError(
            "The chosen user name is already taken, please choose a different one."
        )

    global SESSION
    new_data = UserData(
        username=name,
        full_name=full_name,
        passwd=passwd,
        email=email,
        disable=True,
    )

    SESSION.add(new_data)
    SESSION.commit()


def delete_user(name: str):
    """delete user from database"""
    if check_username_is_available(name):
        raise ValueError("The Choosen username is no in our database.")

    global SESSION

    result = SESSION.query(UserData).filter_by(username=name).first()

    if result:
        SESSION.delete(result)
        SESSION.commit()


def update_user_status(name: str, disable: bool):
    """update user status"""
    result = SESSION.query(UserData).filter_by(username=name).first()
    result.disable = disable

    SESSION.commit()


def get_passwd(name: str):
    """get hashed password of target user"""

    if check_username_is_available(name):
        raise ValueError("User not found.")

    print("\t\tusername is found")

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

    global SESSION

    result = SESSION.query(UserData).filter_by(username=name).first()

    if result:
        return [
            result.username,
            result.passwd,
            result.full_name,
            result.email,
            result.disable,
        ]

    raise ValueError("User information not found.")
