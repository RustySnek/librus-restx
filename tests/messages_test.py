import requests
from session import api_session as s
from config import URL

def get_pages():
    pages = s.get(URL+"/messages/pages")
    return pages.status_code, pages.json()["max_page"]

def get_messages(page):
    msgs = s.get(URL+"/messages/"+str(page))
    return msgs.status_code, msgs.json()
def test_messages():
    status, max_page= get_pages()
    message_status, messages = get_messages(max_page)
    assert status == 200
    assert message_status == 200
    assert isinstance(messages, list)
    if len(messages) > 0:
        pass
        # Once ill get some messages ill add the logic here.....
    
