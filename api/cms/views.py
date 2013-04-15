from cms.models import *
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from django.core import serializers
from django.http import HttpResponse
import json

# Create your views here.
def home(request):
    if request.method == 'GET':
        return render_to_response('cms/index.html', {}, context_instance=RequestContext(request))


def users(request):
    writers = []
    full_users = UserProfile.objects.filter(user_type='WR')
    for u in full_users:
        i = {'email' : u.email, 'name': u.first_name + u.last_name}
        tags = u.get_profile().tags.all()
        tag_list= [t.category for t in tags]
        i['tags'] = tag_list
        writers.append(i)
    data  = json.dumps(writers)
    return HttpResponse(data)


def course(request):
    if request.method == 'GET':
        return render_to_response('cms/course.html', {}, context_instance=RequestContext(request))


def edit(request):
    if request.method == 'GET':
        return render_to_response('cms/edit.html', {}, context_instance=RequestContext(request))
