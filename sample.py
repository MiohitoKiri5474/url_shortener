"""This is a example for testing api."""
import getpass
import json
import subprocess

import requests


class JWTToken:
    """record jwt token"""

    def __init__(self):
        self.jwt_token = None

    def get_token(self):
        """get the value of jwt_token"""
        return self.jwt_token

    def update_token(self, _token):
        """update jwt_token"""
        self.jwt_token = _token


USER_INPUT = ""
USERNAME = ""
PASSWD = ""
URL = "http://localhost:8000"
TIMEOUT = 0.5
JWT_TOKEN = JWTToken()


def subprocess_run(command):
    """subprocess execute"""
    try:
        output = subprocess.run(
            command, capture_output=True, text=True, check=True
        ).stdout
        return output
    except subprocess.CalledProcessError as err:
        raise ValueError(str(err)) from err


def login_app(username: str, passwd: str):
    """login service"""
    command = [
        "curl",
        "-X",
        "POST",
        URL + "/token",
        "-H",
        "accept: application/json",
        "-H",
        "Content-Type: application/x-www-form-URLencoded",
        "-d",
        "grant_type=&username="
        + username
        + "&password="
        + passwd
        + "&scope=&client_id=&client_secret=",
    ]

    try:
        res = subprocess_run(command)
        js_res = json.loads(res)
        JWT_TOKEN.update_token(js_res.get("access_token"))
        return (
            "Welcome, "
            + whoami().json().get("username")
            + ". Hope you have a nice day. "
        )
    except ValueError as err:
        raise ValueError(str(err)) from err


def add_url(ori_url: str, _admin_url: str):
    """adding url shortener into the service"""
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN.get_token()}",
        "Content-Type": "application/json",
    }
    json_data = {"original_url": ori_url, "admin_url": _admin_url}
    return requests.post(
        URL + "/add_url", json=json_data, headers=headers, timeout=TIMEOUT
    ).content.decode("utf-8")


def delete_url(admin_url: str):
    """delete url shortener with admin code"""
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN.get_token()}",
    }
    return requests.delete(
        URL + "/delete_url/" + admin_url, headers=headers, timeout=TIMEOUT
    ).content.decode("utf-8")


def list_url():
    """list all url shortener from current user in service"""
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN.get_token()}",
    }
    return requests.get(URL + "/list/", headers=headers, timeout=TIMEOUT).json()


def whoami():
    """get current user information"""
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN.get_token()}",
    }
    return requests.get(URL + "/whoami/", headers=headers, timeout=TIMEOUT)


while True:
    USER_INPUT = input("> ").split()
    if len(USER_INPUT) == 0:
        continue
    if USER_INPUT[0] == "exit":
        break
    if USER_INPUT[0] == "login":
        if JWT_TOKEN.get_token():
            yn = input(
                "The previous user has not logged out yet. Do you want to logout? [y/N]:"
            ).lower()
            if yn in {"y", "yes"}:
                JWT_TOKEN.update_token(None)
            else:
                continue
        USERNAME = input("Enter your username: ")
        PASSWD = getpass.getpass("Enter your password: ")
        try:
            print(login_app(USERNAME, PASSWD))
        except ValueError as ERROR:
            print("[Error]: " + str(ERROR))
    elif USER_INPUT[0] == "add":
        if len(USER_INPUT) < 3:
            print("[Error]: This command needs more arguments.")
        else:
            print(add_url(USER_INPUT[1], USER_INPUT[2]))
    elif USER_INPUT[0] == "delete":
        if len(USER_INPUT) < 2:
            print("[Error]: This command needs more arguments.")
        else:
            print(delete_url(USER_INPUT[1]))
    elif USER_INPUT[0] == "list":
        lit = list_url()
        user_info = whoami()
        if user_info.status_code == 401:
            print("[Error]: User not found, please login first.")
        elif len(lit) == 0:
            print(
                "User "
                + user_info.json().get("username")
                + " has not yet added any URL shortener."
            )
        else:
            print("URL shortener create by. " + user_info.json().get("username") + ":")
            for i in lit:
                print("\t" + i[0] + " -> " + i[1])
    elif USER_INPUT[0] == "whoami":
        user_info = whoami()
        if user_info.status_code == 401:
            print("[Error]: User not found, please login first.")
        else:
            user_info_js = user_info.json()
            print("Username:\t" + user_info_js.get("username"))
            print("Full Name:\t" + user_info_js.get("full_name"))
            print("Email:\t\t" + user_info_js.get("email"))
    elif USER_INPUT[0] == "logout":
        if JWT_TOKEN.get_token():
            print("User " + whoami().json().get("username") + " logout.")
        else:
            print("Cannot find the logged-in user.")
        JWT_TOKEN.update_token(None)
    elif USER_INPUT[0] == "help":
        print("login:\t\t\t\tUser login")
        print("logout:\t\t\t\tUser logout")
        print("whoami:\t\t\t\tDisplay user information")
        print("list:\t\t\t\tDisplay URL shortener create by user")
        print("add [original_url] [admin_url]: Create a URL shortener")
        print(
            "delete [admin_url]:\t\tDetele URL shortener which admin_code is [admin_url]"
        )
    else:
        print("[Error]: Command not found.")
