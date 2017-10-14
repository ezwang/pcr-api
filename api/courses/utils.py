import datetime

from models import Semester


def current_semester():
    now = datetime.datetime.now()
    semester = 'A' if now.month < 5 else ('B' if now.month < 9 else 'C')
    return Semester(now.year, semester)
