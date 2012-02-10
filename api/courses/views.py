from models import *
from Semester import *
from APIObjects import *
from links import *
import json
import datetime
import sandbox_config
from collections import defaultdict
from django.http import HttpResponse, HttpResponseRedirect
from json_helpers import JSON

DOCS_URL = 'http://www.pennapps.com/kevinsu/pcr_documentation.html'
DOCS_HTML = "<a href='%s'> %s </a>" % (DOCS_URL, DOCS_URL)

RSRCS = 'values'
API_ROOT = '/' + sandbox_config.DISPLAY_NAME

def redirect(path, request, extras=[]):
  query = '?' + request.GET.urlencode() if request.GET else ''
  fullpath = "%s/%s/%s%s" % (API_ROOT, path, '/'.join(extras), query)
  return HttpResponseRedirect(fullpath)

def dead_end(fn):
  def wrapped(request, path, variables):
    if path:
      return dispatch_404(message="Past dead end!")(request, path, variables)
    else:
      return fn(request, path, variables)
  return wrapped

def dispatch_404(message=None, perhaps=None):
  def view(request, path, _):
    raise API404(message)
  return view

def dispatch_dead_end(str):
  @dead_end
  def view(request, path, _):
    return HttpResponse("Useful information! " + str)
  return view

def optlist_map(func, l):
  return None if l is None else [func(x) for x in l]

def list_json(l):
  return None if l is None else l if type(l) is list else list(l)

def json_output(d):
  return d # dict((k, v) for (k, v) in d.iteritems() if v is not None)

def apiify_course_history(history, courses=None, aliases=None, name=None):
  """when you absolutely, positively, need this shit to work quickly"""
  result = APICourseHistory(history.id)
  result.courses = courses 
  result.aliases = aliases
  result.name = name 
  return result

def apiify_course_history_slow(history_uid):
  """used by pages that only need a few course histories"""
  history = CourseHistory.objects.get(id=history_uid)

  result = APICourseHistory(history_uid)
  result.courses = [apiify_course(c) for c in history.course_set.all()] 
  result.aliases = set(alias.course_code for alias in history.aliases)
  result.name = list(history.course_set.all())[-1].name
  return result

class APICourseHistory:
  def __init__(self, uid):
    self.uid = uid # Integer id (unique to course histories)
    self.courses = [] #APICourse Objects
    self.aliases = [] #(dept, num) tuple pairs
    self.name = None

  def path(self):
    return coursehistory_url(self.uid)

  def basic_info(self):
    return {
      'id': self.uid,
      'name': self.name,
      'path': self.path(),
      'aliases': ["%s-%03d" % (code[0], code[1]) for code in self.aliases]
    }

  def toShortJSON(self):
    return json_output(self.basic_info())

  def toJSON(self):
    response = self.basic_info()
    response[COURSE_TOKEN] = [c.toShortJSON() for c in self.courses]
    response[REVIEW_TOKEN] = {'path': self.path() + '/' + REVIEW_TOKEN}
    return json_output(response)

class APISemester:
  def __init__(self, semester_object):
    self.sem = semester_object

  def path(self):
    return semester_url(self.sem.code())

  def basic_info(self):
    return {
      'id': self.sem.code(),
      'name': str(self.sem),
      'year': self.sem.year,
      'seasoncode': self.sem.seasoncodeABC,
      'path': self.path()
    }

  def toShortJSON(self):
    return json_output(self.basic_info())

  def toJSON(self):
    result = self.basic_info()
    def current_sem_depts(depts):
      courses = Course.objects.filter(semester=self.sem).all()
      #Super slow but it gets cached
      good_depts = set(alias.department for course in courses for alias \
        in course.alias_set.all())
      #filter original set based on good list, to preserve ordering
      return [d for d in depts.all() if d in good_depts]

    result[DEPARTMENT_TOKEN] = depts_helper(self.sem.code(), current_sem_depts)
    return json_output(result)

