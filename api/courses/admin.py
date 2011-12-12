from courses.models import *
from django.contrib import admin
from buttonable_model_admin import *


class CourseAdmin(ButtonableModelAdmin):
  def generate_cache(self, what_is_this_other_arg):
    pass

  generate_cache.short_description = 'Generate Cache'

  buttons = [generate_cache]


class InstructorAdmin(admin.ModelAdmin):
  search_fields = ['first_name', 'last_name']


admin.site.register(Instructor, InstructorAdmin)
admin.site.register(Course, CourseAdmin)

for model in [Section]:
  admin.site.register(model)
