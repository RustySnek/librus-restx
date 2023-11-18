from flask import Flask, request, jsonify, make_response, request
from flask_restx import Api, Resource, fields, reqparse
from librus_apix.exceptions import AuthorizationError, TokenError, DateError, MaintananceError, ParseError
from librus_apix.get_token import get_token, Token
from librus_apix.messages import get_recieved, message_content, get_max_page_number
from librus_apix.grades import get_grades
from librus_apix.attendance import get_attendance, get_detail
from librus_apix.schedule import get_schedule, schedule_detail
from librus_apix.timetable import get_timetable
from datetime import datetime
from librus_apix.announcements import get_announcements
from librus_apix.homework import get_homework, homework_detail
from json import JSONDecodeError
from collections import defaultdict

from flask_cors import CORS
app = Flask(__name__)
api = Api(app)
CORS(app, support_credentials=True, resources={r"/*": {"origins": "*"}})
model = api.model('Login', {
    'username': fields.String,
    'password': fields.String
})
overview_model = api.model('Overview', {
    'last_login_date': fields.String,
    'last_login_time': fields.String,
    })

def dictify(_list: list):
    return [val.__dict__ for val in _list]

@api.route('/login')
class Login(Resource):
    @api.doc(body=model)
    def post(self):
        try:
            token = get_token(api.payload['username'], api.payload['password'])
            return {"X-API-Key": token.API_Key}, 200
        except MaintananceError as err:
            return {"Maintanance": str(err)}, 503
        except KeyError:
            return {"error": "Provide a proper Authorization header"}, 401
        except AuthorizationError as AuthError:
            return {"error": str(AuthError)}, 401

@api.route('/messages/pages')
class MessagePages(Resource):
    @api.header("X-API-Key", type=[str])
    def get(self):
        try:
            token = Token(request.headers.get("X-API-Key"))
            max_number = {"max_page": get_max_page_number(token)}, 200
        except TokenError as err:
            max_number = {"error": str(err)}, 401
        return max_number

@api.route('/messages/<int:page>')
class Message(Resource):
    @api.header("X-API-Key", type=[str])
    def get(self, page):
        try:
            token = Token(request.headers.get("X-API-Key"))
            msgs = dictify(get_recieved(token, page)), 200
        except TokenError as token_err:
            msgs = {'error': str(token_err)}, 401
        return msgs
@api.route('/messages/content/<string:content_url>')
class MessageContent(Resource):
    def get(self, content_url: str):
        try:
            token = Token(request.headers.get("X-API-Key"))
            content = message_content(token, content_url), 200
        except TokenError as token_err:
            content = {'error': str(token_err)}, 401
        return content

@api.route('/overview')
class Overview(Resource):
    """
    format: %Y-%m-%d %H:%M:%S
    """
    @api.doc(model=overview_model)
    def post(self):
        try:
            last_login_date = api.payload['last_login_date']
            last_login_time = api.payload['last_login_time']
            last_login = datetime.strptime(" ".join([last_login_date, last_login_time]), '%Y-%m-%d %H:%M:%S')
        except KeyError:
            return {"Error": 'Please provide a proper date and time headers.'}, 401
        except ValueError:
            return {"Error": "Please provide a proper date/time values. YY-MM-DD / HH:MM:SS"}, 401

        def to_dict(obj):
                    initial = obj.__dict__
                    try:
                        initial.update({"value": obj.value})
                    except:
                        pass
                    return initial

        try:
            token = Token(request.headers.get('X-API-Key'))

            grades = get_grades(token, 'all')[0]
            converted_grades = {}
            status_code = 200
            for semester in grades:
                converted_grades[semester] = {}
                for subject in grades[semester]:
                    
                    converted_grades[semester][subject] = []
                    for grade in grades[semester][subject]:
                        if datetime.strptime(grade.date, "%Y-%m-%d") < last_login:
                            continue
                        else:
                            converted_grades[semester][subject].append(grade.__dict__)
            dictify_attendance = list(map(dictify, [at for at in get_attendance(token)]))
            attendance = []
            for _semester in dictify_attendance:
                attendance.append(list(filter(lambda x: datetime.strptime(x["date"], "%Y-%m-%d") > last_login, _semester)))
            messages = get_recieved(token, 0)
            new_messages = []
            for message in messages:
                if datetime.strptime(message.date, '%Y-%m-%d %H:%M:%S') > last_login:
                    new_messages.append(message.__dict__)
            announcements = get_announcements(token)
            new_announcements = []
            for announcement in announcements:
                if datetime.strptime(announcement.date, '%Y-%m-%d') > last_login:
                    new_announcements.append(announcement.__dict__)

        except TokenError as token_err:
            converted_grades = {'error': str(token_err)}
            status_code = 401
            attendance = {'error': str(token_err)}
            new_messages = {'error': str(token_err)}
            new_announcements = {'error': str(token_err)}
        return {'Grades': converted_grades, 'Attendance': attendance, 'Messages': new_messages, 'Announcements': new_announcements}, status_code

