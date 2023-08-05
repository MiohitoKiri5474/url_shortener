import subprocess, json, getpass, requests

user_input = ''
username = ''
passwd = ''
url = 'http://localhost:8000'
jwt_token = None

def subprocess_run (command):
    try:
        output = subprocess.run (command, capture_output = True, text = True, check = True).stdout
        return output
    except subprocess.CalledProcessError as error:
        raise ValueError (str (error))

def login_app (username: str, passwd: str):
    command = ['curl', '-X', 'POST', url + '/token', '-H', 'accept: application/json', '-H', 'Content-Type: application/x-www-form-urlencoded', '-d', 'grant_type=&username=' + username + '&password=' + passwd + '&scope=&client_id=&client_secret=']

    try:
        res = subprocess_run (command)
        js_res = json.loads (res)
        global jwt_token
        jwt_token = js_res.get ('access_token')
        return 'Welcome, ' + whoami().json().get ('username') + '. Hope you have a nice day. '
    except ValueError as error:
        raise ValueError (str (error))

def add_url (ori_url: str, _admin_url: str):
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    json_data = {
        "original_url": ori_url,
        "admin_url": _admin_url
    }
    return requests.post (url + '/add_url', json = json_data, headers = headers ).content.decode ('utf-8')

def delete_url (admin_url: str):
    headers = {
        "Authorization": f"Bearer {jwt_token}",
    }
    return requests.delete (url + '/delete_url/' + admin_url, headers = headers ).content.decode ('utf-8')

def list_url():
    headers = {
        "Authorization": f"Bearer {jwt_token}",
    }
    return requests.get (url + '/list/', headers = headers).json()

def whoami():
    headers = {
        "Authorization": f"Bearer {jwt_token}",
    }
    return requests.get (url + '/whoami/', headers = headers)

while (True):
    user_input = input ('> ').split()
    if len (user_input) == 0:
        continue
    if user_input[0] == 'exit':
        break
    elif user_input[0] == 'login':
        if jwt_token:
            yn = input ('The previous user has not logged out yet. Do you want to logout? [y/N]:').lower()
            if yn == 'y' or yn == 'yes':
                jwt_token = None
            else:
                continue
        username = input ('Enter your username: ')
        passwd = getpass.getpass ('Enter your password: ')
        try:
            print (login_app (username, passwd))
        except ValueError as error:
            print ('[Error]: ' + str (error))
    elif user_input[0] == 'add':
        if len (user_input) < 3:
            print ('[Error]: This command needs more arguments.')
        else:
            print (add_url (user_input[1], user_input[2]))
    elif user_input[0] == 'delete':
        if len (user_input) < 2:
            print ('[Error]: This command needs more arguments.')
        else:
            print (delete_url (user_input[1]))
    elif user_input[0] == 'list':
        lit = list_url()
        user_info = whoami()
        if user_info.status_code == 401:
            print ('[Error]: User not found, please login first.')
        elif len (lit) == 0:
            print ('User ' + user_info.json().get ('username') + ' has not yet added any url shortener.' )
        else:
            print ('url shortener create by. ' + user_info.json().get ('username') + ':')
            for i in lit:
                print ( '\t' + i[0] + ' -> ' + i[1])
    elif user_input[0] == 'whoami':
        user_info = whoami()
        if user_info.status_code == 401:
            print ('[Error]: User not found, please login first.')
        else:
            user_info_js = user_info.json()
            print ('Username:\t' + user_info_js.get ('username'))
            print ('Full Name:\t' + user_info_js.get ('full_name'))
            print ('Email:\t\t' + user_info_js.get ('email'))
    elif user_input[0] == 'logout':
        if jwt_token:
            print ('User ' + whoami().json().get ('username') + ' logout.')
        else:
            print ('Cannot find the logged-in user.')
        jwt_token = None
    elif user_input[0] == 'help':
        print ('login:\t\t\t\tUser login')
        print ('logout:\t\t\t\tUser logout')
        print ('whoami:\t\t\t\tDisplay user information')
        print ('list:\t\t\t\tDisplay URL shortener create by user')
        print ('add [original_url] [admin_url]: Create a URL shortener')
        print ('delete [admin_url]:\t\tDetele URL shortener which admin_code is [admin_url]')
    else:
        print ('[Error]: Command not found.')
