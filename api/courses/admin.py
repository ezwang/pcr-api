from courses.models import *
from django.contrib import admin

class InstructorAdmin(admin.ModelAdmin):
  search_fields = ['first_name', 'last_name']

admin.site.register(Instructor, InstructorAdmin)

for model in [Course, Section]:
  admin.site.register(model)