class APICourse:
  def __init__(self, uid):
    self.uid = uid # Integer id (unique to courses)
    self.name = None # String, with the name of the course
    self.aliases = [] # List of (department_code_str, coursenum_int) tuples
    self.description = None # String
    self.credits = None # Float
    self.sections = None # list of APISection objects
    self.history = None # Integer; history ID
    self.semester = None # String

  def path(self):
    return course_url(self.uid)

  def getAliases(self):
    return ["%s-%03d" % x for x in self.aliases]
  
  def basic_info(self):
    return {
      'id': self.uid, 'name': self.name,
      'aliases': self.getAliases(), 'path': self.path(),
      'semester': self.semester
    }

  def toShortJSON(self):
    return json_output(self.basic_info()) 

  def toJSON(self):
    result = self.basic_info()
    path = self.path()
    result.update({
      'credits': self.credits,
      'description': self.description,
      SECTION_TOKEN: {
        'path': path + '/' + SECTION_TOKEN,
        RSRCS: [x.toShortJSON() for x in self.sections],
      },
      REVIEW_TOKEN: {
        'path': path + '/' + REVIEW_TOKEN,
      },
      COURSEHISTORY_TOKEN: {'path': coursehistory_url(self.history)},
    })

    return json_output(result)

  def makeChildSection(self, *args, **kwargs):
    s = APISection(self, *args, **kwargs)
    if self.sections is not None:
      self.sections.append(s)
    return s

def apiify_course(course):
  api_course = APICourse(course.id)  
  #add aliases and sections manually, sadly
  api_course.aliases = [(a.department.code, a.coursenum) 
    for a in course.alias_set.all()
  ]
  api_course.sections = [apiify_section(s, api_course) 
    for s in course.section_set.all()]
  api_course.name = course.name
  api_course.semester = course.semester.code()
  api_course.description = course.description
  api_course.history = course.history_id
  return api_course

def apiify_section(section, course=None):
  #to avoid circular dependencies
  course = course or apiify_course(section.course)
  s = APISection(course, section.sectionnum)
  s.meetingtimes = apiify_meetingtimes(section.meetingtime_set.all())
  s.instructors = [apiify_instructor(i) for i in section.instructors.all()]
  s.reviews = [apiify_review(r, section=s) for r in section.review_set.all()]
  s.name = section.name or course.name
  return s

class APISection:
  def __init__(self, course, sectionnum):
    self.course = course # APICourse object
    self.name = None # String, with the name of the section
    self.sectionnum = sectionnum # Integer (e.g. 1 for 001)
    # Doesn't actually suck this much.  See apiify_section
    self.group = None # Integer
    self.instructors = None # List of APIInstructors
    self.meetingtimes = None # List of meetingtime_json outputs
    self.reviews = None # List of APIReview Objects

  @property
  def id(self):
    return "%s-%03d" % (self.course.uid, self.sectionnum)

  def path(self):
    return section_url(self.course.uid, self.sectionnum)

  def getAliases(self):
    return ["%s-%03d" % (alias, self.sectionnum)
            for alias in self.course.getAliases()]
    
  def toShortJSON(self):
    return json_output({
      'id': self.id, 
      'aliases': self.getAliases(),
      'name': self.name,
      'sectionnum': "%03d" % self.sectionnum, 
      'path': self.path(),
      })

  def toJSON(self):
    path = self.path()
    return json_output({
      'id': "%s-%03d" % (self.course.uid, self.sectionnum),
      'aliases': self.getAliases(),
      'group': self.group, 
      'name': self.name,
      'sectionnum': "%03d" % self.sectionnum, 
      INSTRUCTOR_TOKEN: optlist_map(lambda i: i.toShortJSON(), self.instructors),
      'meetingtimes': list_json(self.meetingtimes), 
      'path': path,
      COURSE_TOKEN: self.course.toShortJSON(),
      REVIEW_TOKEN: {
        'path': '%s/%s' % (path, REVIEW_TOKEN),
         RSRCS: [x.toShortJSON() for x in self.reviews]
      },
    })

class APIInstructor:
  def __init__(self, pennkey, name, depts=None, sections=None, reviews=None):
    self.pennkey = pennkey
    self.name = name
    self.depts = depts 
    self.sections = sections
    self.reviews = reviews

  def path(self):
    return instructor_url(pennkey)
  
  def basic_info(self):
    result = {
      'id': self.pennkey,
      'name': self.name,
      'path': self.path(),
    }
    if self.depts:
      result[DEPARTMENT_TOKEN] = self.depts
    return result

  def toShortJSON(self):
    return json_output(self.basic_info())

  def toJSON(self):
    result = self.basic_info()
    result[SECTION_TOKEN] = {'path': "%s/%s" % (self.path(), SECTION_TOKEN)}
    if self.sections:
      result[SECTION_TOKEN][RSRCS] = [x.toShortJSON() for x in self.sections]
    result[REVIEW_TOKEN] = {'path': "%s/%s" % (self.path(), REVIEW_TOKEN)}
    if self.reviews:
      result[REVIEW_TOKEN][RSRCS] = [x.toShortJSON() for x in self.reviews]
    return result

