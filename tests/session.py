import requests
from login_test import login

api_session = requests.session()
api_session.headers = login()[1]

