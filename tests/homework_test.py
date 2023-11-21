from session import api_session as s
from config import URL
from datetime import datetime, timedelta

def get_homework(date_from, date_to):
    homework = s.get(URL+f"/homework/{date_from}/{date_to}")
    return homework.status_code, homework.json()

def test_homework():
    date_to = datetime.now()
    date_from = date_to - timedelta(days=31)
    status, homework = get_homework(date_from, date_to)
    assert status == 200 or status == 206
    assert isinstance(homework, list)
