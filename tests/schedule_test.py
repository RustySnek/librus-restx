from session import api_session as s
from config import URL
from datetime import datetime

def get_schedule(year, month):
    schedule = s.get(URL+f"/schedule/{year}/{month}")
    return schedule.status_code, schedule.json()

def test_schedule():
    now = datetime.now().date()
    status, schedule = get_schedule(now.year, now.month)
    assert status == 200
    assert isinstance(schedule, dict)

