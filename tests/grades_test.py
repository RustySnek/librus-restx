from session import api_session as s
from config import URL

def get_grades():
    grades = s.get(URL+"/grades/all")
    return grades.status_code, grades.json()

def test_grades():
    status, grades = get_grades()
    assert status == 200
    assert isinstance(grades, dict)
