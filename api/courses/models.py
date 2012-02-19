from django.db import models
from Semester import *
from links import *
import urllib
import re

# Note: each class has get_absolute_url - this is for "url" when queried

# TODO get rid of this?
def json_output(d):
  return d # dict((k, v) for (k, v) in d.iteritems() if v is not None)

class Department(models.Model):
  """A department/subject"""
  code = models.CharField(max_length=5, primary_key=True)
  name = models.CharField(max_length=200)

  def __unicode__(self):
    return self.code

  def get_absolute_url(self):
    # don't know actual semester
    return department_url(self.code.lower())

class CourseHistory(models.Model):
  """A course, as it has existed for many semesters. Various courses
     (several Courses each of CIS 160, CIS 260, CSE 260...) will all
     point to the same CourseHistory if they're all continuations
     of the same course."""
  notes = models.TextField()
  def __unicode__(self):
    return u"CourseHistory ID %d (%s)" % (self.id, self.notes)
  
  @property
  def aliases(self):
    """all names that this thing is known by"""
    #TODO: shadowing (IE, CIS 260 is not used by another course, don't alias 
    #me that way.
    return Alias.objects.filter(course__history=self).only('coursenum', 'department__name')

  def get_absolute_url(self):
    return coursehistory_url(self.id)

class Course(models.Model):
  """A course that can be taken during a particular semester
     (e.g. CIS-120 @2010c). A course may have multiple
     crosslistings, i.e. COGS 001 and CIS 140 are the same
     course. 

     The following should be distinct courses (TODO are they?):
     WRIT-039-301 and WRIT-039-303 (they have same course number,
      but different titles)
  """
  semester = SemesterField() # models.IntegerField() # ID to create a Semester
  name = models.CharField(max_length=200)
  credits = models.FloatField(null=True)
  description = models.TextField()
  history = models.ForeignKey(CourseHistory, null=True)
  oldpcr_id = models.IntegerField(null=True)

  def __unicode__(self):
    return "%s %s" % (self.id, self.name)

  def get_absolute_url(self):
    return course_url(self.id)

  def getAliases(self):
    return ["%s-%03d" % (x.department.code, x.coursenum)
            for x in self.alias_set.all()]

  def basic_info(self):
    return {
      'id': self.id, 'name': self.name,
      'aliases': self.getAliases(), 'path': self.get_absolute_url(),
      'semester': self.semester.code()
    }

  def toShortJSON(self):
    return json_output(self.basic_info()) 

  def toJSON(self):
    result = self.basic_info()
    path = self.get_absolute_url()
    result.update({
      'credits': self.credits,
      'description': self.description,
      SECTION_TOKEN: {
        'path': path + '/' + SECTION_TOKEN,
        RSRCS: [x.toShortJSON() for x in self.section_set.all()],
      },
      REVIEW_TOKEN: {
        'path': path + '/' + REVIEW_TOKEN,
      },
      COURSEHISTORY_TOKEN: {'path': coursehistory_url(self.history_id)},
    })

    return json_output(result)

class Instructor(models.Model):
  """ A course instructor or TA (or "STAFF")"""
  #Leave names able to accept nulls- some professor names have been redacted
  first_name = models.CharField(max_length=80, null=True) 
  last_name = models.CharField(max_length=80, null=True)
  #TODO: don't have these yet
  pennkey = models.CharField(max_length=80, null=True)
  email = models.EmailField(max_length=80, null=True)
  #TODO photo?
  website = models.URLField(max_length=200, null=True)
  oldpcr_id = models.IntegerField(null=True)
 
  @property
  def name(self):
    return (self.first_name or "") + " " + (self.last_name or "")

  @property
  def temp_id(self):
    return re.sub(r"[^\w]", "-", "%d %s" % (self.id, self.name))
    #for pennapps demo only

  def get_absolute_url(self):
    return instructor_url(self.temp_id)

  def __unicode__(self):
    return self.name

class Alias(models.Model):
  """ A (department, number) name for a Course. A Course will have
  as many Aliases as it has crosslistings. """
  
  course = models.ForeignKey(Course)
  department = models.ForeignKey(Department)
  coursenum = models.IntegerField()
  semester = SemesterField() # redundant; should equal course.semester
  #when importing from registrat, we don't have pcr_id's
  oldpcr_id = models.IntegerField(null=True)

  def __unicode__(self):
    return "%s: %s-%03d (%s)" % (self.course.id, 
                                 self.department, 
                                 self.coursenum,
                                 self.semester.code()
                                )

  def get_absolute_url(self):
    return "/courses/course/%s/%s/%03d/" % (
      self.semester.code(),
      str(self.course.department).lower(),
      self.course.coursenum) #TODO dereference alias?

  @property
  def course_code(self):
    """returns something akin to the tuple ('CIS', 120)"""
    return (self.department.code, self.coursenum)
 
