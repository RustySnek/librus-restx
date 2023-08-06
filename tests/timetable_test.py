from session import api_session as s
from config import URL
from datetime import datetime, timedelta

def get_closest_monday(target_date):
    # Calculate the difference between the target date and the nearest Monday
    days_until_monday = (target_date.weekday() - 0) % 7
    
    # Calculate the date of the closest Monday
    closest_monday = target_date - timedelta(days=days_until_monday)
    
    return closest_monday

def get_timetable(year, month, day):
    timetable = s.get(URL+f"/timetable/{year}/{month}/{day}")
    return timetable.status_code, timetable.json()

def test_timetable():
    now = datetime.now()
    monday = get_closest_monday(now).date()
    status, timetable = get_timetable(monday.year, monday.month, monday.day)
    assert status == 200 
    assert isinstance(timetable, dict)
