from django.contrib import admin
from django.http import HttpResponse
from django.conf.urls.defaults import patterns


from courses.models import *


class InstructorAdmin(admin.ModelAdmin):
  search_fields = ['first_name', 'last_name']

admin.site.register(Instructor, InstructorAdmin)


class CourseAdmin(admin.ModelAdmin):
  def get_urls(self):
    urls = super(CourseAdmin, self).get_urls()
    my_urls = patterns('',
      (r'^generate_cache/$', lambda(request): HttpResponse("you clicked generate cache")),
      (r'^push_to_live/$', lambda(request): HttpResponse("you clicked push to live"))
    )
    return my_urls + urls

admin.site.register(Course,CourseAdmin)

for model in [Section]:
  admin.site.register(model)

"""
grab 'patterns' from django.conf.urls.defaults
 and either add the pattern to some Admin's get_urls(self) 
 a la the end of http://djangosnippets.org/snippets/1936/

 Make it fire towards some custom python script that Matt has.

 As a result, hitting either of the 'generate cache' / 'push live' buttons
 will be forwarded to matt's scripts here.

"""
