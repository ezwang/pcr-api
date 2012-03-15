from models import *
from Semester import *
from links import *
import json
import datetime
import sandbox_config
from collections import defaultdict
from django.http import HttpResponse, HttpResponseRedirect
from json_helpers import JSON

DOCS_URL = 'http://www.pennapps.com/kevinsu/pcr_documentation.html'
DOCS_HTML = "<a href='%s'> %s </a>" % (DOCS_URL, DOCS_URL)

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

  # Note: Some courses have no aliases (probably an import script bug).
  # This function will not see those courses (we don't really want to anyway),
  # so we have hist_to_name default to "" (if it defaulted to None, then
  # name_override would not happen and it would fetch their real names and that
  # would be slow)
  hist_to_aliases = defaultdict(set)
  hist_to_name = defaultdict(lambda: "")
  for e in query_results:
    hist_to_aliases[e['course__history']].add((e['department__code'], e['coursenum']))
    hist_to_name[e['course__history']] = (e['course__name'])

  #don't inclue course histories that are only offered this semester
  old_course_history_ids = [x[0] for x in Course.objects \
    .filter(semester__lt=current_semester()) \
    .select_related('history') \
    .values_list('history') \
    .distinct()]

  hists = CourseHistory.objects.filter(id__in=old_course_history_ids)
  course_histories = [h.toShortJSON(name_override=hist_to_name[h.id],
                                    aliases_override=hist_to_aliases[h.id])
                      for h in hists]

  return JSON({RSRCS: course_histories})

@dead_end
def semesters(request, path, _):
  semester_list = (semesterFromID(d['semester']) for d in \
    Course.objects.values('semester').order_by('semester').distinct())
  return JSON({RSRCS: [s.toShortJSON() for s in semester_list]})

@dead_end
def semester_main(request, path, (semester_code,)):
  return JSON(semesterFromCode(semester_code).toJSON())

@dead_end
def semester_dept(request, path, (semester_code, dept_code,)):
  dept_code = dept_code.upper()
  d = Department.objects.get(code=dept_code)
  dept = SemesterDepartment(semesterFromCode(semester_code), d)
  return JSON(dept.toJSON())

@dead_end
def instructors(request, path, _):
  if not request.consumer.access_pcr:
    # This method is only available to those with review data access.
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

  def make_instructor_json(i):
    json = i.toShortJSON()
    json[DEPARTMENT_TOKEN] = instructor_to_depts(i)
    return json

  #3. get and aggregate all course alias data no 'this semester only' prof, please
  return JSON({RSRCS: [
    make_instructor_json(i) \
    for i in Instructor.objects.all() if i.id in prof_to_courses
  ]})

@dead_end
def instructor_main(request, path, (instructor_id,)):
  db_id = int(instructor_id.split("-")[0])
  c = Instructor.objects.get(id=db_id)
  return JSON(c.toJSON(extra=['sections', 'reviews']))

@dead_end
def instructor_sections(request, path, (instructor_id,)):
  db_id = int(instructor_id.split("-")[0])
  sections = Instructor.objects.get(id=db_id).section_set.all() 

  return JSON({RSRCS: [s.toJSON() for s in sections]})

@dead_end
def instructor_reviews(request, path, (instructor_id,)):
  db_id = int(instructor_id.split("-")[0])
  sections = Instructor.objects.get(id=db_id).section_set.all() 
  reviews = sum([list(s.review_set.all()) for s in sections], [])
   
  return JSON({RSRCS: [r.toJSON() for r in reviews]})

@dead_end
def coursehistory_main(request, path, (histid,)):
  hist = CourseHistory.objects.get(id=histid)
  return JSON(hist.toJSON())

@dead_end
def coursehistory_reviews(request, path, (histid,)):
  reviews = Review.objects.filter(section__course__history__id=histid)
  return JSON({RSRCS: [r.toJSON() for r in reviews]})

@dead_end
def course_main(request, path, (courseid,)):
  course = Course.objects.get(id=int(courseid))
  return JSON(course.toJSON())

@dead_end
def course_reviews(request, path, (courseid,)):
  sections = Course.objects.get(id=courseid).section_set.all()
  reviews = sum([list(s.review_set.all()) for s in sections],[])
  return JSON({RSRCS: [r.toJSON() for r in reviews]})

@dead_end
def course_sections(request, path, (courseid,)):
  # Return full JSON.
  api_sections = list(Course(courseid).section_set.all())
  return JSON({RSRCS: [s.toJSON() for s in api_sections]})

def course_history(request, path, (courseid,)):
  course = Course.objects.get(id=int(courseid))
  return redirect(coursehistory_url(course.history_id), request)

@dead_end
def section_main(request, path, (courseid, sectionnum)):
  try:  
    section = Section.objects.get(sectionnum=sectionnum, course=courseid)
    return JSON(section.toJSON())
  except Section.DoesNotExist:
    raise API404("Section %03d of course %d not found" % (sectionnum, courseid))


@dead_end
def section_reviews(request, path, (courseid, sectionnum)):
  try:
    section = Section.objects.get(sectionnum=sectionnum, course=courseid)
    return JSON({RSRCS: [r.toJSON() for r in section.review_set.all()]})
  except Section.DoesNotExist:
    raise API404("Section %03d of course %d not found" % (sectionnum, courseid))

@dead_end
def review_main(request, path, (courseid, sectionnum, instructor_id)):
  try:
    db_instructor_id = int(instructor_id.split("-")[0])
    db_review = Review.objects.get(section__sectionnum=sectionnum,
                                   section__course=courseid,
                                   instructor__id=db_instructor_id)
    review = db_review
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
  depts = Department.objects.order_by('code').all()
  return JSON({RSRCS: [d.toShortJSON() for d in depts] })

@dead_end
def dept_main(request, path, (dept_code,)):
  dept_code = dept_code.upper()
  d = Department.objects.get(code=dept_code)
  return JSON(d.toJSON())

@dead_end
def dept_reviews(request, path, (dept_code,)):
  reviews = Review.objects.filter(section__course__alias__department__code=dept_code)
  return JSON({RSRCS: [r.toJSON() for r in reviews]})


@dead_end
def buildings(request, path, _):
  #TODO
  return JSON({RSRCS: [Building(code="LEVH", name="Levine Hall").toJSON()]})

@dead_end
def building_main(request, path, (code,)):
  code = code.upper()
  if code != "LEVH":
    raise API404("Building %s not found" % code)

  return JSON(Building(code="LEVH", name="Levine Hall").toJSON())

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