def apiify_meetingtimes(meetingtimeset):
  #TODO for after 1.0
  return [meetingtime_json(m.start, m.end, m.day, m.type, None, None, None) \
    for m in meetingtimeset]

def meetingtime_json(start, end, day, type,
                     room_building, room_number, room_name):
  return {
    'start': start, # String (e.g. "13:30")
    'end': end, # String (e.g. "15:00")
    'day': day, # String (e.g. "R" for thursday)
    'type': type, # String (e.g. "LEC")
#TODO FOR AFTER 1.0
#    'room': {'building': room_building, # building_json output
#             'id': '%s %s' % (room_building['id'], room_number),
#             'name': room_name, # String, or None if has no name.
#             'number': room_number, # String (e.g. "321")
#             }
  }

def building_json(code, name, lat=13.371337, lng=90.01):
  return json_output({
    'id': code,
    'name': name,
    'latitude': lat,
    'longitude': lng,
    'path': building_url(code)
    })

class APIDepartment:
  def __init__(self, code, name, semester=None):
    self.code = code # String
    self.name = name # String
    self.hists = None # List of APICourseHistories
    self.courses = None # List of APICourses, if semester specific
    self.semester = semester #if True, add to path

  def path(self):
    if self.semester:
      return semdept_url(self.semester, self.code)
    else:
      return department_url(self.code)
  
  def base_info(self):
    return {
      'id': self.code,
      'name': self.name,
      'path': self.path(),
    }
  def toShortJSON(self):
    return json_output(self.base_info())

  def toJSON(self):
    result = self.base_info() 
    if self.hists:
      result[COURSEHISTORY_TOKEN] = [h.toShortJSON() for h in self.hists]
      #Post 1.0/nice to have, reviews for semester-department.
      result[REVIEW_TOKEN] = {'path': "%s/%s" % (self.path(), REVIEW_TOKEN)},
    elif self.courses:
      result[COURSE_TOKEN] = [c.toShortJSON() for c in self.courses]

    return result

def apiify_review(review, section=None):
  bits = review.reviewbit_set.all()
  ratings = dict((bit.field, "%1.2f" % bit.score) for bit in bits)
  instructor = apiify_instructor(review.instructor) if review.instructor_id else None
  section = section or apiify_section(review.section)

  return APIReview(section, ratings, instructor,
                   review.forms_returned, review.forms_produced, review.comments)

class APIReview:
  def __init__(self, section, ratings, instructor, forms_returned, forms_produced, comments):
    self.section = section # APISection object
    self.instructor = instructor #APIInstructor object 
    self.instructor_JSON = instructor.toShortJSON() if instructor else None
    self.ratings = ratings
    self.forms_returned = forms_returned
    self.forms_produced = forms_produced
    self.comments = comments

  def basic_info(self):
    return {
      'id': '%s-%s' % (self.section.id, self.instructor.pennkey),
      'section': self.section.toShortJSON(),
      'instructor': self.instructor_JSON, # to deal with possible none, hack
      'path': review_url(self.section.course.uid, self.section.sectionnum,
                         self.instructor.pennkey if self.instructor else "99999-JAIME-MUNDO")
    }

  def toShortJSON(self):
    return json_output(self.basic_info())

  def toJSON(self):
    result = self.basic_info()
    result.update({
      'num_reviewers': self.forms_returned,
      'num_students': self.forms_produced,
      'ratings': self.ratings,
      'comments': self.comments,
    })

    return json_output(result)

# FNAR 337 Advanced Orange (Jaime Mundo)
# Explore the majesty of the color Orange in its natural habitat,
# and ridicule other, uglier colors, such as Chartreuse (eww).

# MGMT 099 The Art of Delegating (Alexey Komissarouky)
# The Kemisserouh delegates teaching duties to you. Independent study.

class API404(Exception):
  def __init__(self, message=None, perhaps=None):
    self.message = message
    self.perhaps = perhaps


