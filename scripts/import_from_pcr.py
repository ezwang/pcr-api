'''Imports course and review information from an existing database and updates the database appropriately.'''
import MySQLdb as db
#hack to get scripts to run w/ django
import sys, os
from collections import defaultdict
import pickle
sys.path.append("..")
sys.path.append("../api")
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from courses.models import *
from string import capwords
from itertools import izip, product
from collections import defaultdict
from sandbox_config import *

"""
Instructions:
Run with a given semester (IE, "2009a") to import all of that semester's data
from the PCR database (location configured below) into the Django models
""" 

conn = db.connect(db=IMPORT_DATABASE_NAME, 
                  user=IMPORT_DATABASE_USER, 
                  passwd=IMPORT_DATABASE_PWD)

def run_query(query_str, args=None):
  c = conn.cursor()
  c.execute(query_str, args)
  return c.fetchall()

def select(fields, table, conditions=None):
  query = "SELECT %s FROM %s" % (str.join(', ', fields), table)
  if conditions:
    query += " WHERE %s" % str.join(' AND ', conditions)
  return run_query(query)

def sync_depts():
  """syncs departments and returns a deptId -> API Dept object mapping"""
  depts = run_query("""SELECT dept_ID, dept_code, dept_title 
                         FROM coursereview_tbldepts""")
  # pull departments from api one by one, create if they dont exist.
  deptID_to_model = {}
  for dept_id, dept_code, dept_title in depts:
    dept, created = Department.objects.get_or_create(code=dept_code.strip())
    #update name
    dept.name = capwords(dept_title)
    dept.save() #not efficient (IE, N+1 queries)
    #add to answer
    deptID_to_model[dept_id] = dept
  return deptID_to_model

LDAP_TO_ENGLISH = {"telephoneNumber"     :"phone",
                   "mail"                :"mail",
                   "givenName"           :"first_name",
                   "sn"                  :"last_name",
                   "uid"                 :"pennkey",
                   "title"               :"title",
                   "eduPersonAffiliation":"affiliation",
                   "displayname"         :"display_name"
                  }
VALID_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"
LDAP_DIR = "ldap_out"

def ldap_file_name(prefix): return "%s/%s.txt" % (LDAP_DIR, prefix)

def write_ldap_file(prefix):
  """make a cmd-line call to get all faculty starting w/ prefix into file"""
  file_name = ldap_file_name(prefix)
  print "### Querying LDAP for %s" % (file_name,)
  output = os.system("""ldapsearch -h directory.upenn.edu -b """ + 
            """"ou=People, dc=upenn, dc=edu" -x -LLL "(&""" +
            # NOTE: commenting out faculty affiliation requirement because
            # Courses can be taught by staff/students/etc  
            #"""(eduPersonAffiliation=fac""" +
            """(uid=%s*))" > %s"""
              % (prefix, file_name)
           )
  if output == 1024:
    #too many results, split into multiple names
    os.system("rm " + file_name)
    for new_prefix in (prefix + c for c in VALID_CHARS):
      write_ldap_file(new_prefix)
  elif output > 0:
    print "Unknown error when querying LDAP for prefix: " + prefix
  else:
    print "Prefix %s downloaded from LDAP" % (prefix,)

def download_ldap_data(): 
  """download every faculty member from LDAP. Warning: takes a while"""
  print "Are you sure you want to delete all LDAP input? Comment next if so"
  return
  os.system("rm -f %s/*" % (LDAP_DIR,)) #kill the old stuff

def parse_ldap_file(file_name, entries):
  """ parse an LDAP results file into a dictionary
      entries must be a defaultdict(list)
  """
  print "### Loading results from %s" % (file_name,)
  f = open(os.path.join(LDAP_DIR,file_name))
  entry = {}
  for line in f:
    line = line.strip()
    if line != "":
      if ":" in line:
        k, v = map(lambda x: x.strip(), line.split(":", 1))
        if k in LDAP_TO_ENGLISH:
          entry[LDAP_TO_ENGLISH[k]] = v
    else:
      entries[(entry["first_name"], entry["last_name"])].append(entry)
      entry = {}

  return entries

