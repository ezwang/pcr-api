from django.template import RequestContext
from django.shortcuts import redirect, render_to_response

from json_helpers import JSON

# Create your views here.
def home(request):
    if request.method == 'GET':
        return render_to_response('cms/index.html', {}, context_instance=RequestContext(request))


def users(request):
  return 'placeholder'
  #return JSON(something)

#def courses(request):

def course(request): 
    if request.method == 'GET':
	return render_to_response('cms/course.html', {}, context_instance=RequestContext(request))

