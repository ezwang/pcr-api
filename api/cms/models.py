from django.db import models
from django.contrib.auth.models import User


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
    ('ED', 'Editor'),
    ('EC', 'Editor-in-Chief'),
)


class Tag(models.Model):
    category = models.CharField(max_length=3, choices=TAGS)
    def __unicode__(self):
        return self.category

    class Meta:
        ordering = ('category',)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    user_type = models.CharField(max_length=3, choices=USER_TYPE)
    tags = models.ManyToManyField(Tag, blank=True, null=True)


class Course(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    professor = models.CharField(max_length=200)
    section = models.CharField(max_length=200)
    semester = models.DateField(auto_now_add=True)

    def toJSON(self):
        pass

    def __unicode__(self):
        return u'%s %s' % (self.name, self.professor)


class Summary(models.Model):
    course = models.ForeignKey(Course)
    status = models.CharField(max_length=1, choices=SUMMARY_STATUSES)
    text = models.TextField()

    def toJSON(self):
        pass

    def __unicode__(self):
        return u'%s' % (self.course.name)


class Review(models.Model):
    course = models.ForeignKey(Course)
    text = models.TextField()

    def toJSON(self):
        pass

    def __unicode__(self):
        return u'%s' % (self.course.name)