def get_ldap_data():
  """return a dict from (First, Last) -> [users with that info]"""
  print "##### Parsing LDAP Data into useful format #####"
  entries = defaultdict(list)
  
  for ldap_file in os.listdir(LDAP_DIR):
    entries = parse_ldap_file(ldap_file, entries)
  
  return entries 

def get_instructors():
  fields = ('lecturer_ID', 'first_name', 'last_name')
  instructors_raw = select(fields, 'coursereview_tbllecturers')
  for oldpcr_id, first_name, last_name in instructors_raw:
    yield get_or_create_instructor(oldpcr_id, first_name, last_name)

def import_instructors():
  instructor_map = {}
  for instructor in get_instructors():
    instructor_map[instructor.oldpcr_id] = instructor
  return instructor_map

def get_or_create_instructor(oldpcr_id, first_name, last_name):
  instructor, _  = Instructor.objects.get_or_create(
    oldpcr_id = oldpcr_id,
    first_name = first_name,
    last_name = last_name
  )
  return instructor

def import_courses(depts):
  '''Import courses from the old pcr database and turn them into Django objects.
  
  Returns a dictionary containing all courses, with keys id, year, and semester.
  (To reduce the number of database look-ups.)
  '''
  courses_final = {}
  TOY_WHERE_CLAUSE = '1'#"c.course_ID = 13166"
  courses_raw = run_query("""SELECT course_ID, dept_ID, course_code,
    course_description, crosslist_ID FROM coursereview_tblcourses as c WHERE %s ORDER BY course_ID ASC""" % (TOY_WHERE_CLAUSE,))
  # also pull every course that this thing has ever been taught,
  course_history_raw = run_query("""SELECT c.course_ID, s.year, s.semester, s.section_title FROM coursereview_tblsections as s, `coursereview_tblcourses` as c WHERE %s AND c.course_ID = s.course_ID GROUP BY s.course_ID, s.year, s.semester ORDER BY s.course_ID""" % (TOY_WHERE_CLAUSE,))
  course_names = {}

  sems_taught = defaultdict(list)
  for course_id, year, semester, name in course_history_raw:
    sems_taught[course_id].append(Semester(year, semester))
    course_names[course_id] = name

  # then, add each course the the appropriate course-history object
  course_crosslist_aliases = {} 
  for course_id, _, _, _, crosslist_id in courses_raw:
    #crosslist id = canonical id for that course in old system, or 0 if none
    course_crosslist_aliases[course_id] = crosslist_id or course_id

  course_histories = {}
  #create a course for each semester it was taught in
  for course_id, dept_id, course_num, course_desc, _ in courses_raw:
    canonical_course_id = course_crosslist_aliases[course_id]

    courses = set(
      [get_or_create_course(course_id, course_num, course_desc, 
        canonical_course_id, depts[dept_id], semester, course_names[course_id]) 
      for semester in sems_taught[course_id]]
    )

    history = get_or_create_course_history(courses, course_id)
    courses_final[course_id] = {}
    for course in courses:
      courses_final[course_id][course.semester.year, course.semester.seasoncodeABC] = course
      course.history = get_or_create_course_history(courses, course_id) 
      course.save()
     
  return courses_final

def get_or_create_course(id, num, desc, canonical_id, dept, semester, name):
  course, _ = Course.objects.get_or_create(
    oldpcr_id  = canonical_id,
    semester   = semester,
    defaults   = { 
      #back-up name (in case no sections) is CIS 520-style
      "name"        : name or "%s %d" % (dept.code, int(num)),
      #not setting credits: get that from Registrar instead
      "description" : desc,
      #setting course history afterwards
      "history"     : None
    }
  ) 

  # even if the course already exists, we want to make sure we've aliased it  
  course_alias, _ = Alias.objects.get_or_create(
    oldpcr_id  = id, 
    semester   = semester,
    department = dept,
    coursenum  = num,
    course     = course
  )


  return course