@dead_end
def course_histories(request, path, _):
  if not request.consumer.access_secret:
    # This method is for the PCR site only.
    raise API404("This is not the database dump you are looking for.")

  #1. get and aggregate all course alias data
  alias_fields = ['coursenum', 'department__code', 'course__history', 'course__name']
  query_results = Alias.objects.select_related(*alias_fields).values(*alias_fields)

  hist_to_aliases = defaultdict(set)
  hist_to_name = defaultdict(lambda: None)
  for e in query_results:
    hist_to_aliases[e['course__history']].add((e['department__code'], e['coursenum']))
    hist_to_name[e['course__history']] = (e['course__name'])

  #don't inclue course histories that are only offered this semester
  old_course_history_ids = [x[0] for x in Course.objects \
    .filter(semester__lt=current_semester()) \
    .select_related('history') \
    .values_list('history') \
    .distinct()]

  api_course_histories = [
      apiify_course_history(c, 
        aliases=hist_to_aliases[c.id],
        name=hist_to_name[c.id],
        courses=None
    ) for c in CourseHistory.objects.filter(id__in=old_course_history_ids)]

  course_histories = [c.toShortJSON() for c in api_course_histories]
  return JSON({RSRCS: course_histories})

@dead_end
def semesters(request, path, _):
  semester_list = (semesterFromID(d['semester']) for d in \
    Course.objects.values('semester').order_by('semester').distinct())
  return JSON({RSRCS: [APISemester(s).toShortJSON() for s in semester_list]})

@dead_end
def semester_main(request, path, (semester_code,)):
  return JSON(APISemester(semesterFromCode(semester_code)).toJSON())

@dead_end
def semester_dept(request, path, (semester_code, dept_code,)):
  dept_code = dept_code.upper()
  d = Department.objects.get(code=dept_code)
  dept = APIDepartment(d.code, d.name, semester_code)

  courses = Course.objects.filter( \
    alias__department = d, \
    semester = semesterFromCode(semester_code))

  dept.courses = [apiify_course(c) for c in courses]
  return JSON(dept.toJSON())

def apiify_instructor(instructor, depts=None, extra=[]):
  sections = [apiify_section(s) for s in instructor.section_set.all()] \
    if 'sections' in extra else None
  reviews = [apiify_review(r) for r in instructor.review_set.all()] \
    if 'reviews' in extra else None
  return APIInstructor(instructor.temp_id, instructor.name, depts, sections, reviews)

@dead_end
def instructors(request, path, _):
  if not request.consumer.access_secret:
    # This method is for the PCR site only.
    raise API404("This is not the database dump you are looking for.")

  #get departments for every instructor
  #1.  Professor id --> set of courses they teach
  prof_to_courses_fields = ['instructor_id', 'section__course_id']
  #thing in the current semester (IE, profs only teaching this semester aren't useful)
  prof_to_courses_query = Review.objects.select_related(*prof_to_courses_fields) \
    .values(*prof_to_courses_fields)
  prof_to_courses = defaultdict(set)
  for e in prof_to_courses_query:
    prof_to_courses[e['instructor_id']].add(e['section__course_id'])
    
  #2.  Course id --> set of departments its in
  course_to_depts_fields = ['department__code', 'course_id']
  course_to_depts_query = Alias.objects.select_related(*course_to_depts_fields) \
    .values(*course_to_depts_fields)
  course_to_depts = defaultdict(set)
  for e in course_to_depts_query:
    course_to_depts[e['course_id']].add(e['department__code'])
  
  def instructor_to_depts(i):
    return list(set(dept for course in prof_to_courses[i.id] for dept in course_to_depts[course]))

  #3. get and aggregate all course alias data no 'this semester only' prof, please
  return JSON({RSRCS: [
    apiify_instructor(i, instructor_to_depts(i)).toShortJSON() \
    for i in Instructor.objects.all() if i.id in prof_to_courses
  ]})

@dead_end
def instructor_main(request, path, (instructor_id,)):
  db_id = int(instructor_id.split("-")[0])
  c = apiify_instructor(Instructor.objects.get(id=db_id), extra=['sections', 'reviews'])
  return JSON(c.toJSON())

@dead_end
def instructor_sections(request, path, (instructor_id,)):
  db_id = int(instructor_id.split("-")[0])
  sections = Instructor.objects.get(id=db_id).section_set.all() 

  return JSON({RSRCS: [apiify_section(s).toJSON() for s in sections]})

@dead_end
def instructor_reviews(request, path, (instructor_id,)):
  db_id = int(instructor_id.split("-")[0])
  sections = Instructor.objects.get(id=db_id).section_set.all() 
  reviews = sum([list(s.review_set.all()) for s in sections], [])
   
  return JSON({RSRCS: [apiify_review(r).toJSON() for r in reviews]})

