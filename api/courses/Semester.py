"""
Code for semester objects.

Note that:
(Year Y, semester s) (with s=0,1,2 -> a,b,c) is semester
  3(Y-1740) + s       = 780 + 3(Y-2000) + s
Semester 2010a is 810. Current (2010c) is 812.
"""
from django.db import models
import datetime

class Semester:
  """ A semester, with a calendar year and a season.
  Season codes: (a,b,c) -> (Spring, Summer, Fall)"""
  def __init__(self, year = None, semester = None):
    """ Create a semester from a year and a season code.
      Valid inputs (all case-insensitive): Semester(2010, 'c') ==
        Semester('2010', 'c') == Semester('2010c') """
    if year is None:
      year, semester = 1740, "a" # the epoch
    if semester is None:
      year, semester = year[:-1], year[-1]
    semesternum = "abc".find(semester.lower())
    if semesternum == -1:
      raise ValueError("Invalid semester code: " + semester)
    
    self.year = int(year) # calendar year
    self.semesternum = semesternum # (0,1,2) -> (Spring, Summer, Fall)

  @property    
  def id(self):
    """ Returns the numerical ID for this semester.
    (Year Y, semester s) (with s=0,1,2 -> a,b,c) is semester
      3(Y-1740) + s       = 780 + 3(Y-2000) + s
    Semester 2010a is 810. Current (2010c) is 812. """
    return 3 * (self.year - 1740) + self.semesternum

  @property  
  def seasoncodeABC(self):
    """ Returns the season code. """
    return "ABC"[self.semesternum]
  
  def code(self):
    """ Returns code YYYYa (calendar year + season code) """
    return "%4d%s" % (self.year, self.seasoncodeABC)
  
  def __repr__(self):
    return "Semester(%d,\"%s\")" % (self.year, self.seasoncodeABC)
  
  def __str__(self):
    return "%s %d" % (["Spring", "Summer", "Fall"][self.semesternum], self.year)

  def get_absolute_url(self):
    return "/courses/course/" + self.code()

  def __cmp__(self, other):
    if other:
      return cmp(self.id, other.id)
    else:
      return 1 # arbitrarily, if other is given as '' 

def current_semester():
  now = datetime.datetime.now()
  semester = 'A' if now.month < 5 else ('B' if now.month < 9 else 'C')
  return Semester(now.year, semester)

def semesterFromID(id):
  """ Given a numerical semester ID, return a semester. """
  return Semester(1740 + id / 3, "abc"[id % 3])

def semesterFromCode(yyyys):
  if len(yyyys) != 5: raise Exception("too many or too few characters")
  year = int(yyyys[:4])
  season = yyyys[4].lower()
  return Semester(year=year, semester=season)


class SemesterField(models.Field):
  description = "A semester during which a course may be offered"

  __metaclass__ = models.SubfieldBase

  def __init__(self, *args, **kwargs):
    super(SemesterField, self).__init__(*args, **kwargs)

  def get_internal_type(self):
    return "SemesterField"

  def db_type(self, connection):
    return 'smallint'

  def to_python(self, value):
    if isinstance(value, Semester):
      return value
    if value == "":
      return Semester()
    if "HACKS!": # commence hack:
      try:
        seasons = ["Spring", "Summer", "Fall"]
        tmp_season, tmp_year = value.split(" ")
        if tmp_season in seasons:
          return Semester(tmp_year, "abc"[seasons.index(tmp_season)])
      except:
        pass
    try: 
      id = int(value)
    except ValueError as e:
      raise e
    else:
      return semesterFromID(id)

  def get_prep_value(self, value):
    return value.id
