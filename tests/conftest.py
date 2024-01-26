"""
conftest
"""
import os

import pytest
from passlib.context import CryptContext

from app import db

USERNAME = "lltzpp"
PASSWD = "alternate"
LOGIN_JSON = {"username": USERNAME, "password": PASSWD}
URL_JSON = {
    "original_url": "https://miohitokiri5474.github.io/",
    "admin_url": "main_page",
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(autouse=True)
def build(request):
    """build a database before every test"""
    if os.path.exists("data.db"):
        os.remove("data.db")

    db.build_db()
    print("\tcreated a new db")

    marks = request.node.own_markers
    for i in marks:
        if i.name == "create":
            print("\tcreated built-in user")
            db.insert_user(
                USERNAME, pwd_context.hash(PASSWD), "Jamie Lin", "lltzpp@gmail.com"
            )
