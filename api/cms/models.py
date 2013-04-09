from django.db import models
from django.contrib.auth.models import User

# Create your models here.

SUMMARY_STATUSES = (
  (0, 'Not started'),
  (1, 'In progress'),
  (2, 'Submitted'),
  (3, 'Published')
)

class Summary(models.Model):
  course = models.ForeignKey(Course)
  status = models.CharField(max_length=1, choices=SUMMARY_STATUSES)
  text = models.TextField()

  def toJSON(self):
    pass
  def __unicode__(self):
    pass

class Course(models.Model):
  user = models.ForeignKey(User, null=True)
  name = models.CharField(max_length=200)
  department = models.CharField(max_length=200)
  professor = models.CharField(max_length=200)
  section = models.IntegerField()

  def toJSON(self):
    pass
  def __unicode__(self):
    pass

class Review(models.Model):
  course = models.ForeignKey(Course)
  text = models.TextField()

  def toJSON(self):
    pass
  def __unicode__(self):
    pass