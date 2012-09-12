

#tokens for paths and dispatcher

# List of keywords for each of the API end points.
# the API. That is, if a user wants to get a list of Departments, they should
# go to "/depts"
# Our convention is to use plural names for everything.

DEPARTMENT_TOKEN = 'depts'
INSTRUCTOR_TOKEN = 'instructors'
COURSEHISTORY_TOKEN = 'coursehistories'
COURSE_TOKEN = 'courses'
SECTION_TOKEN = 'sections'
REVIEW_TOKEN = 'reviews'
# TODO: This breaks convention??
BUILDING_TOKEN = 'building'
SEMESTER_TOKEN = 'semesters'

#TODO: do we want JSON keys to be here or elsewhere?
# This is the wrapper keyword for whatever is returned from the API.
# That is, if one accesses "/depts", one should get:
#   {
#       'values': [Dept1, Dept2, ...]
#   }
RSRCS = 'values'


# List of absolute urls of each model.
# These are factored out because they are convenient for redirects inside
# the views.


def coursehistory_url(uid):
    return '/%s/%d' % (COURSEHISTORY_TOKEN, uid)


def semester_url(code):
    return '/%s/%s' % (SEMESTER_TOKEN, code.lower())


def course_url(uid):
    return '/%s/%d' % (COURSE_TOKEN, uid)


def section_url(course_uid, sectionnum):
    return '/%s/%d/%s/%03d' % (COURSE_TOKEN, course_uid,
                               SECTION_TOKEN, sectionnum)


def instructor_url(pennkey):
    return '/%s/%s' % (INSTRUCTOR_TOKEN, pennkey)


def building_url(code):
    return '/%s/%s' % (BUILDING_TOKEN, code.lower()),


def department_url(code):
    return '/%s/%s' % (DEPARTMENT_TOKEN, code.lower())


def semdept_url(semcode, deptcode):
    return '/%s/%s/%s' % (SEMESTER_TOKEN, semcode.lower(), deptcode.lower())


def review_url(course_uid, sectionnum, pennkey):
    # leading / comes from section_url
    return "%s/%s/%s" % (section_url(course_uid, sectionnum),
                         REVIEW_TOKEN,
                         pennkey)
