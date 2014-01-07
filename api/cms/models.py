from django.db import models
from django.contrib.auth.models import User
from django.core import serializers


# Create your models here.

SUMMARY_STATUSES = (
    ('N', 'Not started'),
    ('I', 'In progress'),
    ('S', 'Submitted'),
    ('P', 'Published')
)

TAGS = (
    ('WHA', 'Wharton'),
    ('SOC', 'Social Sciences'),
    ('MTS', 'Math/Science'),
    ('HUM', 'Humanities'),
    ('ENG', 'Engineering'),
    ('NUR', 'Nursing'),
)

USER_TYPE = (
    ('WR', 'Writer'),
# broken up into section
# each section has writers, 2 section editors.
# writer hits post -> goes to editor
    ('ED', 'Editor'),
# editor hits post -> editor in chief
    ('EC', 'Editor-in-Chief'),
# eic hits post to go live
)


# threshold for showing the courses with certain number of reviews.


class Tag(models.Model):
    """ Specializations for the editors.
        Each editor can have multiple Specializations """
    category = models.CharField(max_length=3, choices=TAGS)

    def __unicode__(self):
        return self.category

    class Meta:
        ordering = ('category',)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    user_type = models.CharField(max_length=3, choices=USER_TYPE)
    # tags = models.ManyToManyField(Tag, blank=True, null=True)
    # tags = models.ForeignKey(Tag, blank=True, null=True)
    tags = models.ForeignKey(Tag, blank=True, null=True)


class Summary(models.Model):
    """
        The summary that the summarizers create - contains information
        on it's current review status (by the editors)
    """
    status = models.CharField(max_length=1, choices=SUMMARY_STATUSES)
    text = models.TextField()

    def toJSON(self):
        pass

    def __unicode__(self):
        return u'%s' % (self.course.name)

class Course(models.Model):
    """ Course Section (2012F, 2012S...).
        Every "instance" of a course that can be reviewed
        Contains metadata taken from xml, as well as the current date
    """
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    professor = models.CharField(max_length=200)
    section = models.CharField(max_length=200)
    semester = models.DateField(auto_now_add=True)
    term = models.CharField(max_length=20)
    # summary = models.ForeignKey(Summary, null=True, blank=True)

    def toJSON(self):
        pass

    def __unicode__(self):
        return u'%s %s' % (self.name, self.professor)

class Review(models.Model):
    """ The review text for a given course by a student """
    course = models.ForeignKey(Course)
    text = models.TextField()

    def toJSON(self):
        pass

    def __unicode__(self):
        return u'%s' % (self.course.name)