@dead_end
def coursehistory_main(request, path, (histid,)):
  hist = apiify_course_history_slow(histid)
  return JSON(hist.toJSON())

@dead_end
def coursehistory_reviews(request, path, (histid,)):
  reviews = Review.objects.filter(section__course__history__id=histid)
  return JSON({RSRCS: [apiify_review(r).toJSON() for r in reviews]})

@dead_end
def course_main(request, path, (courseid,)):
  course = Course.objects.get(id=int(courseid))
  return JSON(apiify_course(course).toJSON())

@dead_end
def course_reviews(request, path, (courseid,)):
  sections = Course.objects.get(id=courseid).section_set.all()
  reviews = sum([list(s.review_set.all()) for s in sections],[])
  return JSON({RSRCS: [apiify_review(r).toJSON() for r in reviews]})

@dead_end
def course_sections(request, path, (courseid,)):
  # Return full JSON.
  api_sections = [apiify_section(s) for s in Course(courseid).section_set.all()]
  return JSON({RSRCS: [s.toJSON() for s in api_sections]})

def course_history(request, path, (courseid,)):
  course = Course.objects.get(id=int(courseid))
  return redirect(coursehistory_url(course.history_id), request)

@dead_end
def section_main(request, path, (courseid, sectionnum)):
  try:  
    section = Section.objects.get(sectionnum=sectionnum, course=courseid)
    return JSON(apiify_section(section).toJSON())
  except Section.DoesNotExist:
    raise API404("Section %03d of course %d not found" % (sectionnum, courseid))


@dead_end
def section_reviews(request, path, (courseid, sectionnum)):
  try:
    section = Section.objects.get(sectionnum=sectionnum, course=courseid)
    return JSON({RSRCS: [apiify_review(r).toJSON() for r in section.review_set.all()]})
  except Section.DoesNotExist:
    raise API404("Section %03d of course %d not found" % (sectionnum, courseid))

@dead_end
def review_main(request, path, (courseid, sectionnum, instructor_id)):
  try:
    db_instructor_id = int(instructor_id.split("-")[0])
    db_review = Review.objects.get(section__sectionnum=sectionnum,
                                   section__course=courseid,
                                   instructor__id=db_instructor_id)
    review = apiify_review(db_review)
    return JSON(review.toJSON())
  except Review.DoesNotExist:
    raise API404("Review for %s for section %03d of course %d not found" %
                 (instructor_id, sectionnum, courseid))

def alias_course(request, path, (coursealias,)):
  try:
    semester_code, dept_code, coursenum_str = coursealias.upper().split('-')
    semester = semesterFromCode(semester_code)
    coursenum = int(coursenum_str)
  except:
    raise API404("Course alias %s not in correct format: YYYYS-DEPT-100." %
                 coursealias)

  courseid = Alias.objects.get(semester=semester,
                               department=dept_code,
                               coursenum=coursenum).course_id
  return redirect(course_url(courseid), request, path)

def alias_section(request, path, (sectionalias,)):
  try:
    semester_code, dept_code, coursenum_str, sectionnum_str = (
      sectionalias.upper().split('-'))
    semester = semesterFromCode(semester_code)
    coursenum = int(coursenum_str)
    sectionnum = int(sectionnum_str)
  except:
    raise API404("Section alias %s not in correct format: YYYYS-DEPT-100-001."
                 % sectionalias)

  courseid = Alias.objects.get(semester=semester,
                               department=dept_code,
                               coursenum=coursenum).course_id
  return redirect(section_url(courseid, sectionnum), request, path)

def alias_currentsemester(request, path, _):
  return HttpResponse("(redirect) current semester, extra %s" % path)

def alias_coursehistory(request, path, (historyalias,)):
  try:
    dept_code, coursenum_str = historyalias.upper().split('-')
    coursenum = int(coursenum_str)
  except:
    raise API404("Course alias %s not in correct format: DEPT-100." %
                 historyalias)

  latest_alias = Alias.objects.filter(
    department=dept_code, coursenum=coursenum).order_by('-semester')[0]
  
  return redirect(coursehistory_url(latest_alias.course.history_id),
                  request, path)

def alias_misc(request, path, (alias,)):
  return HttpResponse("I have no idea how you got here.  This isn't really a 'thing'." + alias)

@dead_end
def depts(request, path, _):
  return JSON({RSRCS: depts_helper()})

