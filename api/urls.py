"""Root PCR project URLs"""
from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin
from tastypie.api import Api

from courses.api import CourseResource


admin.autodiscover()

v2_api = Api(api_name='v2')
v2_api.register(CourseResource())

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^pcrsite-static/(?P<page>.*)$', 'static_content.views.serve_page'),
    (r'api/', include(v2_api.urls)),
    (r'^v1/(?P<url>.*)', 'courses.urls.dispatch'),
)
