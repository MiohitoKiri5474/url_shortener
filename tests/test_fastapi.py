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


def test_when_admin_code_is_not_found():
    """test api when admin code is not found"""

    res = CLIENT.get("/r/lmao")
    assert res.status_code == 404


def test_user_is_not_exist():
    """test login with username is not found"""

    user_json = {
        "username": "user_not_found",
        "password": "what_is_password_can_i_eat_it",
    }

    res = CLIENT.post("/token", data=user_json)
    assert res.status_code == 400
    assert res.json() == {"detail": "User not found."}


def test_add_url_is_already_exist():
    """test add url which is already exist"""

    login_res = CLIENT.post("/token", data=LOGIN_JSON)
    assert login_res.status_code == 200

    jwt_token_json = {"Authorization": "Bearer " + login_res.json().get("access_token")}

    url_add_res_first_time = CLIENT.post(
        "/add_url", headers=jwt_token_json, data=json.dumps(URL_JSON)
    )
    assert url_add_res_first_time.status_code == 201
    assert url_add_res_first_time.json() == {
        "detail": f"{URL_JSON.get ('admin_url')} -> {URL_JSON.get ('original_url')} by. {USERNAME}"
    }

    url_add_res_second_time = CLIENT.post(
        "/add_url", headers=jwt_token_json, data=json.dumps(URL_JSON)
    )
    assert url_add_res_second_time.status_code == 400
    assert url_add_res_second_time.json() == {
        "detail": "The chosen short code is already taken. Please choose a different code."
    }

    url_delete_res = CLIENT.delete(
        "/delete_url/" + URL_JSON.get("admin_url"), headers=jwt_token_json
    )
    assert url_delete_res.status_code == 200
    assert url_delete_res.json() == {
        "detail": f"{URL_JSON.get ('admin_url')} is successfully deleted."
    }


def test_add_user_is_already_exist():
    """test add a user which username is already exist"""

    user_json = json.dumps(
        {
            "username": "miohitokiri5474",
            "passwd": "alternate",
            "full_name": "MiohitoKiri5474",
            "email": "lltzpp@gmail.com",
        }
    )

    headers = {"accept": "application/json", "Content-Type": "application/json"}

    first_time_res = CLIENT.post("/", headers=headers, data=user_json)
    assert first_time_res.status_code == 201
    assert first_time_res.json() == {"detail": "User created successfully."}

    second_time_res = CLIENT.post("/", headers=headers, data=user_json)
    assert second_time_res.status_code == 400
    assert second_time_res.json() == {
        "detail": "The chosen user name is alreadt taken, please choose a different one."
    }
