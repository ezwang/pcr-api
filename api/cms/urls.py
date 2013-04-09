from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',
    (r'^index.html', home),
    (r'^course.html', course),
    (r'^edit.html', edit),
)