@api.route('/grades/<string:sort_by>')
class Grades(Resource):
    def get(self, sort_by: str) -> tuple[dict, int]:
        """
        Returns a dictionary containing Grades and GPA (Average Grades) {"Grades": ..., "Gpa": ...}
        Grades values contain both semesters as dictionaries inside a list [{"Biology": [...], [...]}, {"Biology": [...], [...]}]
        Each subject inside a semester contains a list of all grades. A grade is a dictionary with all the grade attributes.
        Gpa values contain a dictionary with Subject names as keys and a list of semesters avg. and final avg.
        GPA structure: {
                "Biology": [{"gpa": 3.0}, {"gpa": 4.3}],
                "History": [{"gpa: 2.1"}, {"gpa": 1.2}],
                }
        Grades structure: [
                { # First Semester
                    "Biology": [dicts of grades],
                    "History": [dicts of grades],
                    ...
                    },
                { # Second Semester
                    "Biology": [dicts of grades],
                    ...
                    }
                ]
        """
        def to_dict(obj):
            initial = obj.__dict__
            try:
                initial.update({"value": obj.value})
            except:
                pass
            return initial
        try:
            token = Token(request.headers.get("X-API-Key"))
            all_grades, avg_grades = get_grades(token, sort_by)
            grades = [defaultdict(list), defaultdict(list)]
            status_code = 200
            for semester in all_grades:
                for subject in all_grades[semester]:
                    grades[semester-1][subject] = list(map(to_dict, all_grades[semester][subject]))
            for subject in avg_grades:
                avg_grades[subject] = dictify(list(avg_grades[subject]))

        except TokenError as token_err:
           grades = {'error': str(token_err)}
           avg_grades = {'error': str(token_err)}
           status_code = 401

        return {'Grades': grades, 'Gpa': avg_grades}, status_code

@api.route('/attendance/')
class Attendance(Resource):
    def get(self):
        try:
            token = Token(request.headers.get("X-API-Key"))
            attendance = list(map(dictify, [_a for _a in get_attendance(token, {'zmiany_logowanie_wszystkie': ''})])), 200
        except TokenError as token_err:
           attendance = {'error': str(token_err)}, 401
        return attendance
@api.route('/attendance/details/<string:detail_url>')
class AttendanceDetail(Resource):
    def get(self, detail_url: str):
        try:
            token = Token(request.headers.get("X-API-Key"))
            detail = get_detail(token, detail_url), 200
        except TokenError as token_err:
            detail = {'error': str(token_err)}, 401
        return detail
@api.route('/schedule/<string:year>/<string:month>')
class Schedule(Resource):
    def get(self, year: str, month: str):
        try:
            token = Token(request.headers.get("X-API-Key"))
            _schedule = get_schedule(token, month, year)
            schedule = defaultdict(list)
            for day in _schedule:
                schedule[day] = dictify(_schedule[day])
        except TokenError as token_err:
            schedule = {'error': str(token_err)}, 401
        return schedule
@api.route('/schedule/details/<string:detail_prefix>/<string:detail_url>')
class ScheduleDetail(Resource):
    def get(self, detail_prefix: str, detail_url: str):
        try:
            token = Token(request.headers.get("X-API-Key"))
            details = schedule_detail(token, detail_prefix, detail_url), 200
        except TokenError as token_err:
            details = {'error': str(token_err)}, 401
        return details
@api.route('/timetable/<string:year>/<string:month>/<string:day>')
class Timetable(Resource):
    def get(self, **kwargs):
        try:
            token = Token(request.headers.get("X-API-Key"))
            timetable = get_timetable(token, datetime.strptime('-'.join(kwargs.values()), '%Y-%m-%d'))
            timetable = {key: dictify(val) for key,val in timetable.items()}, 200
        except TokenError as token_err:
            timetable = {'error': str(token_err)}, 401
        except DateError as date_err:
            timetable = {'error': str(date_err)}, 401
        return timetable
@api.route('/announcements')
class Announcements(Resource):
    def get(self):
        try:
            token = Token(request.headers.get("X-API-Key"))
            announcements = dictify(get_announcements(token)), 200
        except TokenError as token_err:
            announcements = {'error': str(token_err)}, 401
        return announcements
@api.route('/homework/details/<string:detail_url>')
class HomeworkDetails(Resource):
    def get(self, detail_url: str):
        try:
            token = Token(request.headers.get("X-API-Key"))
            details = homework_detail(token, detail_url), 200
        except TokenError as token_err:
            details = {'error': str(token_err)}, 401
        return details
@api.route('/homework/<string:date_from>/<string:date_to>')
class Homework(Resource):
    def get(self, date_from: str, date_to: str):
        try:
            token = Token(request.headers.get("X-API-Key"))
            homework = get_homework(token, date_from, date_to)
            if len(homework) > 0:
                homework = dictify(homework), 200
            else:
                homework = {'No homework found.': ''}
        except TokenError as token_err:
            homework = {'error': str(token_err)}, 401
        except ParseError as parse_err:
            homework = {'No homework found.': ''}, 206
        return homework

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
