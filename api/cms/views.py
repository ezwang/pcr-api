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


def users(request, userid):
    if request.method == 'GET':
        u = {}
        current_user = UserProfile.objects.get(id=userid)
        u['userid'] = current_user.id
        u['name'] = current_user.user.first_name + " " + current_user.user.last_name
        u['email'] = current_user.user.email
        c = []
        courses = Course.objects.filter(user = current_user.user)
        for co in courses:
            #individual course dictionary
            summary = Summary.objects.get(course = co)
            #create a summary dictionary that will be an attribute of the course dict
            s = {'status': summary.status, 'text' : summary.text}
            i = {'summary': s, 'name' : co.name, 'department' : co.department,
                 'professor' : co.professor, 'section' : co.section}
            c.append(i)
        u['courses'] = c
        data = json.dumps(u)
        return HttpResponse(data)
    # writers = []
    # full_users = UserProfile.objects.filter(user_type='WR')
    # for u in full_users:
    #     i = {'email' : u.user.email, 'userid' : u.id, 'name': u.user.first_name + u.user.last_name}
    #     tags = u.tags.all()
    #     tag_list= [t.category for t in tags]
    #     i['tags'] = tag_list
    #     writers.append(i)
    # if request.method == 'GET':
    #     data  = json.dumps(writers)
    #     return HttpResponse(data)
    # else:
    #     return render_to_response('cms/users.html', {writers : writers}, context_instance = RequestContext(request))


def course(request):
    if request.method == 'GET':
        return render_to_response('cms/course.html', {}, context_instance=RequestContext(request))


def edit(request):
    if request.method == 'GET':
        return render_to_response('cms/edit.html', {}, context_instance=RequestContext(request))
