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
