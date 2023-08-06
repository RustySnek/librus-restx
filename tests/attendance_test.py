from session import api_session as s
from config import URL

def get_attendance():
    attendance = s.get(URL+"/attendance")
    return attendance.status_code, attendance.json()

def test_attendance():
    status, attendance = get_attendance()
    assert status == 200
    assert isinstance(attendance, list)
