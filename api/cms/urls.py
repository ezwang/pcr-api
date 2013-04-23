from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',
    (r'^users/(?P<userid>\d+)/?$', users),
    (r'^initial/?$', initial),
    (r'^_add_tag/?$', add_tags),
    (r'^_update_assigments/?$', update_assignments),
    (r'^index.html', home),
    (r'^course.html', course),
    (r'^edit.html', edit),
)