def depts_helper(semester = None, *condition_funcs):
  filt_depts = reduce(lambda depts, filt: filt(depts), condition_funcs, Department.objects.order_by('code').all())
  return [APIDepartment(d.code, d.name, semester).toShortJSON() for d in filt_depts] 

@dead_end
def dept_main(request, path, (dept_code,)):
  dept_code = dept_code.upper()
  d = Department.objects.get(code=dept_code)
  hists = CourseHistory.objects.filter(course__alias__department=d)
  
  dept = APIDepartment(d.code, d.name)
  #using set to remove duplicate course histories 
  dept.hists = [apiify_course_history_slow(h.id) for h in set(hists)]
  return JSON(dept.toJSON())

@dead_end
def dept_reviews(request, path, (dept_code,)):
  reviews = Review.objects.filter(section__course__alias__department__code=dept_code)
  return JSON({RSRCS: [apiify_review(r).toJSON() for r in reviews]})


@dead_end
def buildings(request, path, _):
  #TODO
  return JSON({RSRCS: [building_json("LEVH", "Levine Hall")]})

@dead_end
def building_main(request, path, (code,)):
  code = code.upper()
  if code != "LEVH":
    raise API404("Building %s not found" % code)

  return JSON(building_json("LEVH", "Levine Hall"))

@dead_end
def index(request, path, _):
  return JSON("Welcome to the PennApps Courses API. For documentation, see %s."
              % DOCS_HTML)

def dispatcher(dispatchers):
  d_str = dispatchers.get("/str")
  d_int = dispatchers.get("/int")
  def dispatch_func(request, path, variables=[]):
    if not path:
      return dispatchers[''](request, [], variables)
    first, rest = path[0], path[1:]
    if first in dispatchers:
      return dispatchers[first](request, rest, variables)
    elif d_int and all(x in "0123456789" for x in first):
      return d_int(request, rest, variables + [int(first)])
    elif d_str:
      return d_str(request, rest, variables + [first])
    elif d_int:
      return dispatch_404("i can has digits")(request, path, variables)
    else:
      return dispatch_404("what is this i dont even")(request, path, variables)
  return dispatch_func

dispatch_root = {
  '': index,
  INSTRUCTOR_TOKEN: {'': instructors,
                 '/str': {'': instructor_main,
                          SECTION_TOKEN: instructor_sections,
                          REVIEW_TOKEN: instructor_reviews}},
  COURSEHISTORY_TOKEN: {'': course_histories,
                    '/int': {'': coursehistory_main,
                             REVIEW_TOKEN: coursehistory_reviews},
                    '/str': alias_coursehistory},
  DEPARTMENT_TOKEN: {'': depts,
           '/str': {'': dept_main,
                    REVIEW_TOKEN: dept_reviews}},
  COURSE_TOKEN: {'': dispatch_404("sorry, no global course list"),
             '/int': {'': course_main,
                      REVIEW_TOKEN: course_reviews,
                      SECTION_TOKEN: {'': course_sections,
                                  '/int': {'': section_main,
                                           REVIEW_TOKEN: {'': section_reviews,
                                                      '/str': review_main}}},
                      COURSEHISTORY_TOKEN: course_history},
             '/str': alias_course},
  SECTION_TOKEN: {'': dispatch_404("sorry, no global sections list"),
              '/str': alias_section},
  SEMESTER_TOKEN: {'': semesters,
               '/str': {'': semester_main,
                        '/str': semester_dept}},
  BUILDING_TOKEN: {'': buildings,
               '/str': building_main},
  '/str': alias_misc}

def annotate_dictionary(d, fn):
  if type(d) == dict:
    return fn(dict((k, annotate_dictionary(v, fn)) for k,v in d.iteritems()))
  else:
    return d

dispatch_root = annotate_dictionary(dispatch_root, dispatcher)

def dispatch(request, url):
  try:
    if not request.consumer.access_pcr and "review" in url:
      raise API404("This API token does not have access to review data.")
    return dispatch_root(request, [x for x in url.split('/') if x])
  except API404 as e:
    obj = {
      'help': "See %s for API documentation." % DOCS_HTML,
      'error': 'Error 404. The resource could not be found: ' + request.path}
    if e.perhaps:
      obj['perhaps_you_meant'] = e.perhaps # and perhaps not
    if e.message:
      obj['message'] = e.message
    return JSON(obj, valid=False, httpstatus=404)
