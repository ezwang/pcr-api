from django.conf.urls import url

# import each of the keys for the dispatch_root
from links import *
# import each of the handlers
from views import *
from dispatcher import cross_domain_ajax


def dispatch_404(message=None, perhaps=None):
    def view(request):
        raise API404(message)
    return view


urlpatterns = [
    # Index
    url(r"^$", index),

    # Instructors
    url(r"^instructors$", instructors),
    url(r"^instructors/(?P<instructor_id>[^/]+)$", instructor_main),
    url(r"^instructors/(?P<instructor_id>[^/]+)/sections$", instructor_sections),
    url(r"^instructors/(?P<instructor_id>[^/]+)/reviews$", instructor_reviews),

    # Course Histories
    url(r"^coursehistories$", course_histories),
    url(r"^coursehistories/(?P<histid>\d+)/?$", coursehistory_main, name="history"),
    url(r"^coursehistories/(?P<histid>\d+)/reviews$", coursehistory_reviews),
    url(r"^coursehistories/(?P<historyalias>[^/]+)(?P<path>.*)", alias_coursehistory),

    # Departments
    url(r"^depts$", depts),
    url(r"^depts/(?P<dept_code>[^/]+)$", dept_main),
    url(r"^depts/(?P<dept_code>[^/]+)/reviews$", dept_reviews),

    # Semesters
    url(r"^semesters$", semesters),
    url(r"^semesters/(?P<semester_code>[^/]+)$", semester_main),
    url(r"^semesters/(?P<semester_code>[^/]+)/(?P<dept_code>[^/]+)$", semester_dept),

    # Buildings
    url(r"^building$", buildings),
    url(r"^building/(?P<code>[^/]+)$", building_main),

    # Courses
    url(r"^courses$", dispatch_404("sorry, no global course list")),
    url(r"^courses/(?P<courseid>\d+)/?$", course_main, name="course"),
    url(r"^courses/(?P<courseid>\d+)/reviews$", course_reviews),
    url(r"^courses/(?P<courseid>\d+)/sections$", course_sections),
    url(r"^courses/(?P<courseid>\d+)/sections/(?P<sectionnum>[^/]+)/?$", section_main, name="section"),
    url(r"^courses/(?P<courseid>\d+)/sections/(?P<sectionnum>[^/]+)/reviews$", section_reviews),
    url(r"^courses/(?P<courseid>\d+)/sections/(?P<sectionnum>[^/]+)/reviews/(?P<instructor_id>[^/]+)$", review_main),
    url(r"^courses/(?P<coursealias>[^/]+)(?P<path>.*)$", alias_course),

    # Sections
    url(r"^sections$", dispatch_404("sorry, no global sections list")),
    url(r"^sections/(?P<sectionalias>[^/]+)$", alias_section),

    # Misc
    url(r"^(?P<alias>.*)$", alias_misc)
]


def handle_errors(func):
    def wrap(request, *args, **kwargs):
        try:
            if not request.consumer.access_pcr and "review" in request.path:
                raise API404("This API token does not have access to review data.")
            response = func(request, *args, **kwargs)
        except API404 as e:
            obj = {
                'help': "See %s for API documentation." % DOCS_HTML,
                'error': 'Error 404. The resource could not be found: ' + request.path
            }
            if e.perhaps:
                obj['perhaps_you_meant'] = e.perhaps  # and perhaps not
            if e.message:
                obj['message'] = e.message
            return JSON(obj, valid=False, httpstatus=404)
        return response
    return wrap


for pattern in urlpatterns:
    pattern.callback = handle_errors(cross_domain_ajax(pattern.callback))
