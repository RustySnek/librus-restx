import requests
from config import *

def login():
    resp = requests.post("http://127.0.0.1:5000/login", json={"username": username, "password": password}, headers=HEADERS)
    return resp.status_code, resp.json()

def test_login():
    status, header = login()
    assert status == 200
    assert isinstance(header, dict)
    assert list(header.keys())[0] == "X-API-Key"
