#tokens for paths and dispatcher - everything is plural now
DEPARTMENT_TOKEN = 'depts'
INSTRUCTOR_TOKEN = 'instructors'
COURSEHISTORY_TOKEN = 'coursehistories'
COURSE_TOKEN = 'courses'
SECTION_TOKEN = 'sections'
REVIEW_TOKEN = 'reviews'
BUILDING_TOKEN = 'building'
SEMESTER_TOKEN = 'semesters'

def coursehistory_url(uid):
    return '/%s/%d' % (COURSEHISTORY_TOKEN, uid)

def semester_url(code):
    return '/%s/%s' % (SEMESTER_TOKEN, code)

def course_url(uid):
    return '/%s/%d' % (COURSE_TOKEN, uid)

def coursehistory_url(uid):
    return '/%s/%d' % (COURSEHISTORY_TOKEN, uid)

def section_url(course_uid, sectionnum):
    return '/%s/%d/%s/%03d' % (COURSE_TOKEN, course_uid,
                               SECTION_TOKEN, sectionnum)

def instructor_url(pennkey):
    return '/%s/%s' % (INSTRUCTOR_TOKEN, pennkey)

def building_url(code):
    return '/%s/%s' % (BUILDING_TOKEN, code),

def department_url(code):
    return '/%s/%s' % (DEPARTMENT_TOKEN, code)

def semdept_url(semcode, deptcode):
    return '/%s/%s/%s' % (SEMESTER_TOKEN, self.semester, self.code)

def review_url(course_uid, sectionnum, pennkey):
    return "%s/%s/%s" % (section_url(course_uid, sectionnum),
                         REVIEW_TOKEN,
                         pennkey)
