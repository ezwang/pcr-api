import datetime
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from cms.models import *

from sandbox_config import SITE_NAME, URL_ROOT, TEST_EMAIL


QUESTIONS = [
    {
        'q': "Are all your groups University-recognized?",
        'ys': ['icf'],
        'ns': []
        },
]

COMMON_QS = [
    ("What are the goals and mission of your event and how do the "
     "relate to the missions of all groups involved?"),
    ("Describe in detail the nature of your event and the timeline for "
     "its completion."),
    ("Please list three past events held by the collaborating "
     "organizations and describe their outcomes."),
    ("How do you plan to publicize this event?"),
    ]

COMMON_FOLLOWUP_QS = [
    ("How did your event go?"),
    ("Why was it a success?")
    ]


REQUESTERS = [
    'philo',
    'testrequester1',
    'testrequester2',
    'testrequester3',
    ]

FUNDERS = [
    {
        'name': 'UA Contingency',
        'un': 'uacontingency',
        'desc': ('Fund events that need funding and have exhausted their other '
               'alternatives.'),
        'qs': [],
        'fqs': []
        }
    ]

SUMMARIES = [
    {'course': '',
     'status': '',
     'text': ''
    },
    {'course': '',
     'status': '',
     'text': ''
    }
]

COURSES = [
    {'user': '',
     'name': '',
     'department': '',
     'professor': '',
     'section': ''
    },
    {'course': '',
     'status': '',
     'text': ''
    }
]

def add_user(name, email):
    user = User.objects.create_user(
    username=name
    password=name,
    email=email)

def add_summary(course, status, text):
    # new model object


def add_course(user, name, department, professor, section):

def add_review(course, text):

def populate():
    for summary in SUMMARIES:
        add_summary(**summary)


def add_funder(name, un, desc, qs, fqs):
    """Add a funder and their attendant questions."""
    # User and CFAUser
    user = User.objects.create_user(
        username=un,
        password=un,
        email=TEST_EMAIL)
    user.first_name = name[:30]
    profile = user.get_profile()
    profile.user_type = 'F'
    profile.mission_statement = desc
    profile.osa_email = TEST_EMAIL
    profile.save()

    # Questions
    for q in qs:
        FreeResponseQuestion.objects.create(funder=profile, question=q)

    for fq in fqs:
        FollowupQuestion.objects.create(funder=profile, question=fq)


def add_requester(un):
    """Import a dummy requester."""
    User.objects.create_user(username=un, email=TEST_EMAIL, password=un)


def import_users():
    """Import all the funders described above."""
    CFAUser.objects.all().delete()
    User.objects.filter(is_staff=False).delete()
    FreeResponseQuestion.objects.all().delete()

    # Import funders
    for funder in FUNDERS:
        add_funder(**funder)

    # Import requesters
    for requester in REQUESTERS:
        add_requester(requester)


def import_questions():
    """Import the common and eligibility questions. Should be run after
    import_funders."""
    EligibilityQuestion.objects.all().delete()
    FunderConstraint.objects.all().delete()
    for question in QUESTIONS:
        q = EligibilityQuestion.objects.create(question=question['q'])
        for y in question['ys']:
            FunderConstraint.objects.create(
                funder=User.objects.get(username=y).cfauser,
                question=q, answer='Y')
        for n in question['ns']:
            FunderConstraint.objects.create(
                funder=User.objects.get(username=n).cfauser,
                question=q, answer='N')

    CommonFreeResponseQuestion.objects.all().delete()
    for common_q in COMMON_QS:
        CommonFreeResponseQuestion.objects.create(question=common_q)
    for common_followup_q in COMMON_FOLLOWUP_QS:
        CommonFollowupQuestion.objects.create(question=common_followup_q)
        

def import_sites():
  site = Site.objects.get_current()
  site.domain = SITE_NAME + URL_ROOT
  site.name = "The Common Funding App"
  site.save()


def import_all():
    import_users()
    import_questions()
    import_sites()
    return 0

if __name__ == '__main__':
    sys.exit(import_all())