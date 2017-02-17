from cms.models import *
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth.models import User
from cms.models import UserProfile, Tag
from django.core.context_processors import csrf
import json


# Create your views here.
def home(request):
    if request.method == 'GET':
        c = {}
        c.update(csrf(request))
        return render_to_response('cms/index.html', c, context_instance=RequestContext(request))


# TODO: not safe?
def users(request):
    """
    POST:
        creates the user and the tags it's passed, if they aren't already created
        ('WHA', 'Wharton'),
        ('SOC', 'Social Sciences'),
        ('MTS', 'Math/Science'),
        ('HUM', 'Humanities'),
        ('ENG', 'Engineering'),
        ('NUR', 'Nursing'),
        params:
            'email'
            'name'
            'specialty'
            'user_type': 3 character identifier as per model
    """
    if request.method == 'POST':
        params = json.loads(request.body)
        specialty = params['specialty']
        email = params['email']
        name = params['name']
        first_name, last_name = name.split()
        tag, created = Tag.objects.get_or_create(category=specialty.upper())
        user = User(first_name=first_name, last_name=last_name, username=name, email=email)
        user.save()
        profile = UserProfile(user=user, user_type=params['user_type'])
        profile.save()
        profile.tags = tag
        data = serializers.serialize('json', [profile])
        return HttpResponse(data)


# TODO: not safe?
def get_user(request, userid=0):
    """
    GET:
        params:
            TODO: @scwu

    """
    if request.method == 'GET':
        u = {}
        current_user = UserProfile.objects.get(id=userid)
        u['userid'] = current_user.id
        u['name'] = current_user.user.username
        u['email'] = current_user.user.email
        c = []
        courses = Course.objects.filter(user = current_user.user)
        for co in courses:
            #individual course dictionary
            summary = Summary.objects.get(course = co)
            #create a summary dictionary that will be an attribute of the course dict
            s = {'status': summary.status, 'text' : summary.text}
            i = {'summary': s, 'name' : co.name, 'department' : co.department,
                 'professor' : co.professor, 'section' : co.section, 'courseid' : co.id}
            c.append(i)
        u['courses'] = c
        data = json.dumps(u)
        return HttpResponse(data)


def courses(request, courseid):
    if request.method == 'GET':
        course = Course.objects.filter(id=courseid)
        data = serializers.serialize("json", course)
        return HttpResponse(data)


def initial(request):
    all_info = {}
    writers = []
    #gets all writers of type "writer"
    full_users = UserProfile.objects.all()
    for u in full_users:
        user_courses = Course.objects.filter(user=u).count()
        i = {'reviews': user_courses, 'id': u.id,'email' : u.user.email, 'name': u.user.first_name + " " + u.user.last_name}
        tags = u.tags
        #get all tags of user
        writers.append(i);
    all_info['users'] = writers
    courses = []
    #get all courses
    all_courses = Course.objects.all()
    for co in all_courses:
        user_id = co.user.id if co.user else None
        i = {'user' : user_id, 'department' : co.department,
             'professor' : co.professor, 'section' : co.section, 'courseid' : co.id}
        courses.append(i)
    all_info['courses'] = courses
    #put into json dump and return
    data = json.dumps(all_info)
    return HttpResponse(data)

def update_assignments(request):
    if request.method=='POST':
        params = json.loads(request.body)
        course_id = params['courseid']
        user_id = params['user']
        user = User.objects.get(id=user_id)
        if user:
            course = Course.objects.get(id=course_id)
            if course:
                course.user = user
                course.save()
                return HttpResponse('{"Response":"Success", "Results": "True"}')
            else:
                return HttpResponse('{"Response":"Failure", "Results": "No course found"}')
        else:
            return HttpResponse('{"Response":"Failure", "Results": "No user found"}')
    else:
        return HttpResponse('{"Response":"Failure", "Results": "Not an AJAX request"}')

def add_tags(request):
    if request.is_ajax():
        tag = request.POST['tag']
        user_id = request.POST['userid']
        user = UserProfile.objects.get(id=user_id)
        if user:
            if not user.tags.objects.filter(category = tag).exists():
                tag = Tag.objects.get(category = tag)
                user.tags.add(tag)
                user.save()
                return HttpResponse('{"Response":"Success", "Results": "True"}')

def add_summary(request):
    if request.is_ajax():
        summary = request.POST['summary']
        course_id = request.POST['course']
        status_change = request.POST['status']
        course_model = Course.objects.get(id=course_id)
        if (status=='I'):
            course_model.summary.text=summary
            course_model.summary.status='I'
            course_model.summary.save()
        elif (status=='S'):
            course_model.summary.text=summary
            course_model.summary.status='S'
            course_model.summary.save()
        course_model.save()
        return HttpResponse('{"Response":"Success"}')


def summary_status(request):
    if request.is_ajax():
        course_id = request.POST['course']
        status_change = request.POST['status']
        if (status=='P'):
            course_model = Course.objects.get(id=course_id)
            course_model.summary.status='I'
            course_model.summary.save()
            course_model.save()


def course(request):
    if request.method == 'GET':
        c = {}
        c.update(csrf(request))
        return render_to_response('cms/course.html', c, context_instance=RequestContext(request))


def edit(request):
    if request.method == 'GET':
        return render_to_response('cms/edit.html', {}, context_instance=RequestContext(request))


def autoassign(request):
    """
    simple inefficient alg:
    1. get list of departments
    2. get map of specialty to courses
    3. get map of specialty to users (# as well)
    4. calculate courses:user ratios
    5. starting with the specialty with the lowest course:user ratio:
        1. assign courses to users in that specialty until the average is reached.
            If the first department, just iterate over and spread to users. Update global average as the number assigned to each user.
        2. If average reached, then pool users and assign to all
        3. update global average,
    ** calculate and average the four ratios
    """
    if request.method == 'GET':
        # return render_to_response('cms/edit.html', {}, context_instance=RequestContext(request))
    # get all departments
    # departments = 1

    # grab all departments
        departments = Course.objects.values_list('department', flat=True).distinct()
        numbers = {}

        # set up a dict, department to number in each
        for dept in departments:
            numbers[dept] = len(Course.objects.filter(department=dept))

        sorted_list = sorted(numbers.items(), key=lambda x: x[1], reverse=True)

        # get users, order them by number assigned
        users = User.objects.all()
        courses = Course.objects.all()
        # for each course, assign it to a user in turn.

        index = 0;
        for course in courses:
            course.user = users[index]
            course.save()
            if index == len(users) - 1:
                index = 0
            else:
                index += 1
        return render_to_response('cms/edit.html', {}, context_instance=RequestContext(request))












