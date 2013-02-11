from django.template import RequestContext
from django.shortcuts import redirect, render_to_response


# Create your views here.
def home(request):
    if request.method == 'GET':
        return render_to_response('cms/index.html', {}, context_instance=RequestContext(request))

def course(request): 
    if request.method == 'GET':
	return render_to_response('cms/course.html', {}, context_instance=RequestContext(request))

