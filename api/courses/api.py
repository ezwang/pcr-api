"""TastyPie API definitions"""
from tastypie.resources import ModelResource

from models import *


class CourseResource(ModelResource):
  class Meta:
    queryset = Course.objects.all()
    resource_name = 'course'
