from django.conf.urls import url

# import each of the keys for the dispatch_root
from links import *
# import each of the handlers
from views import *
from dispatcher import cross_domain_ajax


urlpatterns = [
    url(r"^instructors$", instructors)
]


def dispatch_404(message=None, perhaps=None):
    def view(request, path, _):
        raise API404(message)
    return view


def dispatcher(dispatchers):
    d_str = dispatchers.get("/str")
    d_int = dispatchers.get("/int")

    def dispatch_func(request, path, variables=[]):
        if not path:
            return dispatchers[''](request, [], variables)
        first, rest = path[0], path[1:]
        if first in dispatchers:
            return dispatchers[first](request, rest, variables)
        elif d_int and first.isdigit():
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


def _annotate_dictionary(d, fn):
    if type(d) == dict:
        return fn(dict((k, _annotate_dictionary(v, fn)) for k, v in d.iteritems()))
    else:
        return d


dispatch_root = _annotate_dictionary(dispatch_root, dispatcher)


@cross_domain_ajax
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
            obj['perhaps_you_meant'] = e.perhaps  # and perhaps not
        if e.message:
            obj['message'] = e.message
        return JSON(obj, valid=False, httpstatus=404)
