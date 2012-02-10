"""
Test for the API views.
"""
import json

from django.test import TestCase
from django.test.client import Client

from api.apiconsumer.models import APIConsumer

import models


class DataTest(TestCase):
  def setUp(self):
    self.consumer = APIConsumer.objects.create(
        name="test",
        email="test@test.com",
        description="",
        token="root",
        permission_level=9001
        )
    self.client = Client()

    cis = models.Department.objects.create(
        code='CIS', name='Computer Science')
    ese = models.Department.objects.create(
        code='ESE', name='Electrical Engineering')
    cis110 = models.CourseHistory.objects.create(notes="None.")
    cis110_1 = models.Course.objects.create(
        semester = 810,
        name = "CIS 110",
        credits = 1.0,
        description = "intro to CS.",
        history = cis110
        )
    instructor1 = models.Instructor.objects.create(
        first_name="John", last_name="Doe")
    section1 = models.Section.objects.create(
        course=cis110_1, name="Intro to CS", 
        sectionnum='001', sectiontype='LEC')
    alias1 = models.Alias.objects.create(
        course=cis110_1, department=cis, coursenum=1, semester='810')
    alias2 = models.Alias.objects.create(
        course=cis110_1, department=ese, coursenum=1, semester='810')
    review1 = models.Review.objects.create(
        section=section1, instructor=instructor1,
        forms_returned=10, forms_produced=20, form_type=1,
        comments="Students enjoyed the course.")
    reviewbit1 = models.ReviewBit.objects.create(
        review=review1, field="Instructor Quality", score=3.0)
    reviewbit2 = models.ReviewBit.objects.create(
        review=review1, field="Difficulty", score=1.0)
    reviewbit3 = models.ReviewBit.objects.create(
        review=review1, field="Course Quality", score=2.0)

  def get_result(self, path):
    """Load a page on the API and return the result.
    
    Fails on inability to parse json or invalid content.
    """
    response = self.client.get(path, {'token': self.consumer.token})
    try:
      content = json.loads(response.content)
    except ValueError as e:
      self.fail("%s (s=\"%s\")" % (e, response.content))
    self.assertTrue(content['valid'], content)
    return content['result']

  def validate_results(self, path):
    result = self.get_result(path)
    self.assertTrue(len(result['values']) > 0, result)

  def test_presence_of_depts(self):
    self.validate_results('/depts')

  def test_dept_should_have(self):
    result = self.get_result('/depts/CIS')
    self.assertTrue("coursehistories" in result)
    self.assertTrue("id" in result)
    self.assertTrue("name" in result)
    self.assertTrue("path" in result)
    self.assertTrue("reviews" in result)
  
  def test_coursehistory_should_have(self):
    result = self.get_result('/coursehistories/1')
    self.assertTrue("aliases" in result)
    self.assertTrue("courses" in result)
    self.assertTrue("id" in result)
    self.assertTrue("name" in result)
    self.assertTrue("path" in result)
    self.assertTrue("reviews" in result)

  def test_presence_of_instructors(self):
    self.validate_results('/instructors')

  def test_instructor_should_have(self):
    instructor = models.Instructor.objects.all()[0]
    result = self.get_result(instructor.get_absolute_url())
    self.assertTrue("id" in result)
    self.assertTrue("name" in result)
    self.assertTrue("path" in result)
    self.assertTrue("reviews" in result)

  def test_course_should_have(self):
    result = self.get_result('/courses/1')
    self.assertTrue("aliases" in result)
    self.assertTrue("coursehistories" in result)
    self.assertTrue("credits" in result)
    self.assertTrue("description" in result)
    self.assertTrue("id" in result)
    self.assertTrue("name" in result)
    self.assertTrue("path" in result)
    self.assertTrue("reviews" in result)
    self.assertTrue("sections" in result)
    self.assertTrue("semester" in result)

  def test_presence_of_course_reviews(self):
    self.validate_results('/courses/1/reviews')

  def test_presence_of_sections(self):
    self.validate_results('/courses/1/sections')

  def test_section_should_have(self):
    result = self.get_result('/courses/1/sections/001/')
    self.assertTrue("aliases" in result)
    self.assertTrue("courses" in result)
    self.assertTrue("group" in result)
    self.assertTrue("id" in result)
    self.assertTrue("instructors" in result)
    self.assertTrue("meetingtimes" in result)
    self.assertTrue("name" in result)
    self.assertTrue("path" in result)
    self.assertTrue("reviews" in result)
    self.assertTrue("sectionnum" in result)

  def test_presence_of_section_reviews(self):
    self.validate_results('/courses/1/sections/001/reviews')

  def test_review_should_have(self):
    result = self.get_result('/courses/1/sections/001/reviews')
    review = result['values'][0]

    self.assertTrue("comments" in review)
    self.assertTrue("id" in review)
    self.assertTrue("instructor" in review)
    self.assertTrue("num_reviewers" in review)
    self.assertTrue("num_students" in review)
    self.assertTrue("path" in review)
    self.assertTrue("ratings" in review)
    self.assertTrue("section" in review)

    comments = review['comments']
    instructor = review['instructor']
    ratings = review['ratings']
    num_reviewers = review['num_reviewers']
    num_students = review['num_students']
    section = review['section']

    self.assertTrue(comments != "null", msg=comments)
    self.assertTrue(len(comments) > 0, msg=comments)
    self.assertTrue(instructor['name'] == "John Doe", msg=instructor)
    self.assertTrue(len(ratings) > 0, msg=result)
    self.assertTrue(int(num_reviewers) > 0)
    self.assertTrue(int(num_students) > 0)
    self.assertTrue(section['sectionnum'] == '001')
