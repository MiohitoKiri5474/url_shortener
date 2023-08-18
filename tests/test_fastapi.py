"""
testing fastapi
"""

import json

from fastapi.testclient import TestClient

from app.main import app

USERNAME = "lltzpp"
PASSWD = "alternate"
CLIENT = TestClient(app)
LOGIN_JSON = {"username": USERNAME, "password": PASSWD}
URL_JSON = {
    "original_url": "https://miohitokiri5474.github.io/",
    "admin_url": "main_page",
}


def test_homepage():
    """test root"""

    res = CLIENT.get("/")
    assert res.status_code == 200
    assert res.json() == {"detail": "Welcome to the URL shortener API"}


def test_login():
    """test service logon"""

    res = CLIENT.post("/token", data=LOGIN_JSON)
    assert res.status_code == 200
    assert not res.json() == {"detail": "Incorrect username or password"}


def test_add_user_and_delete_user():
    """test add/delete user"""

    user_json = {
        "username": "miohitokiri5474",
        "passwd": "alternate",
        "full_name": "MiohitoKiri5474",
        "email": "lltzpp@gmail.com",
    }

    headers = {"accept": "application/json", "Content-Type": "application/json"}

    res = CLIENT.post("/", headers=headers, data=json.dumps(user_json))
    assert res.status_code == 201
    assert res.json() == {"detail": "User created successfully."}

    res = CLIENT.post(
        "/token", data={"username": "miohitokiri5474", "password": "alternate"}
    )
    assert res.status_code == 200
    assert not res.json() == {"detail": "Incorrect username or password"}

    jwt_token = {
        "Authorization": res.json().get("token_type")
        + " "
        + res.json().get("access_token")
    }

    res = CLIENT.delete("/" + "miohitokiri5474", headers=jwt_token)
    assert res.status_code == 200


def test_add_url_and_delete_url():
    """test add/delete url shortener after login"""

    login_res = CLIENT.post("/token", data=LOGIN_JSON)
    assert login_res.status_code == 200

    jwt_token_json = {"Authorization": "Bearer " + login_res.json().get("access_token")}

    url_add_res = CLIENT.post(
        "/add_url", headers=jwt_token_json, data=json.dumps(URL_JSON)
    )
    assert url_add_res.status_code == 201
    assert url_add_res.json() == {
        "detail": f"{URL_JSON.get ('admin_url')} -> {URL_JSON.get ('original_url')} by. {USERNAME}"
    }

    goto_url_res = CLIENT.get("/r/" + URL_JSON.get("admin_url"))
    assert goto_url_res.status_code == 200

    url_delete_res = CLIENT.delete(
        "/delete_url/" + URL_JSON.get("admin_url"), headers=jwt_token_json
    )
    assert url_delete_res.status_code == 200
    assert url_delete_res.json() == {
        "detail": f"{URL_JSON.get ('admin_url')} is successfully deleted."
    }
