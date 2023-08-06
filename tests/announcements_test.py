from session import api_session as s
from config import URL

def get_announcements():
    announcements = s.get(URL+"/announcements")
    return announcements.status_code, announcements.json()

def test_announcements():
    status, announcements = get_announcements()
    assert status == 200
    assert isinstance(announcements, list)

