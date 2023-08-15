"""
testing fastapi
"""

from fastapi.testclient import TestClient

from app.main import app

CLIENT = TestClient(app)


def test_homepage():
    """test root"""

    res = CLIENT.get("/")
    assert res.status_code == 200
    assert res.json() == "Welcome to the URL shortener API"


def test_login():
    """test service logon"""

    res = CLIENT.post("/token", data={"username": "lltzpp", "password": "alternate"})
    assert res.status_code == 200
    assert not res.json() == {"detaul": "Incorrect username or password"}