def get_or_create_course_history(course_history_courses, course_id): 
  histories = [h.history for h in course_history_courses if h.history]
  uniques = len(set(histories))
  if uniques > 1:
    raise "Course %d is already tied to multiple course_histories!" % (course_id,)
  elif uniques == 1:
    return histories[0]
  else:
    return CourseHistory.objects.create(notes = "Created from PCR ID:"+str(course_id))

def get_sections(courses_final, instructors, year, semester):
  fields = ('year', 'semester', 'course_ID', 'section_code', 'lecturer_ID', 'section_ID', 'section_title')
  conditions = ('year="%s"' % year, 'semester="%s"' % semester)
  sections_raw = select(fields, 'coursereview_tblsections', conditions)
  for year, semester, course_id, section_num, lecturer_id, oldpcr_id, name in sections_raw:
    yield get_or_create_section(courses_final[course_id][year, semester],
      section_num, instructors, lecturer_id, oldpcr_id, name)
    
def import_sections(courses_final, instructors, year, semester):
  '''Import the sections from old pcr, updating and creating Django Section models.
  
  A Section has a course, sectionnum, instructors, group, sectiontype, and 
  oldpcr_id.

  *Section type values:
  CLN clinic
  DIS dissertation
  IND indepedent study
  LAB lab
  LEC lecture
  MST masters thesis
  REC recitation
  SEM seminar
  SRT senior thesis
  STU studio
  '''
  section_map = {}
  for section in get_sections(courses_final, instructors, year, semester):
    section_map[section.course, float(section.sectionnum)] = section
  return section_map

def get_comments(course_map, instructor_map, year, semester):
  fields = ['review', 'lecturer_ID', 'course_ID']
  conditions = ['year="%s"' % year, 'semester="%s"' % str(semester).upper()]
  comments_raw = select(fields, 'coursereview_tbllecturerreviews', conditions)
  comments_map = {}
  for review, lecturer_id, course_id in comments_raw:
    if review is not None:
      review = review.decode('cp1252', "ignore").encode('utf-8', "ignore")
    comments_map[course_map[course_id][year, str(semester).upper()], instructor_map[lecturer_id]] = review
  return comments_map

def get_or_create_section(course, section_num, instructors, lecturer_id, oldpcr_id, name): 
  section, created = Section.objects.get_or_create(
      course = course,
      sectionnum = section_num,
      defaults = {
        "oldpcr_id": oldpcr_id,
        "group":  None,
        "sectiontype": None,
        "name": name or ""
      }
    )
  try:
    instructor = instructors[lecturer_id]
  except:
    print "Found unrecognized instructor id: %s" % lecturer_id
    instructor = get_or_create_instructor(lecturer_id, None, None)
  section.instructors.add(instructor)
  section.save()
  return section  

def get_reviews(courses, sections, year, semester, instructors, comments_map):
  fields = ('num_forms_returned', 'num_forms_produced', 'form_type', 'course_ID', 'year', 'semester', 'section_code', 'section_ID', 'lecturer_id')
  conditions = ('year="%s"' % year, 'semester="%s"' % semester)
  reviews_raw = select(fields, 'coursereview_tblsections', conditions)
  for forms_returned, forms_produced, form_type, course_ID, year, semester, \
    section_num, oldpcr_id, lecturer_id in reviews_raw:
    # if this instructor got deleted, its underlying review is pointless
    if lecturer_id in instructors:
      instructor = instructors[lecturer_id]
      try:
        comments = comments_map[courses[course_ID][year, semester], instructor]
      except KeyError:
        comments = None
      yield (get_or_create_review(sections[courses[course_ID][year, semester],  
             float(section_num)], forms_returned, forms_produced, form_type, instructor, comments), \
               oldpcr_id)
    else:
      print "Can't find instructor ID: %d for review %s" % (lecturer_id, section_num)

def import_reviews(courses, sections, year, semester, instructors, comments_map):
  '''Import the old pcr_id reviews into the Django database. Returns a dictionary containg all of the imported reviews keyed on oldpcr_id.'''
  review_map = {}
  for review in get_reviews(courses, sections, year, semester, instructors, comments_map):
    review_map[review[1]] = review[0]
  return review_map