class Section(models.Model):
  """ A section of a Course
  Inherits crosslisting properties from course
  (e.g. if COGS-001 and CIS-140 are Aliases for course 511, then
  COGS-001-401 and CIS-140-401 are "aliases" for section 511-401
  TODO: is this structure guaranteed by the registar?

  TODO: document how group works
  """
  course      = models.ForeignKey(Course)
  name        = models.CharField(max_length=200)
  sectionnum  = models.IntegerField()
  instructors = models.ManyToManyField(Instructor, null=True)
  group       = models.IntegerField(null=True)
  sectiontype = models.CharField(max_length=3, null=True)
  """ Section type values:
  CLN clinic
  DIS dissertation
  IND independent study
  LAB lab
  LEC lecture
  MST masters thesis
  REC recitation
  SEM seminar
  SRT senior thesis
  STU studio
  """
  #need to allow nulls for when importing from registrat
  oldpcr_id = models.IntegerField(null=True)

  def __unicode__(self):
    return "%s-%03d " % (self.course, self.sectionnum)

  def get_absolute_url(self):
    return section_url(self.course_id, self.sectionnum)

  class Meta:
    """ To hold uniqueness constraint """
    unique_together = (("course", "sectionnum"),)

  """
  def apiify_section(section, course=None):
  s.instructors = [apiify_instructor(i) for i in section.instructors.all()]
  s.reviews = [apiify_review(r, section=s) for r in section.review_set.all()]
  return s

    def __init__(self, course, sectionnum):
    self.course = course # Course object
    self.name = None # String, with the name of the section
    self.sectionnum = sectionnum # Integer (e.g. 1 for 001)
    self.group = None # Integer
    self.instructors = None # List of APIInstructors
    self.meetingtimes = None # List of meetingtime_json outputs
    self.reviews = None # List of APIReview Objects
    """

  def getAliases(self):
    return ["%s-%03d" % (alias, self.sectionnum)
            for alias in self.course.getAliases()]

  @property
  def api_id(self):
    return "%s-%03d" % (self.course_id, self.sectionnum)
  
  def toShortJSON(self):
    return json_output({
      'id': self.api_id, 
      'aliases': self.getAliases(),
      'name': self.name,
      'sectionnum': "%03d" % self.sectionnum, 
      'path': self.get_absolute_url(),
      })

  def toJSON(self):
    path = self.get_absolute_url()
    return json_output({
      'id': self.api_id,
      'aliases': self.getAliases(),
      'group': self.group, 
      'name': self.name,
      'sectionnum': "%03d" % self.sectionnum, 
      INSTRUCTOR_TOKEN: '**TODO**', # optlist_map(lambda i: i.toShortJSON(), self.instructors),
      'meetingtimes': '**TODO**', # list_json(self.meetingtime_set.all()), 
      'path': path,
      COURSE_TOKEN: self.course.toShortJSON(),
      REVIEW_TOKEN: {
        'path': '%s/%s' % (path, REVIEW_TOKEN),
         RSRCS: '**TODO**' # [x.toShortJSON() for x in self.reviews]
      },
    })

class Review(models.Model):
  """ The aggregate review data for a class. """
  section = models.ForeignKey(Section) 
  instructor = models.ForeignKey(Instructor)
  forms_returned = models.IntegerField()
  forms_produced = models.IntegerField()
  form_type = models.IntegerField()
  comments = models.TextField()

  class Meta:
    """ To hold uniqueness constraint """
    unique_together = (("section", "instructor"),)

  def __unicode__(self):
    return "Review for %s" % str(self.section)

  def get_absolute_url(self):
    pennkey = self.instructor.pennkey if self.instructor else "99999-JAIME-MUNDO"
    return review_url(self.section.course_id, self.section.sectionnum, pennkey)

class ReviewBit(models.Model):
  """ A component of a review. """
  review = models.ForeignKey(Review)
  field = models.CharField(max_length=30)
  score = models.FloatField()

  class Meta:
    """ To hold uniqueness constraint """
    unique_together = (("review", "field"),)

  def __unicode__(self):
    return "%s - %s: %s" % (str(self.review), self.field, self.score)

class Building(models.Model):
  """ A building at Penn. """
  code = models.CharField(max_length=4)
  name = models.CharField(max_length=80)
  latitude = models.FloatField()
  longitude = models.FloatField()

  def __unicode__(self):
    return self.code

  def get_absolute_url(self):
    return "/courses/building/%s/" % self.code.lower()

class Room(models.Model):
  """ A room in a Building. It optionally may be named. """
  building = models.ForeignKey(Building)
  roomnum = models.CharField(max_length=5)
  name = models.CharField(max_length=80)
  # name is empty string if room doesn't have special name
  # (e.g. Wu and Chen Auditorium), don't bother putting in "LEVH 101"

  class Meta:
    """ To hold uniqueness constraint """
    unique_together = (("building", "roomnum"),)
  
  def __unicode__(self):
    if self.name != "":
      return self.name
    else:
      return "%s %s" % (self.building, self.roomnum)
    # TODO: change to spaces to hyphens, for consistency w/ courses?

class MeetingTime(models.Model):
  """ A day/time/location that a Section meets. """
  section = models.ForeignKey(Section)
  type = models.CharField(max_length=3)
  day = models.CharField(max_length=1)
  # the time hh:mm is formatted as decimal hhmm, i.e. h*100 + m
  start = models.IntegerField() 
  end = models.IntegerField()
  room = models.ForeignKey(Room)

  def __unicode__(self):
    return "%s %s - %s @ %s" % (self.day, self.start, self.end, self.room)

class SemesterDepartment:
  """ A (semester, department) pair. Not a model, but treated like one
  for JSON generation purposes. """
  def __init__(self, semester, department):
    self.semester = semester
    self.department = department

  def __unicode__(self):
    return unicode((self.semester, self.department))

  def get_absolute_url(self):
    return semdept_url(self.semester.code(), self.department.code().lower())
