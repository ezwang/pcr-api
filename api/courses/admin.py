from django.contrib import admin
from django.http import HttpResponse
from django.conf.urls.defaults import patterns
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group

from courses.models import Instructor, Course, Section, Review


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Site)


class InstructorAdmin(admin.ModelAdmin):
  search_fields = ['first_name', 'last_name']


class CourseAdmin(admin.ModelAdmin):
  def get_urls(self):
    urls = super(CourseAdmin, self).get_urls()
    my_urls = patterns('',
      (r'^generate_cache/$', lambda(request): HttpResponse("you clicked generate cache")),
      (r'^push_to_live/$', lambda(request): HttpResponse("you clicked push to live"))
    )
    return my_urls + urls


admin.site.register(Instructor, InstructorAdmin)
admin.site.register(Course,CourseAdmin)
admin.site.register(Section)
admin.site.register(Review)

"""
grab 'patterns' from django.conf.urls.defaults
 and either add the pattern to some Admin's get_urls(self) 
 a la the end of http://djangosnippets.org/snippets/1936/

 Make it fire towards some custom python script that Matt has.

 As a result, hitting either of the 'generate cache' / 'push live' buttons
 will be forwarded to matt's scripts here.

"""
