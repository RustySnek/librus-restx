from session import api_session as s
from config import URL


last_login_date = "2020-12-12"
last_login_time = "12:29:59"

def get_overview(lld, llt):
    overview = s.post(URL+"/overview", json={"last_login_date": lld, "last_login_time": llt})
    return overview.status_code, overview.json()

def test_overview():
    status, overview = get_overview(last_login_date, last_login_time)
    assert status == 200
    assert isinstance(overview, dict)
