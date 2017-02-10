import json
import datetime
from collections import defaultdict

from utils import current_semester
from json_helpers import JSON
import sandbox_config
from models import *
from django.http import HttpResponse
from links import *
import dispatcher
from dispatcher import API404, dead_end

DOCS_URL = 'http://pennlabs.org/console/docs.html'
DOCS_HTML = "<a href='%s'>%s</a>" % (DOCS_URL, DOCS_URL)


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

  #don't include course histories that are only offered this semester
  old_course_history_ids = [x[0] for x in Course.objects \
    .filter(semester__lt=current_semester()) \
    .select_related('history') \
    .values_list('history') \
    .distinct()]

  hists = CourseHistory.objects.filter(id__in=old_course_history_ids)
  course_histories = [h.toShortJSON(name_override=hist_to_name[h.id],
                                    aliases_override=hist_to_aliases[h.id])
                      for h in hists]

  # twice to get some crosslistings not caught in the first pass
  dict_histories = remove_duplicates(remove_duplicates(course_histories))
  return JSON({RSRCS: dict_histories})

def remove_duplicates(course_histories):
  course_histories.sort(key=lambda x: -len(x['aliases']))
  dict_histories = []
  for history in course_histories:
    found = False
    for i, old_history in enumerate(dict_histories):
      if not set(history['aliases']).isdisjoint(old_history['aliases']):
        dict_histories[i] = max(history, old_history, key=lambda x: len(x['aliases']))
        dict_histories[i]['aliases'] = list(set(history['aliases']) | set(old_history['aliases']))
        found = True
        break
    if not found:
      dict_histories.append(history)

  return dict_histories

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
  return dispatcher.redirect(coursehistory_url(course.history_id), request)

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
  return dispatcher.redirect(course_url(courseid), request, path)

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
  return dispatcher.redirect(section_url(courseid, sectionnum), request, path)

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
  
  return dispatcher.redirect(coursehistory_url(latest_alias.course.history_id),
                  request, path)

def alias_misc(request, path, (alias,)):
  return HttpResponse('"%s" is not a valid query.' % alias)

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
  return JSON("Welcome to the Penn Labs PCR API. For docs, see %s."
              % DOCS_HTML)