def get_or_create_review(section, forms_returned, forms_produced, form_type, \
                         instructor, comments):
  review, _ = Review.objects.get_or_create(section = section,
                                           instructor = instructor,
                                           defaults = {
                                                       "forms_returned" : forms_returned,
                                                       "forms_produced" : forms_produced,
                                                       "form_type"      : form_type,
                                                       "comments"       : comments
                                                       }
  )
  return review

def import_review_bits(reviews, year, semester):
  fields = ('rInstructorQuality', 'rCourseQuality', 'rDifficulty', 'rCommAbility', 'rInstructorAccess', 'rReadingsValue', 'rAmountLearned', 'rWorkRequired', 'rRecommendMajor', 'rRecommendNonMajor', 'rArticulateGoals', 'rSkillEmphasis', 'rHomeworkValuable', 'rExamsConsistent', 'rAbilitiesChallenged', 'rClassPace', 'rStimulateInterest', 'rOralSkills', 'rInstructorConcern', 'rInstructorRapport', 'rInstructorAttitude', 'rInstructorEffective', 'rGradeFairness', 'rNativeAbility', 'rTAQuality', 'section_ID')
  conditions = ('year="%s"' % year, 'semester="%s"' % semester)
  review_bits_raw = select(fields, 'coursereview_tblsections', conditions) 
  review_bits = set([])
  for review_bit_raw in review_bits_raw:
    section_id = review_bit_raw[-1]
    review = reviews[section_id] if section_id in reviews else None
    if review:
      for field, score in izip(fields[:-1], review_bit_raw[:-1]):
        if score:
          get_or_create_review_bit(review, field, score)
    # Section does not exist because the corresponding instructor does not exist
    else:
      print "Missing review for section: %d" % (section_id,)

def get_or_create_review_bit(review, field, score):
  review_bit, _ = ReviewBit.objects.get_or_create( 
    review = review,
    field = field,
    score = score
  )
  review_bit.save()
  return review_bit

def import_semester_data():
  # sync departments (just in case)
  depts = sync_depts()
  # import instructors (just in case)
  print "Syncing instructors..."
  #lects = sync_instructors() TODO We'll get to this later
  try:
    i = open("instructors.p", "r")
    instructors = pickle.load(i)
    print "found pickle"
  except:
    instructors = import_instructors()
    i = open("instructors.p", "wb")
    pickle.dump(instructors, i)
    
  # import all the courses
  print "Importing courses..."
  try:
    f = open("courses.p", "r")
    print "found pickle"
    course_histories = pickle.load(f)
  except:
    print "no pickle found"
    course_histories = import_courses(depts)
    print "pickling"
    pickle.dump(course_histories, open("courses.p", "wb"))

  for year, semester in product(range(2002, 2012), ('a', 'b', 'c')): 
    # import all sections of all courses
    # import all reviews (based on sections)
    # import all review bits (based on reviews)
    print year, semester

    print "getting sections..."
    try:
      sections = pickle.load(open("sections%s%s.p" % (year, semester), "r"))
      print "pickle found..."
    except:
      print "no pickle found. importing..."
      sections = import_sections(course_histories, instructors, year, semester)
      pickle.dump(sections, open("sections%s%s.p" % (year, semester), "wb"))

    print "getting reviews..."
    try:
      reviews = pickle.load(open("reviews%s%s.p" % (year, semester), "r"))
      print "pickle found..."
    except:
      print "no pickle found. importing..."
      comments = get_comments(course_histories, instructors, year, semester)
      reviews = import_reviews(course_histories, sections, year, semester, instructors, comments)
      pickle.dump(reviews, open("reviews%s%s.p" % (year, semester), "wb"))
      del sections

    print "getting bits..."
    try:
      bits = pickle.load(open("bits%s%s.p" % (year, semester), "r"))
      print "pickle found..."
    except:
      print "no pickle found. importing..."
      bits = import_review_bits(reviews, year, semester)
      pickle.dump(bits, open("bits%s%s.p" % (year, semester), "wb"))

import sys
if __name__ == "__main__":
  import_semester_data()
#download_ldap_data()
