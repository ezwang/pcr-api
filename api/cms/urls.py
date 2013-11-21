from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',
    (r'^users/?$', users),  # POST
    (r'^users/(?P<userid>\d+)/?$', get_user),
    (r'^courses/(?P<courseid>\d+)/?$',courses),
    (r'^initial/?$', initial),
    (r'^_add_tag/?$', add_tags),
    (r'^_update_assigments/?$', update_assignments), #POST
    (r'^index.html', home),
    (r'^course.html', course),
    (r'^edit.html', edit),
    (r'^autoassign', autoassign),
)
